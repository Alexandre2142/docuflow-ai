from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_reports_mock_provider():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "provider": "mock"}

def test_extract_returns_structured_requirement():
    response = client.post("/extract", json={
        "document_id": "demo-001",
        "text": "The facility shall maintain a record of each hazardous waste transfer."
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == "demo-001"
    assert len(payload["requirements"]) == 1
    requirement = payload["requirements"][0]
    assert requirement["topic"] == "Waste management"
    assert requirement["verification_status"] == "verified"
    assert requirement["source_quote"] in (
        "The facility shall maintain a record of each hazardous waste transfer."
    )
    assert payload["review_required"] is True  # mock limitations are disclosed

def test_extract_no_requirement_returns_review_warning():
    response = client.post("/extract", json={
        "document_id": "demo-002",
        "text": "This document describes the facility and its background."
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["requirements"] == []
    assert payload["review_required"] is True
    assert payload["warnings"]

def test_extract_rejects_empty_text():
    response = client.post("/extract", json={"text": ""})
    assert response.status_code == 422

def test_extract_rejects_unknown_request_fields():
    response = client.post("/extract", json={"text": "Test.", "unexpected": "no"})
    assert response.status_code == 422


def test_extract_does_not_match_keyword_inside_another_word():
    response = client.post("/extract", json={
        "document_id": "demo-mustard",
        "text": "The word mustard appears in the cafeteria inventory."
    })

    assert response.status_code == 200
    payload = response.json()
    assert payload["requirements"] == []


def test_extract_preserves_requirement_with_not_only_but_also():
    response = client.post("/extract", json={
        "document_id": "demo-not-only",
        "text": (
            "The facility is not only required to report spills, "
            "but also to investigate them."
        )
    })

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["requirements"]) == 1
    assert payload["requirements"][0]["source_quote"] == (
        "The facility is not only required to report spills, "
        "but also to investigate them."
    )
