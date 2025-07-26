from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.weather_tools import weather_advisory_tool

tools = [FunctionTool(func=weather_advisory_tool)]

weather_agent = LlmAgent(
    name="WeatherAgent",
    model="gemini-2.5-flash",
    description="Agent providing weather forecasts and advisories.",
    tools=tools,
    instruction="""
Use weather_advisory_tool for forecast, alerts, and tips.
"""
)
