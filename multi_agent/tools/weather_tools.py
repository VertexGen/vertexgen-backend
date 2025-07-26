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
