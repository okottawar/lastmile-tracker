from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.order import Order, OrderStatusHistory
from app.models.enums import OrderStatus

TERMINAL_STATUSES={OrderStatus.DELIVERED,OrderStatus.CANCELLED}
VALID_TRANSITIONS={
 OrderStatus.CREATED:{OrderStatus.ASSIGNED,OrderStatus.CANCELLED},
 OrderStatus.ASSIGNED:{OrderStatus.PICKED_UP,OrderStatus.CANCELLED},
 OrderStatus.PICKED_UP:{OrderStatus.IN_TRANSIT,OrderStatus.CANCELLED},
 OrderStatus.IN_TRANSIT:{OrderStatus.OUT_FOR_DELIVERY,OrderStatus.CANCELLED},
 OrderStatus.OUT_FOR_DELIVERY:{OrderStatus.DELIVERED,OrderStatus.FAILED,OrderStatus.CANCELLED},
 OrderStatus.FAILED:{OrderStatus.RESCHEDULED,OrderStatus.CANCELLED},
 OrderStatus.RESCHEDULED:{OrderStatus.ASSIGNED,OrderStatus.CANCELLED},
 OrderStatus.DELIVERED:set(),OrderStatus.CANCELLED:set()
}

async def apply_status_change(db: AsyncSession, order: Order, new_status: OrderStatus, actor_id: int|None, actor_role: str|None, note: str|None=None, is_admin_override: bool=False):
    if not is_admin_override and new_status not in VALID_TRANSITIONS.get(order.status,set()):
        raise HTTPException(status_code=400, detail=f"Invalid transition from '{order.status.value}' to '{new_status.value}'. Allowed next states: {[s.value for s in VALID_TRANSITIONS.get(order.status,set())] or 'none (terminal state)'}")
    order.status=new_status
    db.add(order)
    db.add(OrderStatusHistory(order_id=order.id,status=new_status,actor_id=actor_id,actor_role=actor_role,note=note))
    await db.flush()
    return order
