from enum import StrEnum


class ActionType(StrEnum):
    RUN = "RUN"
    RUN_WITH_MONITORING = "RUN_WITH_MONITORING"
    INSPECT = "INSPECT"
    PLAN_MAINTENANCE = "PLAN_MAINTENANCE"
    ESCALATE = "ESCALATE"
    CONTROLLED_STOP = "CONTROLLED_STOP"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PriorityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OperationalSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SignalTrend(StrEnum):
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


class DataQualityLevel(StrEnum):
    OK = "ok"
    WARNING = "warning"
    SEVERE = "severe"


class DriftStatus(StrEnum):
    NONE = "none"
    WARNING = "warning"
    SEVERE = "severe"


class CriticalityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PressureLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"


class CustomerPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeatureDirection(StrEnum):
    INCREASE_RISK = "increase_risk"
    DECREASE_RISK = "decrease_risk"
    NEUTRAL = "neutral"
