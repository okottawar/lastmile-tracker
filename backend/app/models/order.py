from sqlalchemy import String, Float, Integer, ForeignKey, Enum as SAEnum, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base
from app.models.enums import OrderType, PaymentType, OrderStatus

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    drop_address: Mapped[str] = mapped_column(Text, nullable=False)
    drop_pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    pickup_zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    drop_zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    length_cm: Mapped[float] = mapped_column(Float, nullable=False)
    breadth_cm: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    actual_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volumetric_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    chargeable_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType), nullable=False)
    payment_type: Mapped[PaymentType] = mapped_column(SAEnum(PaymentType), nullable=False)
    base_charge: Mapped[float] = mapped_column(Float, nullable=False)
    weight_charge: Mapped[float] = mapped_column(Float, nullable=False)
    cod_surcharge: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_charge: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), nullable=False, default=OrderStatus.CREATED)
    reschedule_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    customer = relationship("User", back_populates="orders_as_customer", foreign_keys=[customer_id])
    agent = relationship("Agent", back_populates="orders")
    pickup_zone = relationship("Zone", foreign_keys=[pickup_zone_id])
    drop_zone = relationship("Zone", foreign_keys=[drop_zone_id])
    tracking_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan", order_by="OrderStatusHistory.created_at")

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    order = relationship("Order", back_populates="tracking_history")
    actor = relationship("User")
