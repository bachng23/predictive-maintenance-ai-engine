import pytest

from ai_engine.demo.loader import DemoCaseLoader, DemoCaseNotFoundError
from ai_engine.schemas.enums import ScenarioType


def test_list_cases_returns_stable_case_names() -> None:
    loader = DemoCaseLoader()

    assert loader.list_cases() == [
        "bearing_critical",
        "bearing_healthy",
        "bearing_warning",
    ]


def test_load_case_by_case_name() -> None:
    loader = DemoCaseLoader()

    case = loader.load_case("bearing_healthy")

    assert case.case_id == "case_001"
    assert case.scenario_type is ScenarioType.BEARING_HEALTHY


def test_load_case_raises_structured_error_for_unknown_case() -> None:
    loader = DemoCaseLoader()

    with pytest.raises(DemoCaseNotFoundError, match="missing_case"):
        loader.load_case("missing_case")
