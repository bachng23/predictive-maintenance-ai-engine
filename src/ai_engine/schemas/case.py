from pydantic import BaseModel, Field
from typing import Dict, List


class DecisionCase(BaseModel):
    case_id: str = Field(..., description="Unique identifier for the case")
    asset_type: str = Field(..., description="Type of the asset (bearing)")
    scenario_type: str = Field(..., description="Scenario type (bearing_healthy, etc.)")

    telemetry_summary: Dict[str, str] = Field(..., description="Summarized telemetry signals")
    operating_context: Dict[str, str] = Field(..., description="Operating context")

    reported_symptoms: List[str] = Field(default_factory=list, description="Reported symptoms")
    timestamp: str = Field(..., description="Case timestamp")


class NormalizedCase(BaseModel):
    asset_type: str = Field(..., description="Type of the asset (bearing)")

    detected_signals: Dict[str, str] = Field(..., description="Normalized signals")

    signal_quality: float = Field(..., ge=0.0, le=1.0, description="Signal quality (0-1)")
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Data completeness (0-1)")

    symptom_summary: str = Field(..., description="Summarized symptoms")
    operational_severity: str = Field(..., description="Severity level (low/medium/high)")