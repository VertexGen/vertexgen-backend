from datetime import datetime
from google import genai
import base64
from google.genai import types
from models.crop_diagnosis import CropDiagnosis
import os
from dotenv import load_dotenv
import base64

tool_log = []
load_dotenv()

def crop_diagnosis_tool(farmer_id: str, query_input: str, image_base64: str) -> str:
    print("INSIDE crop_diagnosis_tool")

    # with open("output.jpg", "wb") as f:
    #     f.write(base64.b64decode(image_base64))

    print("INPUTS:", {"farmer_id": farmer_id, "query_input": query_input})
    tool_log.append(("crop_diagnosis_tool", datetime.utcnow().isoformat()))
    
    try:
        image_bytes = base64.b64decode(image_base64)
    except Exception as e:
        print("Base64 decode error:", e)
        return "Invalid image input"

    client = genai.Client()
    request = [
        types.Part.from_text(text=query_input),
        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    ]

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=request,
            config={
                'response_mime_type': 'application/json',
                'response_schema': CropDiagnosis,
                'system_instruction': 'Given crop image and text, identify the crop condition and suggest a diagnosis',
                'temperature': 0.2,
                'max_output_tokens': 2000
            },
        )
        print("Tool Response:", response)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        print("Error during generate_content:", e)
        return "Failed to generate diagnosis. Please try again later." + e

