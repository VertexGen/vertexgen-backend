from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
from pydantic import BaseModel
from PIL import Image
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode
from models.agent_models.cropDiagnosisModel import CropDiagnosis
from multi_agent.agent_instruction import crop_agent_instruction
from service.tts_audio import generate_audio
import agentops
agentops.init()
import os
from dotenv import load_dotenv
load_dotenv()

agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"),
    trace_name="my-adk-kisan-app-trace"  
)


crop_agent = LlmAgent(
    name="CropDiagnosisAgent",
    model="gemini-2.5-flash",
    description="Diagnose crop issues from image and/or text.",
    instruction=crop_agent_instruction,
    include_contents='default',
    tools=[generate_audio]
)

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

app = FastAPI()
config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
runner = Runner(
    app_name="holistic-query-orchestrator",
    agent=crop_agent,
    session_service=session_service,
    artifact_service=artifact_service,
)

@app.post("/diagnose")
async def cropImageDiagnosis(
    farmer_id: Optional[str]=Form(None),
    query_input: Optional[str] = Form(None),
    image: Optional[UploadFile]=File(None),
):
    temp_session=await session_service.create_session(
        app_name="holistic-query-orchestrator",
        user_id="1234",
    )
    parts = []
    if query_input:
       parts.append(types.Part.from_text(text=query_input))

    if image and image.filename:
       img_data=await image.read()
       parts.append(types.Part.from_bytes(data=img_data, mime_type=image.content_type))
    content = types.Content(role="user", parts=parts)
    result = runner.run_async(user_id=temp_session.user_id,session_id=temp_session.id,new_message=content,run_config=config)
    async for event in result:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
        
    return final_response  # JSON output from specialist agent(s)

agentops.end_session('Success')

# command to run this api locally 
# uvicorn multi_agent.agent.sub_agents.crop_diagnosis:app --reload --env-file .env

