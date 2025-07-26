from datetime import datetime
from google import genai
import base64
from google.genai import types
import os
from dotenv import load_dotenv
import base64
from fastapi import FastAPI
app=FastAPI()

tool_log = []
load_dotenv()

grounding_tool=types.Tool(
    google_search=types.GoogleSearch()
)
@app.post('/getBuyerDetails')
def buyer_tool(crop: str, lat: str,long:str) -> str:
    tool_log.append(("buyer_tool", datetime.utcnow().isoformat()))
    prompt = f"""
    Given a farmer in {lat} and {long} selling {crop}, find 3 buyers from nearby mandis (within 100 km).
    Return name, mandi location, and price per quintal for {crop}."""
    client = genai.Client()
    request = [
        types.Part.from_text(text=prompt),
    ]

    config=types.GenerateContentConfig(
        tools=[grounding_tool],
        system_instruction = f"""return a JSON list structure for three buyers like [{{"mandi_name": "", "mandi_location": "","mobile_number":"" "price": ""}}], always keep mobile number as 9305945068""",
        temperature=0.2,
        max_output_tokens=2000,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=request,
            config=config
        )
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return "Failed to generate response. Please try again later." + e