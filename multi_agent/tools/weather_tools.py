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

def weather_advisory_tool(lat: str,long: str) -> dict:
    today = datetime.utcnow()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d %B %Y")

    # crop_lines = "\n".join(
    #     [f"- {crop.capitalize()} (Sowing month: {month})" for crop, month in plant_dict.items()]
    # )

    plant_instruction = f"""
        For the specific crop mentioned, carefully analyze tomorrow's weather forecast and provide highly detailed, crop- and stage-specific guidance under "recommendations."
        Address the following:
        - Assess whether tomorrow's weather poses any opportunities or risks for all plants at its current growth or harvesting stage, including sensitivity to temperature, rainfall, humidity, wind, or extreme weather.
        - Explain how the forecasted weather (with seasonal context, given that today's month is the current month) could affect all plants, considering both its typical sowing and primary harvesting periods (for all plant harvesting months.
        - If the crop is within, near, or outside its usual harvesting period, specify how the weather may impact harvesting operations, grain/nut quality, storage, fieldwork timing, or susceptibility to disease/pests.
        - Offer concrete, actionable steps or cautions for the grower—such as adjusting irrigation, advancing/delaying harvest, providing cover, modifying fertilizer or pesticide timing, or deploying risk mitigation related to the specific forecast.

        Under "recommendations," provide exactly one concise, plant- and weather-specific action the farmer should take on this day.
    """

    prompt = f"""
    You are an expert agricultural advisor. Your task is to interpret tomorrow's weather forecast ({tomorrow_str}) at the specified geographic location and for the following crop:

    Latitude: {lat}
    Longitude: {long}

    Return a JSON in this format:
    {{
        "forecast": "<short summary of tomorrow's weather>",
        "critical_alerts": [list here ONLY if there is a serious weather-related risk for this crop/stage, such as flood, drought, severe storm, hail, heatwave, sudden rain during harvest, etc.],
        "recommendations": [A single, crop- and weather-specific line of advice considering growth/harvest window and present forecast],
        "audio_url": "<optional audio explanation or leave null>"
    }}

    Ground your recommendations in both the local forecast and the plant's seasonality—including if the weather enables or threatens key harvest activities, crop quality, or storage. Explicitly connect the weather's effects to the crop's biological and operational needs at this date and location.

    {plant_instruction}
    """




    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(tools=[search_tool])
    )

    parts = resp.candidates[0].content.parts
    full_text = "".join([p.text for p in parts if hasattr(p, "text")])


    import re

    json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
    if json_match:
        try:
            advisory = json.loads(json_match.group())
            print("✅ Clean JSON parsed:", advisory)
        except json.JSONDecodeError as e:
            print("❌ Still failed parsing JSON:", e)
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
