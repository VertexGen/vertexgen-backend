import datetime
import uuid
import os
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, storage
from google.cloud import texttospeech
from vertexai.language_models import ChatModel
from google.cloud import aiplatform
from models.audioModel import AudioRequest, AudioResponse
import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials, initialize_app
import google.genai as genai
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


# Load environment variables
# load_dotenv()
genai_client = genai.Client(
    vertexai=True,
    project=os.getenv("VERTEX_PROJECT_ID"),
    location="us-central1"
)
# Init FastAPI app and router
app = FastAPI()

def initialize_firebase():
    if not firebase_admin._apps:
        firebase_bucket = os.getenv("FIREBASE_BUCKET")

        cred = credentials.ApplicationDefault()

        initialize_app(cred, {'storageBucket': firebase_bucket})

# Vertex AI Init
aiplatform.init(project="vertexgen-466509", location="us-central1")

# Get AI-generated response from Vertex AI
def get_ai_response(prompt: str, lang: str) -> str:
    # Ask Gemini 2.0 Flash to respond in the requested language
    full_prompt = f"Please translate in {lang} without including the language code. Prompt: {prompt}"
    resp = genai_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )
    return resp.text

# Generate audio from AI response
def generate_audio(text: str, language: str) -> str:
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    audio_filename = f"{uuid.uuid4()}.mp3"
    temp_path = f"/tmp/{audio_filename}"

    with open(temp_path, "wb") as out:
        out.write(response.audio_content)

    # Upload to Firebase
    bucket = storage.bucket()
    blob = bucket.blob(f"audio/{audio_filename}")
    blob.upload_from_filename(temp_path)

    # Set TTL (delete in 5 minutes)
    blob.cache_control = "no-cache"
    blob.custom_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    blob.patch()

    url = blob.generate_signed_url(expiration=datetime.timedelta(minutes=5))

    os.remove(temp_path)
    return url

# API Endpoint
@app.post(
    "/audio/generate",
    response_model=AudioResponse
)
def text_to_audio(request: AudioRequest):
    try:
        ai_text= get_ai_response(request.text,request.language)
        audio_url = generate_audio(ai_text, request.language)
        return {
            "text": ai_text,
            "audio_url": audio_url
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=str(e)
        )