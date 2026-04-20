from __future__ import annotations

import json
from pathlib import Path

from ai_engine.schemas.case import DecisionCase


class DemoCaseNotFoundError(FileNotFoundError):
    """Raised when a named demo case cannot be found on disk."""


class DemoCaseLoader:
    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path) if base_path is not None else Path(__file__).resolve().parent / "cases"

    def list_cases(self) -> list[str]:
        return sorted(path.stem for path in self.base_path.glob("*.json"))

    def load_case(self, case_name: str) -> DecisionCase:
        file_path = self.base_path / f"{case_name}.json"
        if not file_path.exists():
            available_cases = ", ".join(self.list_cases()) or "none"
            raise DemoCaseNotFoundError(
                f"Demo case '{case_name}' was not found in {self.base_path}. "
                f"Available cases: {available_cases}."
            )

        with file_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return DecisionCase.model_validate(payload)
