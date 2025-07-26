
from models.translateModel import TranslationResponse,TranslationRequest
import os
from fastapi import FastAPI, HTTPException, Query
# Import GenerativeModel instead of ChatModel from preview
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig # Import necessary classes
from google.cloud import aiplatform
from google.oauth2 import service_account
from google.auth import default


from dotenv import load_dotenv

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_gcp_credentials():
    gcp_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if gcp_creds_path:
        # Use the local credentials file
        return service_account.Credentials.from_service_account_file(
            gcp_creds_path,
            scopes=SCOPES
        )
    else:
        # Use the default credentials provided by the environment (Cloud Run, App Engine, etc.)
        creds, _ = default(scopes=SCOPES)
        return creds
    
# FastAPI app
app = FastAPI()

@app.post("/translate", response_model=TranslationResponse)
def get_translation( request: TranslationRequest):
    try:
        # Initialize the Gemini model
        model = GenerativeModel("gemini-2.0-flash")

        # Start chat
        chat_session = model.start_chat()

        # Prepare prompt
        prompt = f"Translate the following sentence to {request.target_language}. Respond ONLY with the translated text. Do NOT include any explanation, transliteration, or alternative options:\n\n{request.text}"

        # Send prompt
        response = chat_session.send_message(prompt)

        # Extract trasnslation
        translated = response.candidates[0].content.parts[0].text.strip()
        print(translated)
        return TranslationResponse(translated_phrase=translated)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



