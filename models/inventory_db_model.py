# models.py
from sqlalchemy import Column, String, Float, DateTime, func
from db.database import Base

class StockItemDB(Base):
    __tablename__ = "stock_items"
    farmer_id = Column(String, primary_key=True)
    item_name = Column(String, primary_key=True)
    quantity = Column(Float, default=0.0)

class StockLogDB(Base):
    __tablename__ = "stock_logs"
    id = Column(String, primary_key=True)
    farmer_id = Column(String, index=True)
    item_name = Column(String)
    used = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class OrderDB(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True)
    farmer_id = Column(String, index=True)
    item_name = Column(String)
    quantity = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
