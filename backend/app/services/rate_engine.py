from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from dataclasses import dataclass
from app.models.zone import Zone
from app.models.rate_card import RateCard, CODSurchargeRule
from app.models.enums import OrderType, PaymentType, ZoneRelation
from app.services.zone_service import resolve_zone_for_pincode

VOLUMETRIC_DIVISOR = 5000.0

@dataclass
class ChargeBreakdown:
    pickup_zone: Zone
    drop_zone: Zone
    relation: ZoneRelation
    volumetric_weight_kg: float
    actual_weight_kg: float
    chargeable_weight_kg: float
    base_charge: float
    weight_charge: float
    cod_surcharge: float
    total_charge: float

def calculate_volumetric_weight(length_cm: float, breadth_cm: float, height_cm: float) -> float:
    return round((length_cm * breadth_cm * height_cm) / VOLUMETRIC_DIVISOR, 3)

async def get_rate_card(db: AsyncSession, origin_zone_id: int, dest_zone_id: int, order_type: OrderType) -> RateCard:
    result = await db.execute(select(RateCard).where(and_(RateCard.origin_zone_id == origin_zone_id, RateCard.dest_zone_id == dest_zone_id, RateCard.order_type == order_type)))
    rate_card = result.scalar_one_or_none()
    if not rate_card:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No rate card configured for this lane (order_type={order_type.value}). Admin must configure a rate card for this origin-destination pair.")
    return rate_card

async def get_cod_rule(db: AsyncSession, order_type: OrderType) -> CODSurchargeRule | None:
    result = await db.execute(select(CODSurchargeRule).where(CODSurchargeRule.order_type == order_type))
    return result.scalar_one_or_none()

async def calculate_charge(db: AsyncSession, pickup_pincode: str, drop_pincode: str, length_cm: float, breadth_cm: float, height_cm: float, actual_weight_kg: float, order_type: OrderType, payment_type: PaymentType) -> ChargeBreakdown:
    pickup_zone = await resolve_zone_for_pincode(db, pickup_pincode)
    drop_zone = await resolve_zone_for_pincode(db, drop_pincode)
    relation = ZoneRelation.INTRA if pickup_zone.id == drop_zone.id else ZoneRelation.INTER
    volumetric_weight = calculate_volumetric_weight(length_cm, breadth_cm, height_cm)
    chargeable_weight = max(actual_weight_kg, volumetric_weight)
    rate_card = await get_rate_card(db, pickup_zone.id, drop_zone.id, order_type)
    chargeable_weight = max(chargeable_weight, rate_card.min_chargeable_weight_kg)
    base_charge = round(rate_card.base_price, 2)
    weight_charge = round(chargeable_weight * rate_card.price_per_kg, 2)
    cod_surcharge = 0.0
    if payment_type == PaymentType.COD:
        cod_rule = await get_cod_rule(db, order_type)
        if cod_rule:
            pct_amount = (cod_rule.percent_of_order / 100.0) * (base_charge + weight_charge)
            cod_surcharge = round(max(cod_rule.flat_fee, pct_amount), 2)
    total_charge = round(base_charge + weight_charge + cod_surcharge, 2)
    return ChargeBreakdown(pickup_zone, drop_zone, relation, volumetric_weight, actual_weight_kg, chargeable_weight, base_charge, weight_charge, cod_surcharge, total_charge)
