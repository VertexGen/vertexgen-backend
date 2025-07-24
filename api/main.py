# your_project/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from orchestrator import handle_query

app = FastAPI(title="Farmer Assistant API")

class QueryRequest(BaseModel):
    user_id: str
    query: str
    session_id: Optional[str] = None
    image_base64: Optional[str] = None  # Optional image string

class QueryResponse(BaseModel):
    reply: str
    session_id: str
    tool: Optional[dict]

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        result = await handle_query(
            user_id=request.user_id,
            user_input=request.query,
            session_id=request.session_id,
            image_base64=request.image_base64
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn api.main:app --reload
