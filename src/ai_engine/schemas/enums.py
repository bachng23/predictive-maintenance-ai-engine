from enum import StrEnum

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

class ActionType(StrEnum):
    CONTINUE_MONITORING = "continue_monitoring"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    REDUCE_LOAD_AND_INSPECT = "reduce_load_and_inspect"
    STOP_AND_ESCALATE = "stop_and_escalate"
    HUMAN_REVIEW_REQUIRED = "human_review_required"

class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    BLOCKED = "blocked"

