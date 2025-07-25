# your_project/orchestrator_service.py

import asyncio
import base64
from io import BytesIO
from dotenv import load_dotenv

from PIL import Image
from datetime import datetime
from typing import Optional, List
import time
import os

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

# Define tools
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

# Define agent with improved instructions
orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model="gemini-2.0-flash",
    description="Farm agent that answers farmer queries using tools.",
    tools=tools,
    instruction="""
You are the OrchestratorAgent responsible for answering farm-related queries using the appropriate tools.

🧠 Tool Usage Guide:

1️⃣ **Crop Diagnosis**
   - Always use `crop_diagnosis_tool` when the user:
     - Uploads or includes an image (assume it's a plant/crop)
     - Describes any symptoms related to crop issues (e.g., pests, yellowing, wilting, black spots)
   - If both image and text are available, pass both to the tool.

2️⃣ **Financial Planning**
   - Use `financial_planner_tool` for queries about profit, cost, or yield.

3️⃣ **Inventory Management**
   - Use `inventory_status_tool` to check farm stock.
   - Use `reorder_suggestions_tool` to suggest what to reorder.

4️⃣ **Market Prices**
   - Use `market_price_tool` to fetch mandi crop prices.

5️⃣ **Government Schemes**
   - Use `schemes_tool` to find schemes.
   - Use `apply_scheme_tool` to help apply for a scheme.

6️⃣ **Weather Advisory**
   - Use `weather_advisory_tool` for weather tips, forecasts, and alerts.

✅ General Instructions:
- If the user provides an image without a clear question, assume it's about crop health and call the crop diagnosis tool.
- If unclear, ask clarifying questions.
- Never answer from your own knowledge when a tool exists for that domain.
"""
)

_sessions_store = {}
session_service = InMemorySessionService()

async def get_or_create_session(user_id: str, session_id: str = None):
    if session_id:
        if session_id in _sessions_store:
            return _sessions_store[session_id]
        else:
            session = await session_service.create_session(
                app_name="FarmerAssistant",
                user_id=user_id,
                session_id=session_id
            )
            _sessions_store[session_id] = session
            return session
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

    print(image_base64)

    parts = []
    text = f"My farmer ID is {user_id}.\n{user_input}"

    image_bytes = base64.b64decode(image_base64) if image_base64 else None

    if image_bytes:
        try:
            Image.open(BytesIO(image_bytes))
            text += "\nThe farmer has uploaded a crop image that may show a plant disease or problem. Use the crop diagnosis tool with this image."
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
            parts.append(types.Part(text=text))
        except Exception as e:
            print("❌ Failed to decode image:", e)
            parts.append(types.Part(text=text))
    else:
        parts.append(types.Part(text=text))

    message = types.Content(role="user", parts=parts)
    runner = Runner(agent=orchestrator_agent, app_name="FarmerAssistant", session_service=session_service)

    reply_text = ""
    tool_calls = []
    start_time = time.time()

    async for event in runner.run_async(new_message=message, user_id=user_id, session_id=session.id):
        print(f"[{time.time() - start_time:.2f}s] Received event of type: {type(event)}")

        if event.content:
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    print(f"🔧 Tool call detected: {fc.name} with args: {fc.args}")
                    tool_calls.append({
                        "name": fc.name,
                        "kwargs": fc.args,
                    })

                elif hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    print(f"✅ Tool response received: {fr.name} with result: {fr.response}")

                elif hasattr(part, "text") and part.text:
                    print(f"💬 Appending text: {part.text}")
                    reply_text += part.text

    # Diagnostic warning if image provided but crop tool not called
    if image_base64 and not any(call["name"] == "crop_diagnosis_tool" for call in tool_calls):
        print("⚠️ WARNING: Image was provided but crop_diagnosis_tool was NOT called.")

    return {
        "reply": reply_text,
        "tool": tool_calls if tool_calls else [],
        "session_id": session.id
    }
