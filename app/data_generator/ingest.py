import asyncio
import logging

from sqlalchemy import text

from app.config import settings
from app.data_generator import generators
from app.db.postgres import engine
from app.models.dw_tables import Base

logger = logging.getLogger(__name__)


async def run_data_generation(
    n_users: int = 10000,
    n_products: int = 20000,
    n_orders: int = 100000,
    n_reviews: int = 50000,
) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DDL executed — all tables created")

    users = generators.generate_users(n_users)
    products = generators.generate_products(n_products)
    orders = generators.generate_orders(products, users, n_orders)
    returns_data = generators.generate_returns(orders)
    reviews = generators.generate_reviews(products, users, n_reviews)
    inventory = generators.generate_inventory(products)

    async with engine.begin() as conn:
        # users
        await conn.execute(
            text("""
                INSERT INTO users (user_id, name, region, segment, created_at)
                VALUES (:user_id, :name, :region, :segment, :created_at)
            """),
            users,
        )
        logger.info(f"Inserted {len(users)} users")

        # products
        await conn.execute(
            text("""
                INSERT INTO products (sku, title, brand, category, price, specs, created_at)
                VALUES (:sku, :title, :brand, :category, :price, :specs, :created_at)
            """),
            products,
        )
        logger.info(f"Inserted {len(products)} products")

        # orders — capture generated IDs for returns FK
        order_rows = []
        for o in orders:
            result = await conn.execute(
                text("""
                    INSERT INTO orders (sku, user_id, order_date, quantity, amount, status)
                    VALUES (:sku, :user_id, :order_date, :quantity, :amount, :status)
                    RETURNING order_id
                """),
                o,
            )
            order_rows.append(result.scalar_one())
        logger.info(f"Inserted {len(order_rows)} orders")

        # returns — link to order IDs
        returned_order_ids = [
            order_id
            for order, order_id in zip(orders, order_rows)
            if order["status"] == "returned"
        ]
        for ret, order_id in zip(returns_data, returned_order_ids):
            ret["order_id"] = order_id
        await conn.execute(
            text("""
                INSERT INTO returns (sku, order_id, return_date, reason, refund_amount)
                VALUES (:sku, :order_id, :return_date, :reason, :refund_amount)
            """),
            returns_data,
        )
        logger.info(f"Inserted {len(returns_data)} returns")

        # reviews
        await conn.execute(
            text("""
                INSERT INTO reviews (sku, user_id, rating, review_text, review_date)
                VALUES (:sku, :user_id, :rating, :review_text, :review_date)
            """),
            reviews,
        )
        logger.info(f"Inserted {len(reviews)} reviews")

        # inventory
        await conn.execute(
            text("""
                INSERT INTO inventory (sku, stock_qty, warehouse, updated_at)
                VALUES (:sku, :stock_qty, :warehouse, :updated_at)
                ON CONFLICT (sku) DO UPDATE SET stock_qty = EXCLUDED.stock_qty, updated_at = EXCLUDED.updated_at
            """),
            inventory,
        )
        logger.info(f"Inserted {len(inventory)} inventory records")

    logger.info("Data generation complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    asyncio.run(run_data_generation())
