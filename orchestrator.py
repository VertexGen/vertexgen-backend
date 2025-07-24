# your_project/orchestrator_service.py

import asyncio
import base64
from io import BytesIO
from dotenv import load_dotenv

from PIL import Image
from datetime import datetime
from typing import Optional, List

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

# Import tools
from multi_agent.tools.crop_tools import crop_diagnosis_tool
from multi_agent.tools.finance_tools import financial_planner_tool
from multi_agent.tools.inventory_tools import inventory_status_tool, reorder_suggestions_tool
from multi_agent.tools.market_tools import market_price_tool
from multi_agent.tools.scheme_tools import schemes_tool, apply_scheme_tool
from multi_agent.tools.weather_tools import weather_advisory_tool

load_dotenv()

# Define tools + agent
tools = [
    FunctionTool(func=crop_diagnosis_tool),
    FunctionTool(func=financial_planner_tool),
    FunctionTool(func=inventory_status_tool),
    FunctionTool(func=reorder_suggestions_tool),
    FunctionTool(func=market_price_tool),
    FunctionTool(func=schemes_tool),
    FunctionTool(func=apply_scheme_tool),
    FunctionTool(func=weather_advisory_tool),
]
 
orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model="gemini-2.5-flash",
    description="Farm agent that answers farmer queries using tools.",
    tools=tools,
    instruction="""
When a user asks a farm-related question:
✅ Use crop_diagnosis_tool for images + plant problems  
✅ Use financial_planner_tool for cost/profit/yield  
✅ Use inventory_status_tool and reorder_suggestions_tool to manage farm stock  
✅ Use market_price_tool to fetch mandi crop prices  
✅ Use schemes_tool and apply_scheme_tool for government programs  
✅ Use weather_advisory_tool for forecast, alerts, and tips  
Always call a tool when enough info is present.
"""
)


_sessions_store = {}

session_service = InMemorySessionService()

async def get_or_create_session(user_id: str, session_id: str = None):
    if session_id and session_id in _sessions_store:
        return _sessions_store[session_id]
    else:
        session = await session_service.create_session(app_name="FarmerAssistant", user_id=user_id)
        _sessions_store[session.id] = session
        return session


async def handle_query(
    user_id: str,
    user_input: str,
    session_id: Optional[str] = None,
    image_base64: Optional[str] = None
) -> dict:
    session = await get_or_create_session(user_id=user_id, session_id=session_id)

    parts = []
    text = f"My farmer ID is {user_id}.\n{user_input}"

    image_bytes = base64.b64decode(image_base64) if image_base64 else None
    if image_bytes:
        try:
            Image.open(BytesIO(image_bytes)).verify()
            parts.append(types.Part(text=text))
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        except Exception:
            parts.append(types.Part(text=text))
    else:
        parts.append(types.Part(text=text))

    message = types.Content(role="user", parts=parts)

    runner = Runner(agent=orchestrator_agent, app_name="FarmerAssistant", session_service=session_service)

    reply_text = ""
    tool_calls = []

    async for event in runner.run_async(
        new_message=message,
        user_id=user_id,
        session_id=session.id
    ):
        if hasattr(event, "tool_call") and event.tool_call:
            call = event.tool_call
            tool_calls.append({
                "name": call.name,
                "kwargs": call.kwargs,
            })
        elif hasattr(event, "content") and event.content:
            reply_text += "".join(part.text or "" for part in event.content.parts)

    return {
        "reply": reply_text,
        "tool": tool_calls if tool_calls else None,  # Return list or None
        "session_id": session.id
    }
