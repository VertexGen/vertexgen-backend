from models.agent_models.cropDiagnosisModel import CropDiagnosis

crop_agent_instruction = f"""
Given crop image and text, identify the crop condition and suggest a diagnosis, structured as per CropDiagnosis model:
{CropDiagnosis.schema_json(indent=2)}

Ensure:
- `message` includes keys like "Crop Condition" and diagnosis/suggestions as why this disease occured.
- Pass `message` to `generate_audio` tool with appropriate locale code identified from incoming query_input text.
- Populate `audio_url` field with the URL returned by `generate_audio` tool.

strictly stick to response as json structured only.
"""