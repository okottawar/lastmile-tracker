import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.agent import Agent
from app.models.order import Order
from app.models.enums import AgentAvailability, OrderStatus

def _haversine_km(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2): return float("inf")
    R=6371.0; dlat=math.radians(lat2-lat1); dlng=math.radians(lng2-lng1)
    a=math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R*2*math.asin(math.sqrt(a))

async def _active_order_count(db: AsyncSession, agent_id: int) -> int:
    active=[OrderStatus.ASSIGNED,OrderStatus.PICKED_UP,OrderStatus.IN_TRANSIT,OrderStatus.OUT_FOR_DELIVERY]
    return await db.scalar(select(func.count(Order.id)).where(Order.agent_id==agent_id, Order.status.in_(active)))

async def find_best_agent(db: AsyncSession, pickup_zone_id: int, pickup_lat=None, pickup_lng=None) -> Agent:
    result=await db.execute(select(Agent).where(Agent.availability==AgentAvailability.AVAILABLE))
    candidates=result.scalars().all()
    if not candidates: raise HTTPException(status_code=409, detail="No available delivery agents at the moment. Please assign manually or try again later.")
    scored=[]
    for agent in candidates:
        load=await _active_order_count(db, agent.id)
        if load >= agent.max_active_orders: continue
        zone_match=0 if agent.home_zone_id==pickup_zone_id else 1
        distance=_haversine_km(agent.current_lat,agent.current_lng,pickup_lat,pickup_lng)
        scored.append((zone_match,load,distance,agent))
    if not scored: raise HTTPException(status_code=409, detail="All available agents are at maximum capacity. Please assign manually or try again later.")
    scored.sort(key=lambda x:(x[0],x[1],x[2]))
    return scored[0][3]
