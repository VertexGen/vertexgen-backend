from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.finance_tools import financial_planner_tool

tools = [FunctionTool(func=financial_planner_tool)]

financial_planner_agent = LlmAgent(
    name="FinancialPlannerAgent",
    model="gemini-2.5-flash",
    description="Agent for financial planning of crop farming.",
    tools=tools,
    instruction="""
Use financial_planner_tool for cost/profit/yield related queries.
"""
)
