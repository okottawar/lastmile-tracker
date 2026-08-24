from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.zone import Zone, ZoneArea

async def resolve_zone_for_pincode(db: AsyncSession, pincode: str) -> Zone:
    result = await db.execute(select(ZoneArea).where(ZoneArea.pincode == pincode))
    zone_area = result.scalar_one_or_none()
    if not zone_area:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Pincode '{pincode}' is not mapped to any serviceable zone. Admin must add this pincode to a zone before orders can be placed here.")
    result = await db.execute(select(Zone).where(Zone.id == zone_area.zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=500, detail="Zone data inconsistency detected.")
    return zone
