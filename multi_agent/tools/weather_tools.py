import asyncio
from typing import Dict, Any
from datetime import datetime
from google.adk.tools import ToolContext

tool_log = []

async def weather_advisory_tool(lat: float, lon: float, tool_context: ToolContext) -> Dict[str, Any]:
    tool_log.append(("weather_advisory_tool", datetime.utcnow().isoformat()))
    return {
        "forecast": "Tomorrow, July 24, 2025, Delhi will experience partly cloudy skies with a low chance of rain (5%). Temperatures will range from 28°C to 36°C, and humidity will be around 74%.",
        "critical_alerts": [
            "While the forecast for July 24, 2025, indicates a low chance of rain, Delhi is in its monsoon season, and the extended forecast predicts increasing chances of thunderstorms and heavy rainfall later in the week, which poses a risk of waterlogging and related issues for fields. [2, 3]"
        ],
        "recommendations": [
            "Wheat: The weather for July 24, 2025, is favorable for ongoing land preparation activities as wheat (sowing month: November) would have already been harvested. Ensure effective field drainage systems are in place or maintained to manage potential waterlogging from future monsoon rains, crucial for preparing the land for the upcoming sowing season.",
            "Mustard: With October as the sowing month, there is no standing mustard crop. Tomorrow's weather is suitable for initial field preparations. It is critical to establish or maintain proper drainage to prevent water accumulation from impending monsoon showers, ensuring the field is ready for timely sowing.",
            "Sugarcane: Sugarcane, sown in February, is in its active vegetative growth stage. The partly cloudy and warm conditions on July 24, 2025, are generally favorable for growth. However, given the ongoing monsoon season and the increasing likelihood of rain in the coming days, ensure excellent field drainage to prevent waterlogging, which can severely stress the crop. Continuously monitor for and manage humidity-driven diseases and pests."
        ]
    }
