from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import require_admin
from app.core.security import hash_password
from app.models.user import User
from app.models.zone import Zone,ZoneArea
from app.models.rate_card import RateCard,CODSurchargeRule
from app.models.agent import Agent
from app.models.enums import UserRole,ZoneRelation
from app.schemas.zone import ZoneCreate,ZoneOut,ZoneAreaCreate,ZoneAreaOut,RateCardCreate,RateCardOut,CODRuleCreate,CODRuleOut
from app.schemas.agent import AgentCreate,AgentOut,AgentUpdate
router=APIRouter(prefix="/api/admin",tags=["admin"],dependencies=[Depends(require_admin)])
@router.post("/zones",response_model=ZoneOut,status_code=201)
async def create_zone(p:ZoneCreate,db:AsyncSession=Depends(get_db)):
    if (await db.execute(select(Zone).where(Zone.name==p.name))).scalar_one_or_none(): raise HTTPException(409,"Zone with this name already exists.")
    z=Zone(**p.model_dump());db.add(z);await db.commit();await db.refresh(z);return z
@router.get("/zones",response_model=list[ZoneOut])
async def zones(db:AsyncSession=Depends(get_db)): return (await db.execute(select(Zone))).scalars().all()
@router.post("/zone-areas",response_model=ZoneAreaOut,status_code=201)
async def add_area(p:ZoneAreaCreate,db:AsyncSession=Depends(get_db)):
    if not await db.get(Zone,p.zone_id): raise HTTPException(404,"Zone not found.")
    if (await db.execute(select(ZoneArea).where(ZoneArea.pincode==p.pincode))).scalar_one_or_none(): raise HTTPException(409,"Pincode already mapped to a zone.")
    a=ZoneArea(**p.model_dump());db.add(a);await db.commit();await db.refresh(a);return a
@router.get("/zone-areas",response_model=list[ZoneAreaOut])
async def areas(db:AsyncSession=Depends(get_db)): return (await db.execute(select(ZoneArea))).scalars().all()
@router.post("/rate-cards",response_model=RateCardOut,status_code=201)
async def create_rate(p:RateCardCreate,db:AsyncSession=Depends(get_db)):
    for zid in (p.origin_zone_id,p.dest_zone_id):
        if not await db.get(Zone,zid): raise HTTPException(404,f"Zone id {zid} not found.")
    if (await db.execute(select(RateCard).where(RateCard.origin_zone_id==p.origin_zone_id,RateCard.dest_zone_id==p.dest_zone_id,RateCard.order_type==p.order_type))).scalar_one_or_none(): raise HTTPException(409,"Rate card already exists for this lane + order type.")
    r=RateCard(**p.model_dump(),relation=ZoneRelation.INTRA if p.origin_zone_id==p.dest_zone_id else ZoneRelation.INTER);db.add(r);await db.commit();await db.refresh(r);return r
@router.get("/rate-cards",response_model=list[RateCardOut])
async def rates(db:AsyncSession=Depends(get_db)): return (await db.execute(select(RateCard))).scalars().all()
@router.put("/rate-cards/{rid}",response_model=RateCardOut)
async def update_rate(rid:int,p:RateCardCreate,db:AsyncSession=Depends(get_db)):
    r=await db.get(RateCard,rid)
    if not r: raise HTTPException(404,"Rate card not found.")
    for k,v in p.model_dump().items(): setattr(r,k,v)
    r.relation=ZoneRelation.INTRA if p.origin_zone_id==p.dest_zone_id else ZoneRelation.INTER;await db.commit();await db.refresh(r);return r
@router.delete("/rate-cards/{rid}",status_code=204)
async def delete_rate(rid:int,db:AsyncSession=Depends(get_db)):
    r=await db.get(RateCard,rid)
    if not r: raise HTTPException(404,"Rate card not found.")
    await db.delete(r);await db.commit()
@router.post("/cod-rules",response_model=CODRuleOut)
async def cod(p:CODRuleCreate,db:AsyncSession=Depends(get_db)):
    r=(await db.execute(select(CODSurchargeRule).where(CODSurchargeRule.order_type==p.order_type))).scalar_one_or_none()
    if r:r.flat_fee=p.flat_fee;r.percent_of_order=p.percent_of_order
    else:r=CODSurchargeRule(**p.model_dump());db.add(r)
    await db.commit();await db.refresh(r);return r
@router.get("/cod-rules",response_model=list[CODRuleOut])
async def cods(db:AsyncSession=Depends(get_db)): return (await db.execute(select(CODSurchargeRule))).scalars().all()
@router.post("/agents",response_model=AgentOut,status_code=201)
async def create_agent(p:AgentCreate,db:AsyncSession=Depends(get_db)):
    if (await db.execute(select(User).where(User.email==p.email))).scalar_one_or_none(): raise HTTPException(409,"Email already registered.")
    u=User(name=p.name,email=p.email,phone=p.phone,hashed_password=hash_password(p.password),role=UserRole.AGENT);db.add(u);await db.flush();a=Agent(user_id=u.id,home_zone_id=p.home_zone_id,max_active_orders=p.max_active_orders);db.add(a);await db.commit();await db.refresh(a);return a
@router.get("/agents",response_model=list[AgentOut])
async def agents(db:AsyncSession=Depends(get_db)): return (await db.execute(select(Agent))).scalars().all()
@router.patch("/agents/{aid}",response_model=AgentOut)
async def update_agent(aid:int,p:AgentUpdate,db:AsyncSession=Depends(get_db)):
    a=await db.get(Agent,aid)
    if not a: raise HTTPException(404,"Agent not found.")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(a,k,v)
    await db.commit();await db.refresh(a);return a
