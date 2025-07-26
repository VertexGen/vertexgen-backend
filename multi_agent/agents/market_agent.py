from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.market_tools import market_price_tool

tools = [FunctionTool(func=market_price_tool)]

market_agent = LlmAgent(
    name="MarketAgent",
    model="gemini-2.5-flash",
    description="Agent fetching mandi market prices for crops.",
    tools=tools,
    instruction="""
Use market_price_tool for mandi crop price queries.
"""
)
