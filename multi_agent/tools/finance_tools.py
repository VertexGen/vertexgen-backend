import asyncio
from datetime import datetime

tool_log = []

async def financial_planner_tool(
    crop: str,
    area_acres: float,
    total_seed_cost: float,
    total_fertilizer_cost: float,
    total_labor_cost: float,
    expected_yield_kg: float,
    expected_price_per_kg: float
) -> dict:
    tool_log.append(("financial_planner_tool", datetime.utcnow().isoformat()))
    cost = total_seed_cost + total_fertilizer_cost + total_labor_cost
    income = expected_yield_kg * expected_price_per_kg
    return {
        "total_cost": cost,
        "expected_income": income,
        "net_profit": income - cost,
        "break_even_price": round(cost / expected_yield_kg, 2) if expected_yield_kg else 0
    }
