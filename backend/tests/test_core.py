import pytest
from app.services.rate_engine import calculate_volumetric_weight
from app.services.order_lifecycle import VALID_TRANSITIONS
from app.models.enums import OrderStatus

def test_volumetric_weight():
    assert calculate_volumetric_weight(50,50,50)==25

def test_status_machine():
    assert OrderStatus.ASSIGNED in VALID_TRANSITIONS[OrderStatus.CREATED]
    assert OrderStatus.DELIVERED in VALID_TRANSITIONS[OrderStatus.OUT_FOR_DELIVERY]
    assert OrderStatus.RESCHEDULED in VALID_TRANSITIONS[OrderStatus.FAILED]
    assert not VALID_TRANSITIONS[OrderStatus.DELIVERED]
