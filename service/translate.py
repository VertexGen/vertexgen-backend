
from models.translateModel import TranslationResponse,TranslationRequest
import os
from fastapi import FastAPI, HTTPException, Query
# Import GenerativeModel instead of ChatModel from preview
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig # Import necessary classes
from google.cloud import aiplatform

from dotenv import load_dotenv
load_dotenv()

gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if gcp_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds
    
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



#  For local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service.translate:app", host="127.0.0.1", port=8000, reload=True)