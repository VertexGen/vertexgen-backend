import asyncio
from typing import List, Optional
from datetime import datetime
from google.adk.tools import ToolContext
from fastapi import FastAPI, HTTPException, Query
from google import genai
import base64
from google.genai import types
import os

from sqlalchemy import exc
from models.scheme_navigator import Scheme, ApplicationStatus
from models.scheme_db import SchemeMaster,AppliedScheme
from db.database import SessionLocal,init_db
from models.scheme_db import AppliedScheme
import uuid
from sqlalchemy import func

init_db()
app=FastAPI()

tool_log = []

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

async def get_schemes(region: Optional[str] = None, crop: Optional[str] = None,tool_context: ToolContext = None):
    tool_log.append(("schemes_tool", datetime.utcnow().isoformat()))
    db = SessionLocal()
    query = db.query(SchemeMaster)

    if region:
        query = query.filter(
            func.lower(SchemeMaster.region) == region.lower()
        )
    if crop:
        query = query.filter(
            func.lower(SchemeMaster.crop) == crop.lower()
        )

    results = query.all()
    db.close()
    return results

#     client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     request=[]
#     prompt=f"Find relative Kisan Yojana schemes based on {region} and {crop} for the farmer"
#     request.append(types.Part.from_text(text=prompt))
#     response=client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=request,
#         config={
#             'system_instruction':f"""Given region and crop,Use the tool to fetch relevant 3 Kisan Yojana schemes.Do not add any introductory description Only Return a JSON array matching this schema: {Scheme.schema_json()}
# if `scheme_id` is null then populate a dummy schemeId""",
#             'temperature':0.2,
#             'tools':[grounding_tool]
#         },
#     )
#     return response.text

async def apply_scheme_tool(scheme_id: str, farmer_id: str,tool_context: ToolContext = None) -> dict:
    tool_log.append(("apply_scheme_tool", datetime.utcnow().isoformat()))
    session = SessionLocal()
    try:
        # Get scheme_name from SchemeMaster
        master = session.query(SchemeMaster).filter_by(scheme_id=scheme_id).first()
        if not master:
            raise HTTPException(status_code=404, detail="Invalid scheme_id")

        # Generate a unique reference ID
        ref_id = f"{scheme_id}-{farmer_id}-{uuid.uuid4().hex[:6]}"

        # Insert into AppliedScheme with scheme_name
        entry = AppliedScheme(
            reference_id=ref_id,
            scheme_id=scheme_id,
            farmer_id=farmer_id
        )
        session.add(entry)
        session.commit()

    except HTTPException:
        session.rollback()
        raise
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {
            "status": "applied",
            "reference_id": ref_id,
            "scheme_id":scheme_id,
            "scheme_name":master.scheme_name
        }
    finally:
        session.close()