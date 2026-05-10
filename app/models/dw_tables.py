
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    user_id = Column(String(32), primary_key=True, comment="用户ID")
    name = Column(String(64), nullable=False, comment="用户姓名")
    region = Column(String(32), nullable=False, comment="地区：北京/上海/广州/深圳/成都/杭州")
    segment = Column(String(16), nullable=False, comment="用户分层：premium/standard/budget")
    created_at = Column(DateTime, nullable=False, comment="注册时间")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"comment": "商品主表，包含商品标题、品牌、类目、价格、参数"}

    sku = Column(String(32), primary_key=True, comment="商品SKU")
    title = Column(String(256), nullable=False, comment="商品标题")
    brand = Column(String(64), nullable=False, comment="品牌")
    category = Column(String(64), nullable=False, comment="类目")
    price = Column(Numeric(10, 2), nullable=False, comment="价格")
    specs = Column(Text, nullable=False, comment="关键参数")
    created_at = Column(DateTime, nullable=False, comment="上架时间")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"comment": "订单表"}

    order_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False, comment="商品SKU")
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False, comment="用户ID")
    order_date = Column(DateTime, nullable=False, comment="下单时间")
    quantity = Column(BigInteger, nullable=False, comment="购买数量")
    amount = Column(Numeric(10, 2), nullable=False, comment="订单金额")
    status = Column(String(16), nullable=False, comment="订单状态：completed/cancelled/returned")


class Return(Base):
    __tablename__ = "returns"
    __table_args__ = {"comment": "退货记录，包含退货商品SKU、退货日期、退货原因、退款金额"}

    return_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="退货ID")
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False, comment="商品SKU")
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False, comment="关联订单ID")
    return_date = Column(DateTime, nullable=False, comment="退货日期")
    reason = Column(String(128), nullable=False, comment="退货原因")
    refund_amount = Column(Numeric(10, 2), nullable=False, comment="退款金额")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"comment": "商品评价"}

    review_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="评价ID")
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False, comment="商品SKU")
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False, comment="用户ID")
    rating = Column(BigInteger, nullable=False, comment="评分 1-5")
    review_text = Column(Text, nullable=False, comment="评价内容")
    review_date = Column(DateTime, nullable=False, comment="评价日期")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = {"comment": "库存表"}

    sku = Column(String(32), ForeignKey("products.sku"), primary_key=True, comment="商品SKU")
    stock_qty = Column(BigInteger, nullable=False, comment="库存数量")
    warehouse = Column(String(32), nullable=False, comment="仓库：BJ/SH/GZ/CD")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
