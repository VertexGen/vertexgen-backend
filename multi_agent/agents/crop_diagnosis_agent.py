from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.crop_tools import crop_diagnosis_tool

tools = [FunctionTool(func=crop_diagnosis_tool)]

crop_diagnosis_agent = LlmAgent(
    name="CropDiagnosisAgent",
    model="gemini-2.5-flash",
    description="Agent for crop disease diagnosis using images and queries.",
    tools=tools,
    instruction="""
Use crop_diagnosis_tool for plant disease diagnosis using images.
"""
)
