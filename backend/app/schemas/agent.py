from pydantic import BaseModel, Field
from app.models.enums import AgentAvailability
class AgentCreate(BaseModel):
    name:str; email:str; phone:str|None=None; password:str=Field(min_length=8); home_zone_id:int|None=None; max_active_orders:int=Field(default=5,gt=0)
class AgentUpdate(BaseModel):
    availability:AgentAvailability|None=None; home_zone_id:int|None=None; current_lat:float|None=None; current_lng:float|None=None; max_active_orders:int|None=None
class AgentOut(BaseModel):
    id:int; user_id:int; home_zone_id:int|None; availability:AgentAvailability; current_lat:float|None; current_lng:float|None; max_active_orders:int
    class Config: from_attributes=True
