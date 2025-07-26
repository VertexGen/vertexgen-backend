from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from ..service.transcribe import transcribe_audio
import base64


from orchestrator import handle_query

app = FastAPI(title="Farmer Assistant API")

@app.post("/ask")
async def ask_question(
    user_id: str = Form(...),
    query: Optional[str] = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    try:
        image_base64 = None
        if image:
            image_bytes = await image.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        audio_text = None
        if audio:
            audio_text = transcribe_audio(audio, 'hi-IN')

        result = await handle_query(
            user_id=user_id,
            user_input=audio_text if audio_text else query,
            session_id=session_id,
            image_base64=image_base64
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
