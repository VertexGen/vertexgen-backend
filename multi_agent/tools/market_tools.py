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
from google.auth import default
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_credentials():
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if gcp_creds:
        # Local development using service account key file
        return service_account.Credentials.from_service_account_file(
            gcp_creds, scopes=SCOPES
        )
    else:
        # Deployed environment (GCP provides default credentials)
        creds, _ = default(scopes=SCOPES)
        return creds

creds = get_credentials()

PROJECT_ID = "vertexgen-466509"
LOCATION = "us-central1"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    credentials=creds
)

search_tool = Tool(google_search=GoogleSearch())

def market_price_tool(lat: str, long: str, crop: str) -> MarketPrice:
    today = datetime.utcnow().strftime("%d %B %Y")

    prompt = f"""
    You are an expert farm advisor. Based on tomorrow's weather ({today}) for the following location and crop:

    Latitude: {lat}
    Longitude: {long}
    Crop: {crop}

    Your unit of the price should be the regional currently of the location of the latitutude and longitude

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
    
    cleaned_text = full_text.strip()
    if cleaned_text.startswith("```json") or cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```json\s*|```$", "", cleaned_text.strip(), flags=re.MULTILINE)

    json_match = re.search(r'\{[\s\S]*?\}', cleaned_text)
    if json_match:
        try:
            json_str = json_match.group()
            print("📦 Cleaned JSON block:\n", json_str)
            advisory_raw = json.loads(json_str)

            advisory = MarketPrice(
                crop=advisory_raw.get("crop"),
                mandi=advisory_raw.get("mandi"),
                price=str(advisory_raw.get("price")),
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