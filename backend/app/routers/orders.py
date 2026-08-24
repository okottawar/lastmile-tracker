import random,string
from fastapi import APIRouter,Depends,HTTPException,status,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user,require_admin
from app.models.user import User
from app.models.agent import Agent
from app.models.order import Order,OrderStatusHistory
from app.models.enums import UserRole,OrderStatus,AgentAvailability
from app.schemas.order import OrderCreate,OrderOut,OrderDetailOut,ChargeEstimateRequest,ChargeEstimateOut,StatusUpdate,RescheduleRequest,AssignAgentRequest
from app.services.rate_engine import calculate_charge
from app.services.assignment_service import find_best_agent
from app.services.order_lifecycle import apply_status_change,TERMINAL_STATUSES
from app.services.notification_service import notify_status_change
router=APIRouter(prefix="/api/orders",tags=["orders"])
def _num(): return "LMT-"+"".join(random.choices(string.digits,k=8))
@router.post("/estimate",response_model=ChargeEstimateOut)
async def estimate(payload:ChargeEstimateRequest,db:AsyncSession=Depends(get_db)):
    b=await calculate_charge(db,**payload.model_dump()); return ChargeEstimateOut(pickup_zone=b.pickup_zone.name,drop_zone=b.drop_zone.name,relation=b.relation.value,volumetric_weight_kg=b.volumetric_weight_kg,actual_weight_kg=b.actual_weight_kg,chargeable_weight_kg=b.chargeable_weight_kg,base_charge=b.base_charge,weight_charge=b.weight_charge,cod_surcharge=b.cod_surcharge,total_charge=b.total_charge)
@router.post("",response_model=OrderOut,status_code=201)
async def create(payload:OrderCreate,current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    if current_user.role==UserRole.CUSTOMER: customer_id=current_user.id
    elif current_user.role==UserRole.ADMIN:
        if not payload.customer_id: raise HTTPException(400,"Admin must specify customer_id when creating an order.")
        customer=await db.get(User,payload.customer_id)
        if not customer or customer.role!=UserRole.CUSTOMER: raise HTTPException(404,"Customer not found.")
        customer_id=payload.customer_id
    else: raise HTTPException(403,"Only customers or admins can create orders.")
    b=await calculate_charge(db,**{k:v for k,v in payload.model_dump().items() if k!='customer_id'})
    order=Order(order_number=_num(),customer_id=customer_id,created_by_id=current_user.id,pickup_address=payload.pickup_address,pickup_pincode=payload.pickup_pincode,drop_address=payload.drop_address,drop_pincode=payload.drop_pincode,pickup_zone_id=b.pickup_zone.id,drop_zone_id=b.drop_zone.id,length_cm=payload.length_cm,breadth_cm=payload.breadth_cm,height_cm=payload.height_cm,actual_weight_kg=payload.actual_weight_kg,volumetric_weight_kg=b.volumetric_weight_kg,chargeable_weight_kg=b.chargeable_weight_kg,order_type=payload.order_type,payment_type=payload.payment_type,base_charge=b.base_charge,weight_charge=b.weight_charge,cod_surcharge=b.cod_surcharge,total_charge=b.total_charge,status=OrderStatus.CREATED); db.add(order); await db.flush(); db.add(OrderStatusHistory(order_id=order.id,status=OrderStatus.CREATED,actor_id=current_user.id,actor_role=current_user.role.value,note="Order created.")); await db.commit(); await db.refresh(order); customer=await db.get(User,customer_id); await notify_status_change(customer.email,customer.phone,order.order_number,OrderStatus.CREATED); return order
@router.get("",response_model=list[OrderOut])
async def list_orders(status_filter:OrderStatus|None=Query(None,alias="status"),zone_id:int|None=None,agent_id:int|None=None,current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    q=select(Order)
    if current_user.role==UserRole.CUSTOMER:q=q.where(Order.customer_id==current_user.id)
    elif current_user.role==UserRole.AGENT:
        a=(await db.execute(select(Agent).where(Agent.user_id==current_user.id))).scalar_one_or_none()
        if not a: raise HTTPException(404,"Agent profile not found.")
        q=q.where(Order.agent_id==a.id)
    if status_filter:q=q.where(Order.status==status_filter)
    if zone_id:q=q.where((Order.pickup_zone_id==zone_id)|(Order.drop_zone_id==zone_id))
    if agent_id:q=q.where(Order.agent_id==agent_id)
    return (await db.execute(q.order_by(Order.created_at.desc()))).scalars().all()
async def _get(db,id):
    o=(await db.execute(select(Order).options(selectinload(Order.tracking_history)).where(Order.id==id))).scalar_one_or_none()
    if not o: raise HTTPException(404,"Order not found.")
    return o
@router.get("/{order_id}",response_model=OrderDetailOut)
async def detail(order_id:int,current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    o=await _get(db,order_id)
    if current_user.role==UserRole.CUSTOMER and o.customer_id!=current_user.id: raise HTTPException(403,"Not authorized to view this order.")
    if current_user.role==UserRole.AGENT:
        a=(await db.execute(select(Agent).where(Agent.user_id==current_user.id))).scalar_one_or_none()
        if not a or o.agent_id!=a.id: raise HTTPException(403,"Not authorized to view this order.")
    return o
@router.post("/{order_id}/assign",response_model=OrderOut)
async def assign(order_id:int,payload:AssignAgentRequest,current_user:User=Depends(require_admin),db:AsyncSession=Depends(get_db)):
    o=await _get(db,order_id)
    if payload.agent_id:
        a=await db.get(Agent,payload.agent_id)
        if not a: raise HTTPException(404,"Agent not found.")
        if a.availability==AgentAvailability.OFFLINE: raise HTTPException(409,"Selected agent is offline.")
        active=await db.scalar(select(func.count(Order.id)).where(Order.agent_id==a.id,Order.status.in_([OrderStatus.ASSIGNED,OrderStatus.PICKED_UP,OrderStatus.IN_TRANSIT,OrderStatus.OUT_FOR_DELIVERY])))
        if active>=a.max_active_orders: raise HTTPException(409,"Selected agent is at maximum active-order capacity.")
    else:a=await find_best_agent(db,o.pickup_zone_id)
    o.agent_id=a.id; await apply_status_change(db,o,OrderStatus.ASSIGNED,current_user.id,"admin",f"Assigned to agent #{a.id}"+ (" (auto-assigned)" if not payload.agent_id else "")); await db.commit(); await db.refresh(o); c=await db.get(User,o.customer_id); await notify_status_change(c.email,c.phone,o.order_number,OrderStatus.ASSIGNED); return o
@router.patch("/{order_id}/status",response_model=OrderOut)
async def update_status(order_id:int,payload:StatusUpdate,current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    o=await _get(db,order_id); admin=current_user.role==UserRole.ADMIN
    if current_user.role==UserRole.AGENT:
        a=(await db.execute(select(Agent).where(Agent.user_id==current_user.id))).scalar_one_or_none()
        if not a or o.agent_id!=a.id: raise HTTPException(403,"You are not assigned to this order.")
    elif not admin: raise HTTPException(403,"Only agents or admins can update order status.")
    await apply_status_change(db,o,payload.status,current_user.id,current_user.role.value,payload.note,admin)
    if payload.status==OrderStatus.FAILED:o.failed_attempt_count+=1
    if payload.status in TERMINAL_STATUSES or payload.status==OrderStatus.FAILED:
        if o.agent_id:
            a=await db.get(Agent,o.agent_id); active=await db.scalar(select(func.count(Order.id)).where(Order.agent_id==a.id,Order.status.in_([OrderStatus.ASSIGNED,OrderStatus.PICKED_UP,OrderStatus.IN_TRANSIT,OrderStatus.OUT_FOR_DELIVERY])))
            if a and active==0:a.availability=AgentAvailability.AVAILABLE
    await db.commit(); await db.refresh(o); c=await db.get(User,o.customer_id); await notify_status_change(c.email,c.phone,o.order_number,payload.status); return o
@router.post("/{order_id}/reschedule",response_model=OrderOut)
async def reschedule(order_id:int,payload:RescheduleRequest,current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    o=await _get(db,order_id)
    if current_user.role==UserRole.CUSTOMER and o.customer_id!=current_user.id: raise HTTPException(403,"Not authorized to reschedule this order.")
    if o.status!=OrderStatus.FAILED: raise HTTPException(400,"Only failed deliveries can be rescheduled.")
    o.reschedule_date=payload.reschedule_date; await apply_status_change(db,o,OrderStatus.RESCHEDULED,current_user.id,current_user.role.value,payload.note or "Rescheduled delivery."); await db.commit(); c=await db.get(User,o.customer_id); await notify_status_change(c.email,c.phone,o.order_number,OrderStatus.RESCHEDULED)
    try:
        a=await find_best_agent(db,o.pickup_zone_id); o.agent_id=a.id; await apply_status_change(db,o,OrderStatus.ASSIGNED,current_user.id,current_user.role.value,f"Re-assigned to agent #{a.id} for rescheduled attempt."); await db.commit(); await notify_status_change(c.email,c.phone,o.order_number,OrderStatus.ASSIGNED)
    except HTTPException: await db.rollback()
    await db.refresh(o); return o
