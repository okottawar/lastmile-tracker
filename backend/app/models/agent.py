from sqlalchemy import Float, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import AgentAvailability

class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    home_zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=True)
    availability: Mapped[AgentAvailability] = mapped_column(SAEnum(AgentAvailability), nullable=False, default=AgentAvailability.AVAILABLE)
    current_lat: Mapped[float] = mapped_column(Float, nullable=True)
    current_lng: Mapped[float] = mapped_column(Float, nullable=True)
    max_active_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    user = relationship("User", back_populates="agent_profile")
    orders = relationship("Order", back_populates="agent")
    home_zone = relationship("Zone")
