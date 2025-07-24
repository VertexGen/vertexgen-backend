from datetime import datetime
from google import genai
import base64
from google.genai import types
from models.crop_diagnosis import CropDiagnosis
import os

tool_log = []

def crop_diagnosis_tool(farmer_id: str, query_input: str, image_base64: str) -> str:
    tool_log.append(("crop_diagnosis_tool", datetime.utcnow().isoformat()))
    client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    request=[]
    image_bytes = base64.b64decode(image_base64)
    request.append(types.Part.from_text(text=query_input))
    request.append(types.Part.from_bytes(data=image_bytes,mime_type='image/jpeg'))
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=request,
        config={
            'response_mime_type':'application/json',
            'response_schema':CropDiagnosis,
            'system_instruction':'Given crop image and text, identify the crop condition and suggest a diagnosis',
            'temperature':0.2,
            'max_output_tokens':2000
        },
    )
    return response.text
