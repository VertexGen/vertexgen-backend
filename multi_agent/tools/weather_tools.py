import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dotenv import load_dotenv
from models.weatherAdvisoryModel import WeatherAdvisory,AdvisoryRequest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.oauth2.service_account import Credentials
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import re
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

def weather_advisory_tool(lat: str, long: str, crops: list[str]) -> dict:
    today = datetime.utcnow()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d %B %Y")

    crop_list = ", ".join(crops)

    prompt = f"""
    You are an expert agricultural advisor. Based on tomorrow's weather ({tomorrow_str}) for this location:

    Latitude: {lat}
    Longitude: {long}

    The farmer is growing the following crops: {crop_list}

    For each crop:
    - Infer its typical sowing month in this region
    - Estimate its current growth stage
    - Analyze if the weather conditions for tomorrow are favorable or risky for that stage
    - Provide a short, clear, actionable weather-sensitive recommendation

    Respond in this JSON format:
    {{
        "forecast": "<brief weather forecast summary>",
        "critical_alerts": [list only if weather poses severe risk to crops, such as floods, heatwaves, hail, etc],
        "recommendations": [one short line per crop with crop-specific crisp weather-sensitive advice],
        "audio_url": "<optional audio explanation or leave null>"
    }}
    """

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(tools=[search_tool])
    )

    parts = resp.candidates[0].content.parts
    full_text = "".join([p.text for p in parts if hasattr(p, "text")])

    json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
    if json_match:
        try:
            advisory = json.loads(json_match.group())
            print("✅ Clean JSON parsed:", advisory)
        except json.JSONDecodeError as e:
            print("❌ JSON parsing failed:", e)
            advisory = {
                "forecast": None,
                "critical_alerts": [],
                "recommendations": ["❗ Could not parse Gemini response correctly."],
                "audio_url": None
            }
    else:
        print("❌ No JSON object found in Gemini output.")
        advisory = {
            "forecast": None,
            "critical_alerts": [],
            "recommendations": ["❗ No JSON found in Gemini response."],
            "audio_url": None
        }

    return advisory
