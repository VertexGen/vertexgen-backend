from datetime import datetime

tool_log = []

def crop_diagnosis_tool(farmer_id: str, query_input: str, image_base64: str) -> dict:
    tool_log.append(("crop_diagnosis_tool", datetime.utcnow().isoformat()))
    return {
        "diagnosis": "Powdery Mildew",
        "confidence": 0.91,
        "recommended_actions": [
            "Use neem spray in mornings.",
            "Avoid watering in evening."
        ]
    }
