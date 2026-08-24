from pydantic import BaseModel, Field
from datetime import datetime
from app.models.enums import OrderType, PaymentType, OrderStatus
class OrderCreate(BaseModel):
    customer_id:int|None=None; pickup_address:str; pickup_pincode:str; drop_address:str; drop_pincode:str
    length_cm:float=Field(gt=0); breadth_cm:float=Field(gt=0); height_cm:float=Field(gt=0); actual_weight_kg:float=Field(gt=0)
    order_type:OrderType; payment_type:PaymentType
class ChargeEstimateRequest(BaseModel):
    pickup_pincode:str; drop_pincode:str; length_cm:float=Field(gt=0); breadth_cm:float=Field(gt=0); height_cm:float=Field(gt=0); actual_weight_kg:float=Field(gt=0); order_type:OrderType; payment_type:PaymentType
class ChargeEstimateOut(BaseModel):
    pickup_zone:str; drop_zone:str; relation:str; volumetric_weight_kg:float; actual_weight_kg:float; chargeable_weight_kg:float; base_charge:float; weight_charge:float; cod_surcharge:float; total_charge:float
class StatusUpdate(BaseModel): status:OrderStatus; note:str|None=None
class RescheduleRequest(BaseModel): reschedule_date:datetime; note:str|None=None
class AssignAgentRequest(BaseModel): agent_id:int|None=None
class TrackingEventOut(BaseModel):
    status:OrderStatus; actor_role:str|None; note:str|None; created_at:datetime
    class Config: from_attributes=True
class OrderOut(BaseModel):
    id:int; order_number:str; customer_id:int; agent_id:int|None; pickup_address:str; pickup_pincode:str; drop_address:str; drop_pincode:str
    length_cm:float; breadth_cm:float; height_cm:float; actual_weight_kg:float; volumetric_weight_kg:float; chargeable_weight_kg:float
    order_type:OrderType; payment_type:PaymentType; base_charge:float; weight_charge:float; cod_surcharge:float; total_charge:float; status:OrderStatus; reschedule_date:datetime|None; failed_attempt_count:int; created_at:datetime; updated_at:datetime
    class Config: from_attributes=True
class OrderDetailOut(OrderOut):
    tracking_history:list[TrackingEventOut]=[]
