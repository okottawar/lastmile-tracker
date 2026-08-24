import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"

class OrderType(str, enum.Enum):
    B2B = "B2B"
    B2C = "B2C"

class PaymentType(str, enum.Enum):
    PREPAID = "Prepaid"
    COD = "COD"

class OrderStatus(str, enum.Enum):
    CREATED = "Created"
    ASSIGNED = "Assigned"
    PICKED_UP = "Picked Up"
    IN_TRANSIT = "In Transit"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    FAILED = "Failed"
    RESCHEDULED = "Rescheduled"
    CANCELLED = "Cancelled"

class AgentAvailability(str, enum.Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    OFFLINE = "Offline"

class ZoneRelation(str, enum.Enum):
    INTRA = "intra"
    INTER = "inter"
