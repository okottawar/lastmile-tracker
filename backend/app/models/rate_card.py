from sqlalchemy import Float, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import OrderType, ZoneRelation

class RateCard(Base):
    __tablename__ = "rate_cards"
    __table_args__ = (UniqueConstraint("origin_zone_id", "dest_zone_id", "order_type", name="uq_rate_card_lane"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    origin_zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    dest_zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType), nullable=False)
    relation: Mapped[ZoneRelation] = mapped_column(SAEnum(ZoneRelation), nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price_per_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_chargeable_weight_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    origin_zone = relationship("Zone", foreign_keys=[origin_zone_id])
    dest_zone = relationship("Zone", foreign_keys=[dest_zone_id])

class CODSurchargeRule(Base):
    __tablename__ = "cod_surcharge_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType), unique=True, nullable=False)
    flat_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    percent_of_order: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
