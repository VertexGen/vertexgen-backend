from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.inventory_tools import inventory_status_tool, reorder_suggestions_tool

tools = [
    FunctionTool(func=inventory_status_tool),
    FunctionTool(func=reorder_suggestions_tool)
]

inventory_agent = LlmAgent(
    name="InventoryAgent",
    model="gemini-1.5-flash",
    description="Agent managing farm inventory and reorder suggestions.",
    tools=tools,
    instruction="""
Use inventory_status_tool and reorder_suggestions_tool to manage farm stock.
"""
)
