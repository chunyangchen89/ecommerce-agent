import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker("zh_CN")

CATEGORIES = ["手机", "笔记本", "耳机", "平板", "智能手表", "相机", "键盘", "显示器"]
BRANDS = ["Apple", "Samsung", "Sony", "Huawei", "Xiaomi", "Lenovo", "Dell", "Logitech"]
REGIONS = ["北京", "上海", "广州", "深圳", "成都", "杭州"]
SEGMENTS = ["premium", "standard", "budget"]
WAREHOUSES = ["BJ", "SH", "GZ", "CD"]

RETURN_REASONS = [
    "质量问题", "尺寸不符", "与描述不符", "商品损坏", "不想要了",
    "物流太慢", "颜色差异大", "性能不达预期", "包装破损", "买错了",
]

PRODUCT_TEMPLATES = [
    {"desc": "旗舰智能手机，搭载最新芯片，拍照效果卓越", "specs": "骁龙8 Gen4, 12GB RAM, 256GB, 6.7寸 AMOLED"},
    {"desc": "轻薄商务笔记本，长续航高性能", "specs": "i7-14700H, 16GB, 512GB SSD, 14寸 2.8K"},
    {"desc": "主动降噪无线耳机，沉浸式音质体验", "specs": "蓝牙5.3, ANC降噪, 30小时续航, Hi-Res认证"},
    {"desc": "高性能平板电脑，创作娱乐两不误", "specs": "M4芯片, 8GB, 256GB, 11寸 Liquid Retina"},
    {"desc": "运动健康智能手表，全天候监测", "specs": "心率/血氧/GPS, 5ATM防水, 14天续航"},
    {"desc": "全画幅微单相机，专业影像创作", "specs": "6100万像素, 4K120p, 五轴防抖, 双卡槽"},
    {"desc": "机械键盘，Cherry轴体，RGB背光", "specs": "Cherry MX Red, 全键无冲, PBT键帽, Type-C"},
    {"desc": "专业设计显示器，色彩精准", "specs": "27寸 4K, 99% DCI-P3, Delta E<2, HDR600"},
]

REVIEW_TEMPLATES = {
    "high": [
        "质量非常好，物超所值，强烈推荐",
        "使用体验超出预期，做工精细，性能强劲",
        "包装用心，物流快，到手非常满意，会回购",
        "手感舒适，操作流畅，同价位最佳选择",
        "屏幕显示效果惊艳，音质也很出色",
    ],
    "medium": [
        "整体还行，对得起这个价格，部分功能有待优化",
        "性价比可以，但做工细节还有提升空间",
        "基本功能正常使用，没有太大惊喜也没有明显槽点",
        "发货速度一般，产品中规中矩，用着还行",
    ],
    "low": [
        "使用一周后出现卡顿，体验不如预期",
        "做工粗糙，有明显的接缝不齐，质感廉价",
        "电池续航虚标严重，实际使用只有标称的一半",
        "客服响应慢，退换货流程复杂，售后体验差",
        "与商品描述不符，色差大，感觉被骗了",
    ],
}

RATING_WEIGHTS = [
    (5, 0.35, "high"),
    (4, 0.25, "high"),
    (3, 0.20, "medium"),
    (2, 0.12, "medium"),
    (1, 0.05, "low"),
    (0, 0.03, "low"),
]


def generate_users(n: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    users = []
    for i in range(n):
        uid = f"U{str(i + 1).zfill(8)}"
        users.append({
            "user_id": uid,
            "name": fake.name(),
            "region": rng.choice(REGIONS),
            "segment": rng.choice(SEGMENTS),
            "created_at": fake.date_time_between(start_date="-2y", end_date="-30d"),
        })
    return users


def generate_products(n: int, seed: int = 43) -> list[dict]:
    rng = random.Random(seed)
    products = []
    for i in range(n):
        cat_idx = i % len(CATEGORIES)
        tmpl = PRODUCT_TEMPLATES[cat_idx]
        brand = BRANDS[i % len(BRANDS)]
        cat = CATEGORIES[cat_idx]
        series = i // len(CATEGORIES) + 1
        sku = f"SKU{str(i + 1).zfill(8)}"
        price = round(rng.uniform(99.0, 9999.0), 2)
        products.append({
            "sku": sku,
            "title": f"{brand} {cat} 系列{series}",
            "brand": brand,
            "category": cat,
            "price": price,
            "specs": tmpl["specs"],
            "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
        })
    return products


def generate_orders(products: list[dict], users: list[dict], n: int, seed: int = 44) -> list[dict]:
    rng = random.Random(seed)
    skus = [p["sku"] for p in products]
    sku_price = {p["sku"]: float(p["price"]) for p in products}
    uids = [u["user_id"] for u in users]
    orders = []
    for _ in range(n):
        sku = rng.choice(skus)
        uid = rng.choice(uids)
        qty = rng.randint(1, 5)
        amount = round(qty * sku_price[sku] * rng.uniform(0.9, 1.1), 2)
        status = rng.choices(
            ["completed", "cancelled", "returned"],
            weights=[0.80, 0.05, 0.15],
        )[0]
        orders.append({
            "sku": sku,
            "user_id": uid,
            "order_date": fake.date_time_between(start_date="-365d", end_date="now"),
            "quantity": qty,
            "amount": amount,
            "status": status,
        })
    return orders


def generate_returns(orders: list[dict], seed: int = 45) -> list[dict]:
    rng = random.Random(seed)
    returns = []
    for order in orders:
        if order["status"] != "returned":
            continue
        order_date = order["order_date"]
        if isinstance(order_date, str):
            order_date = datetime.fromisoformat(order_date)
        return_date = order_date + timedelta(days=rng.randint(1, 14))
        refund = round(float(order["amount"]) * rng.uniform(0.7, 1.0), 2)
        returns.append({
            "sku": order["sku"],
            "order_id": None,  # filled during ingest after insert
            "return_date": return_date,
            "reason": rng.choice(RETURN_REASONS),
            "refund_amount": refund,
            "_order_idx": len(returns),  # track original order for FK linking
        })
    return returns


def generate_reviews(products: list[dict], users: list[dict], n: int, seed: int = 46) -> list[dict]:
    rng = random.Random(seed)
    skus = [p["sku"] for p in products]
    uids = [u["user_id"] for u in users]
    reviews = []
    for _ in range(n):
        sku = rng.choice(skus)
        uid = rng.choice(uids)
        roll = rng.random()
        cumulative = 0.0
        for rating, weight, tier in RATING_WEIGHTS:
            cumulative += weight
            if roll <= cumulative:
                review_text = rng.choice(REVIEW_TEMPLATES[tier])
                break
        else:
            rating, review_text = 4, rng.choice(REVIEW_TEMPLATES["high"])
        reviews.append({
            "sku": sku,
            "user_id": uid,
            "rating": rating,
            "review_text": review_text,
            "review_date": fake.date_time_between(start_date="-365d", end_date="now"),
        })
    return reviews


def generate_inventory(products: list[dict], seed: int = 47) -> list[dict]:
    rng = random.Random(seed)
    inventory = []
    for p in products:
        inventory.append({
            "sku": p["sku"],
            "stock_qty": rng.randint(0, 5000),
            "warehouse": rng.choice(WAREHOUSES),
            "updated_at": datetime.now(),
        })
    return inventory
