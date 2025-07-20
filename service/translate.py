from fastapi import FastAPI
from models.translateModel import TranslationResponse

app = FastAPI()

@app.get("/translate", response_model=TranslationResponse)
def get_translation():
    return TranslationResponse()
