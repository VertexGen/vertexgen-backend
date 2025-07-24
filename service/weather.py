
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
app = FastAPI(title="🌾 Weather Alert Farmer Assistant API", version="1.0")




# Main advisory logic
def ask_farm_assistant(lat: str,long: str, plant_dict: dict) -> dict:
    today = datetime.utcnow()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d %B %Y")

    crop_lines = "\n".join(
        [f"- {crop.capitalize()} (Sowing month: {month})" for crop, month in plant_dict.items()]
    )

    plant_instruction = f"""
    The farmer is g
    {crop_lines}

    For each of these crops, provide weather-sensitive, crop-specific suggestions under "recommendations".
    The recommenrowing the following crops (with their ideal sowing months):
dations should explain:
    - Whether the weather is favorable or risky for each crop
    - Based on the sowing month in on the next day how weather impacts in that stage
    - What actions or precautions should be taken (e.g., irrigation, drainage, delay in sowing, protection, etc.)

    Return one line per crop under "recommendations".
    """

    prompt = f"""
    You're an expert farm advisor. Based on tomorrow's weather ({tomorrow_str}) for the following location/crop-related query:

    these are the latitute and longidute of the location 
    {lat} {long}

    Please respond in a JSON format with the following structure:
    {{
        "forecast": "<brief weather forecast summary>",
        "critical_alerts": [list only if weather poses severe risk to crops, such as floods, heatwaves, hail etc],
        "recommendations": [one short line per crop with crop-specific crisp weather-sensitive advice],
        "audio_url": "<optional audio explanation or leave null>"
    }}

    Be dynamic: infer severity from forecast, and customize the recommendations using this crop list.
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


# 🔹 POST Endpoint for advisory
@app.post("/predict", response_model=WeatherAdvisory)
def get_farm_advisory(request: AdvisoryRequest):
    try:
        result = ask_farm_assistant(request.lat,request.long, request.plant_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# For local run
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("service.weather:app", host="127.0.0.1", port=8000, reload=True)