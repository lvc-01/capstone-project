from enum import Enum

class UnitStatus(Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    CANCELLING = "Cancelling"
    PROBLEM = "Problem"
    UNAVAILABLE = "Unavailable"