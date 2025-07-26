from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from typing import Optional
import io
import os
from google.auth import default
from google.oauth2 import service_account

from dotenv import load_dotenv

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_credentials():
    creds, _ = default(scopes=SCOPES)
    return creds
    
creds = get_credentials()

from models.transcribeModel import TranscribeRequest, TranscribeResponse, ErrorResponse

app = FastAPI()

async def convert_to_linear16(file: UploadFile) -> bytes:
    input_bytes = await file.read()
    audio = AudioSegment.from_file(io.BytesIO(input_bytes), format=file.filename.split(".")[-1])
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # LINEAR16
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    return buf.getvalue()

@app.post(
    "/transcribe",
    response_model=TranscribeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Transcribe audio in any language using Google Cloud Speech-to-Text",
)
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: str = Query("en-US", description="BCP-47 language code, e.g., hi-IN, ta-IN, en-US")
):
    if not file.content_type.startswith("audio/"):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="Invalid file type").dict()
        )

    try:
        client = speech.SpeechClient()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error=f"Failed to create SpeechClient: {str(e)}").dict()
        )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config)

    try:
        file_data = await convert_to_linear16(file)

        def gen_sync(data, chunk_size=4096):
            for i in range(0, len(data), chunk_size):
                yield speech.StreamingRecognizeRequest(audio_content=data[i:i+chunk_size])

        responses = client.streaming_recognize(streaming_config, gen_sync(file_data))

        transcript = ""
        for response in responses:
            for result in response.results:
                if result.alternatives:
                    transcript += result.alternatives[0].transcript + " "

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error=f"Transcription failed: {str(e)}").dict()
        )

    return TranscribeResponse(transcript=transcript.strip())



### Lang Legend
# | Language     | Code    |
# | ------------ | ------- |
# | Hindi        | `hi-IN` |
# | Tamil        | `ta-IN` |
# | Telugu       | `te-IN` |
# | Marathi      | `mr-IN` |
# | Bengali      | `bn-IN` |
# | Kannada      | `kn-IN` |
# | Malayalam    | `ml-IN` |
# | Gujarati     | `gu-IN` |
# | Punjabi      | `pa-IN` |
# | Urdu         | `ur-IN` |
# | English (IN) | `en-IN` |
# | English (US) | `en-US` |
