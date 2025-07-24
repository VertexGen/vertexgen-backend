import asyncio
from typing import Optional
from datetime import datetime
from google.adk.tools import ToolContext

tool_log = []

async def market_price_tool(crop: str, mandi: Optional[str] = None, tool_context: ToolContext = None) -> dict:
    tool_log.append(("market_price_tool", datetime.utcnow().isoformat()))
    return {
        "crop": crop,
        "mandi": mandi or "Default Mandi",
        "price": 2100,
        "trend": "rising",
        "advice": "Consider waiting a week for better rates."
    }
