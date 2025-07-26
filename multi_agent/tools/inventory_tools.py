import asyncio
from datetime import datetime
import uuid
from google.adk.tools import ToolContext
from sqlalchemy.orm import Session
from db.database import SessionLocal, init_db
from models.inventory_db_model import OrderDB, StockItemDB,StockLogDB
from models.inventory_vendor import StockItem,StockLog,ReorderSuggestion
init_db()
tool_log = []
from fastapi import FastAPI
app=FastAPI()

async def inventory_status_tool(farmer_id: str,tool_context: ToolContext = None) -> list:
    db = SessionLocal()
    items = db.query(StockItemDB).filter(StockItemDB.farmer_id == farmer_id).all()
    db.close()
    return [StockItem(item_name=i.item_name, quantity=i.quantity) for i in items]


async def log_inventory_tool(farmer_id: str, item_name: str, used: float,tool_context: ToolContext = None) -> StockLog:
    db = SessionLocal()
    stock = db.get(StockItemDB, {"farmer_id": farmer_id, "item_name": item_name})
    if not stock:
        stock = StockItemDB(farmer_id=farmer_id, item_name=item_name, quantity=0.0)
    stock.quantity -= used
    db.add(stock)
    entry = StockLogDB(
        id=str(uuid.uuid4()), 
        farmer_id=farmer_id, 
        item_name=item_name, 
        used=used
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    db.close()
    return StockLog(item_name=entry.item_name, used=entry.used, timestamp=entry.timestamp)

async def reorder_suggestions_tool(farmer_id: str,tool_context: ToolContext = None) -> list:
    tool_log.append(("reorder_suggestions_tool", datetime.utcnow().isoformat()))
    db = SessionLocal()
    suggestions = []
    items = db.query(StockItemDB).filter(StockItemDB.farmer_id == farmer_id).all()
    for item in items:
        if item.quantity < 5:  # e.g. threshold
            suggestions.append(ReorderSuggestion(
                item_name=item.item_name,
                need_quantity=10 - item.quantity,
                vendor_id="DEFAULT_VENDOR",
                price_per_unit=100.0,
                audio_url=None
            ))
    db.close()
    return suggestions

async def placeOrder(farmer_id: str, item: str, quantity: float,tool_context: ToolContext = None) -> str:
    tool_log.append(("order_place_tool", datetime.utcnow().isoformat()))
    db = SessionLocal()
    try:
        # 1. Log order
        new_order = OrderDB(
            order_id=str(uuid.uuid4()),
            farmer_id=farmer_id,
            item_name=item,
            quantity=quantity
        )
        db.add(new_order)

        # 2. Update stock quantity (insert if not present)
        stock = db.query(StockItemDB).filter_by(farmer_id=farmer_id, item_name=item).first()
        if stock:
            stock.quantity += quantity
        else:
            stock = StockItemDB(farmer_id=farmer_id, item_name=item, quantity=quantity)
            db.add(stock)

        db.commit()
        return f"Order placed and stock updated for item: {item}"
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"
    finally:
        db.close()