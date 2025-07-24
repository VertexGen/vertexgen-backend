import asyncio
from datetime import datetime
from google.adk.tools import ToolContext

tool_log = []

async def inventory_status_tool(farmer_id: str, tool_context: ToolContext) -> list:
    tool_log.append(("inventory_status_tool", datetime.utcnow().isoformat()))
    return [
        {"item_name": "wheat", "quantity": 5},
        {"item_name": "tomato", "quantity": 2}
    ]

async def reorder_suggestions_tool(farmer_id: str, tool_context: ToolContext) -> list:
    tool_log.append(("reorder_suggestions_tool", datetime.utcnow().isoformat()))
    return [
        {"item_name": "wheat", "need_quantity": 10, "vendor_id": "V123", "price_per_unit": 150},
        {"item_name": "tomato", "need_quantity": 5, "vendor_id": "V456", "price_per_unit": 200}
    ]
