import os
import json
import re
from datetime import datetime

from dotenv import load_dotenv
from models.financial_planner import FinancialPlan
from google.oauth2.service_account import Credentials
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from fastapi import FastAPI, HTTPException

app=FastAPI(title="Financial Planner API", version="1.0")
load_dotenv()
gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if gcp_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds

creds = Credentials.from_service_account_file(
    gcp_creds,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

PROJECT_ID = json.load(open(gcp_creds))["project_id"]
LOCATION = "us-central1"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    credentials=creds
)

search_tool = Tool(google_search=GoogleSearch())

tool_log = []


@app.post('/financial_planner', response_model=FinancialPlan)
async def financial_planner_tool(
    lat : str,
    long: str,
    crop: str,
    area_acres: float
) -> FinancialPlan:
    tool_log.append(("financial_planner_tool", datetime.utcnow().isoformat()))

    prompt = f"""
You are a smart financial assistant for Indian farmers. Please analyze and calculate the financial planning details based on the following inputs:

Crop: {crop}
Area (in acres): {area_acres}
Latitude: {lat}
Longitude: {long}

You have the knowledge of crop seasons, regional climate conditions, and cost economics. I am sowing this crop now, so I want you to:

1. Estimate all necessary cost parameters required to cultivate this crop for the given location and land size, such as:
   - seed_cost
   - fertilizer_cost
   - labor_cost
   - irrigation_cost
   - pesticide_cost
   - other_cost

2. Predict:
   - expected_yield_kg (in kilograms)
   - expected_price_per_kg (in rupees)
   - harvest_month

3. Then calculate the financial plan using these values.

Make sure that no value in the final output is null. If actual data is unavailable, use estimated averages for the region and crop type to fill the values meaningfully.

Output a JSON strictly with the following structure (no additional keys allowed):
{{
  "crop": "",
  "total_cost": 0.0,
  "total_cost_division": {{
    "seed_cost":0.0 ,
    "fertilizer_cost":0.0,
    "labor_cost": 0.0,
    "irrigation_cost": 0.0,
    "pesticide_cost": 0.0 ,
    "other_cost": 0.0
  }},

  "expected_income": 0.0,
  "net_profit": 0.0,
  "break_even_price": 0.0,
  "expected_yield_kg": 0.0,
  "expected_price_per_kg": 0.0,
  "harvest_month": "",
  "advice": ""
}}

Guidelines:
- total_cost: sum of all individual input costs
- total_cost_division: MUST be a nested JSON object (not string)
- expected_income = expected_yield_kg × expected_price_per_kg
- net_profit = expected_income - total_cost
- break_even_price = total_cost / expected_yield_kg (rounded to 2 decimals)
- harvest_month: based on the current sowing time and crop duration (always return a valid month name)
- advice: short financial guidance related to maximizing profit and reducing risk
"""


    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(temperature=0.2, tools=[search_tool])
    )

    parts = resp.candidates[0].content.parts
    full_text = "".join([p.text for p in parts if hasattr(p, "text")])
    print("📊 Gemini Financial Response:\n", full_text)

    cleaned_text = full_text.strip()
    if cleaned_text.startswith("```json") or cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```json\s*|```$", "", cleaned_text.strip(), flags=re.MULTILINE)

    json_match = re.search(r'\{[\s\S]*?\}', cleaned_text)
    if json_match:
        try:
            json_start = cleaned_text.find("{")
            json_end = cleaned_text.rfind("}")
            json_str = cleaned_text[json_start:json_end+1]
            print("📦 Cleaned JSON block:\n", json_str)
            plan_raw = json.loads(json_str)

            return FinancialPlan(
                crop=plan_raw.get("crop"),
                total_cost=plan_raw.get("total_cost"),
                total_cost_division=plan_raw.get("total_cost_division"),
                expected_income=plan_raw.get("expected_income"),
                net_profit=plan_raw.get("net_profit"),
                break_even_price=plan_raw.get("break_even_price"),
                expected_yield_kg=plan_raw.get("expected_yield_kg"),
                expected_price_per_kg=plan_raw.get("expected_price_per_kg"),
                harvest_month=plan_raw.get("harvest_month"),
                advice=plan_raw.get("advice")
            )

        except Exception as e:
            print("❌ Failed to parse financial plan:", e)
            raise HTTPException(status_code=500, detail="Failed to parse Gemini financial response.")
