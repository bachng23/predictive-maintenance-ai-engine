from pydantic import BaseModel, Field

from ai_engine.schemas.enums import AvailabilityStatus, CriticalityLevel, CustomerPriority, PressureLevel


class BusinessContext(BaseModel):
    asset_criticality: CriticalityLevel = Field(..., description="Criticality level of the asset in operations.")
    due_date_pressure: PressureLevel = Field(..., description="Pressure level caused by current due dates.")
    queue_length: int = Field(..., ge=0, description="Number of queued jobs affected by this asset.")
    production_backlog_level: PressureLevel = Field(..., description="Current backlog pressure level.")
    downtime_cost_per_hour: float = Field(..., ge=0.0, description="Estimated cost per hour of downtime.")
    lateness_penalty_estimate: float = Field(..., ge=0.0, description="Estimated penalty cost for late orders.")
    maintenance_cost_estimate: float = Field(..., ge=0.0, description="Estimated cost of planned maintenance.")
    emergency_failure_cost_estimate: float = Field(
        ...,
        ge=0.0,
        description="Estimated cost of emergency failure and unplanned repair.",
    )
    spare_availability: AvailabilityStatus = Field(..., description="Availability of required spare parts.")
    technician_availability: AvailabilityStatus = Field(..., description="Availability of maintenance technicians.")
    maintenance_window_available: bool = Field(..., description="Whether a maintenance window is currently available.")
    current_load_pct: float | None = Field(None, ge=0.0, le=100.0, description="Current machine load percentage.")
    order_id: str | None = Field(None, description="Primary order identifier affected by this decision.")
    customer_priority: CustomerPriority | None = Field(None, description="Priority level of the affected customer order.")
    shift_restriction: str | None = Field(None, description="Shift or staffing restriction relevant to maintenance.")
    business_notes: list[str] = Field(
        default_factory=list,
        description="Additional business context notes for the current case.",
    )
