import os
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from google.oauth2.service_account import Credentials
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

from models.advisoryModel import AdvisoryRequest, AdvisoryResponse, Grounding, Source, Support

# 🌱 Load environment
load_dotenv()
gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if gcp_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds

# 🔐 Set up GCP credentials
creds = Credentials.from_service_account_file(
    gcp_creds,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# 🌍 Extract project details
with open(gcp_creds) as f:
    info = json.load(f)
PROJECT_ID = info["project_id"]
LOCATION = "us-central1"

# ⚙️ Init GenAI client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    credentials=creds
)

# 🌐 Enable web grounding
search_tool = Tool(google_search=GoogleSearch())

# 🚀 FastAPI app
app = FastAPI(title="Farm Assistant API")


def ask_farm_assistant(question: str) -> AdvisoryResponse:
    # 🔍 Generate answer using Gemini with grounding
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=GenerateContentConfig(tools=[search_tool])
    )

    cand = resp.candidates[0]
    parts = cand.content.parts
    full_text = "".join([part.text for part in parts if hasattr(part, "text")])

    # 🧠 Build grounding info
    grounding = Grounding(
        queries=cand.grounding_metadata.web_search_queries,
        sources=[
            Source(uri=chunk.web.uri, title=chunk.web.title)
            for chunk in cand.grounding_metadata.grounding_chunks or []
        ],
        supports=[
            Support(
                text=sup.segment.text,
                chunks=sup.grounding_chunk_indices
            ) for sup in cand.grounding_metadata.grounding_supports or []
        ],
        search_html=cand.grounding_metadata.search_entry_point.rendered_content
    )

    # 🎯 Return structured response
    return AdvisoryResponse(
        question=question,
        timestamp=datetime.utcnow(),
        answer_text=full_text,
        grounding=grounding
    )


@app.post("/advisory", response_model=AdvisoryResponse)
async def advisory_endpoint(request: AdvisoryRequest):
    if not request.question:
        return JSONResponse(status_code=400, content={"error": "Missing 'question'"})
    
    response = ask_farm_assistant(request.question)
    return response

#  For local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service.advisory:app", host="127.0.0.1", port=8000, reload=True)