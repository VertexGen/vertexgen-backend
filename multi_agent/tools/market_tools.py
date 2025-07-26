import os
import json
import re
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from models.market_analysis import MarketPrice
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.oauth2.service_account import Credentials
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

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

# Initialize Vertex AI Client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    credentials=creds
)

# Search grounding tool
search_tool = Tool(google_search=GoogleSearch())

# FastAPI app
app = FastAPI(title="🌾Market Assistant API", version="1.0")


# Main advisory logic
def ask_farm_assistant(lat: str, long: str, crop: str) -> MarketPrice:
    today = datetime.utcnow().strftime("%d %B %Y")

    prompt = f"""
    You are an expert farm advisor. Based on tomorrow's weather ({today}) for the following location and crop:

    Latitude: {lat}
    Longitude: {long}
    Crop: {crop}

    Please respond in a JSON format with the following structure:
    {{
        "crop": "",
        "mandi": "",
        "price": "",
        "trend": "",
        "advice": "",
        "audio_url": ""
    }}

    Guidelines:
    - crop: Name of the crop
    - mandi: Local mandi/market name
    - price: Current price in numeric format (e.g., 2123.0)
    - trend: One of "increasing", "decreasing", or "stable" on the basis of price trend
    - advice: Contextual market-price advice for the farmer, if the market prices are high for crop then suggest the farmer to sell in market, if the prices are low then suggest to store the crop,
    also if the prices are stable then suggest to wait for few days and sell in market
    also when it comes any comodity apart from crops like the things farmer has to buy for his farm like seeds, fertilizers, pesticides etc 
    then suggest the farmer to buy it in next days when the prices are low or if the prices are rising then tell it buy now 
    - audio_url: Keep it null or empty string
    """

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(temperature=0.2, tools=[search_tool])
    )

    parts = resp.candidates[0].content.parts
    full_text = "".join([p.text for p in parts if hasattr(p, "text")])
    print("🔍 Gemini response:", full_text)
    # Clean any Markdown code block formatting
    cleaned_text = full_text.strip()
    if cleaned_text.startswith("```json") or cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```json\s*|```$", "", cleaned_text.strip(), flags=re.MULTILINE)

    # Try parsing the cleaned JSON
    json_match = re.search(r'\{[\s\S]*?\}', cleaned_text)
    if json_match:
        try:
            json_str = json_match.group()
            print("📦 Cleaned JSON block:\n", json_str)
            advisory_raw = json.loads(json_str)

            # Build the response
            advisory = MarketPrice(
                crop=advisory_raw.get("crop"),
                mandi=advisory_raw.get("mandi"),
                price=str(advisory_raw.get("price")),  # 👈 force to string
                trend=advisory_raw.get("trend"),
                advice=advisory_raw.get("advice"),
                audio_url=advisory_raw.get("audio_url") or None
            )

        except Exception as e:
            print("❌ Failed to parse and convert advisory:", e)
            raise HTTPException(status_code=500, detail="Failed to parse Gemini response.")
    else:
        raise HTTPException(status_code=500, detail="No valid JSON object found in Gemini output.")

    return advisory


# 🔹 POST Endpoint for advisory
@app.post("/predict", response_model=MarketPrice)
def get_farm_advisory(lat: str, long: str, crop: str):
    try:
        result = ask_farm_assistant(lat, long, crop)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
