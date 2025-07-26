from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.inventory_tools import inventory_status_tool, reorder_suggestions_tool, placeOrder

tools = [
    FunctionTool(func=inventory_status_tool),
    FunctionTool(func=reorder_suggestions_tool),
    FunctionTool(func=placeOrder)
]

inventory_agent = LlmAgent(
    name="InventoryAgent",
    model="gemini-1.5-flash",
    description="Agent managing farm inventory, ordering farm crops and supplies and reorder suggestions.",
    tools=tools,
    instruction="""
Use inventory_status_tool, placeOrder and reorder_suggestions_tool to manage farm stock.
"""
)
