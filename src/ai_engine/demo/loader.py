from __future__ import annotations
import json
from pathlib import Path
from src.ai_engine.schemas.case import DecisionCase

class DemoCaseLoader:
    def __init__(self, base_path: str | Path = "src/ai_engine/demo/cases") -> None:
        self.base_path = Path(base_path)

    def load_case(self, filename: str) -> DecisionCase:
        file_path = self.base_path / filename

        with open(file_path, "r") as f:
            payload = json.load(f)
        return DecisionCase.model_validate(payload)