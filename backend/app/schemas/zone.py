from pydantic import BaseModel, Field
from app.models.enums import OrderType, ZoneRelation
class ZoneCreate(BaseModel): name:str; description:str|None=None
class ZoneOut(BaseModel):
    id:int; name:str; description:str|None
    class Config: from_attributes=True
class ZoneAreaCreate(BaseModel): zone_id:int; pincode:str; area_name:str|None=None; city:str|None=None
class ZoneAreaOut(BaseModel):
    id:int; zone_id:int; pincode:str; area_name:str|None; city:str|None
    class Config: from_attributes=True
class RateCardCreate(BaseModel):
    origin_zone_id:int; dest_zone_id:int; order_type:OrderType; base_price:float=Field(ge=0); price_per_kg:float=Field(ge=0); min_chargeable_weight_kg:float=Field(gt=0)
class RateCardOut(BaseModel):
    id:int; origin_zone_id:int; dest_zone_id:int; order_type:OrderType; relation:ZoneRelation; base_price:float; price_per_kg:float; min_chargeable_weight_kg:float
    class Config: from_attributes=True
class CODRuleCreate(BaseModel): order_type:OrderType; flat_fee:float=Field(ge=0); percent_of_order:float=Field(ge=0)
class CODRuleOut(BaseModel):
    id:int; order_type:OrderType; flat_fee:float; percent_of_order:float
    class Config: from_attributes=True
