from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.scheme_tools import schemes_tool, apply_scheme_tool

tools = [
    FunctionTool(func=schemes_tool),
    FunctionTool(func=apply_scheme_tool)
]

scheme_agent = LlmAgent(
    name="SchemeAgent",
    model="gemini-2.5-flash",
    description="Agent handling government schemes for farmers.",
    tools=tools,
    instruction="""
Use schemes_tool and apply_scheme_tool for gov programs.
"""
)
