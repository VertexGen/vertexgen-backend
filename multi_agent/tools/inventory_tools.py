import asyncio
from datetime import datetime
import uuid
from google.adk.tools import ToolContext
from sqlalchemy.orm import Session
from db.database import SessionLocal, init_db
from models.inventory_db_model import StockItemDB,StockLogDB
from models.inventory_vendor import StockItem,StockLog,ReorderSuggestion
init_db()
tool_log = []
from fastapi import FastAPI
app=FastAPI()

@app.post('/inventoryStatus')
async def inventory_status_tool(farmer_id: str) -> list:
    db = SessionLocal()
    items = db.query(StockItemDB).filter(StockItemDB.farmer_id == farmer_id).all()
    db.close()
    return [StockItem(item_name=i.item_name, quantity=i.quantity) for i in items]


@app.post('/logInventory')
async def log_inventory_tool(farmer_id: str, item_name: str, used: float) -> StockLog:
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

@app.post('/reorderSuggestion')
async def reorder_suggestions_tool(farmer_id: str) -> list:
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
