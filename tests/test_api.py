from fastapi.testclient import TestClient

from ai_engine.api.app import app
from ai_engine.demo.loader import DemoCaseLoader


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_decision_case_returns_final_state() -> None:
    case = DemoCaseLoader().load_case("bearing_warning")

    response = client.post(
        "/decision-cases/run",
        json=case.model_dump(mode="json"),
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["case"]["metadata"]["case_id"] == "case_002"
    assert payload["risk"] is not None
    assert payload["policy"] is not None
    assert payload["guardrail"] is not None
    assert payload["final_decision"] is not None
