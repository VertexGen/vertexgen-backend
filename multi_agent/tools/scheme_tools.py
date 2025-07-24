import asyncio
from typing import Optional
from datetime import datetime
from google.adk.tools import ToolContext

tool_log = []

async def schemes_tool(region: Optional[str] = None, crop: Optional[str] = None, tool_context: ToolContext = None) -> list:
    tool_log.append(("schemes_tool", datetime.utcnow().isoformat()))
    return [
        {"scheme_id": "SC001", "name": "Organic Farming Support", "description": "Get subsidy on bio-inputs."},
        {"scheme_id": "SC002", "name": "Solar Pump Subsidy", "description": "50% cost covered for solar pumps."}
    ]

async def apply_scheme_tool(scheme_id: str, farmer_id: str, tool_context: ToolContext) -> dict:
    tool_log.append(("apply_scheme_tool", datetime.utcnow().isoformat()))
    return {
        "status": "applied",
        "reference_id": f"{scheme_id}-{farmer_id}"
    }
