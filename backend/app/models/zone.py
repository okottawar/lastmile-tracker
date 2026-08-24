from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Zone(Base):
    __tablename__ = "zones"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    areas = relationship("ZoneArea", back_populates="zone", cascade="all, delete-orphan")

class ZoneArea(Base):
    __tablename__ = "zone_areas"
    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), index=True, nullable=False, unique=True)
    area_name: Mapped[str] = mapped_column(String(150), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    zone = relationship("Zone", back_populates="areas")
