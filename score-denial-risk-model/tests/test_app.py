from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_predict_denial_success():
    """
    Test successful prediction of denial risk.
    This test uses a common ICD-10 code for low back pain.
    """
    claim_data = {
        "cpt": "99213",
        "payer": "Blue Cross",
        "pos": "11",
        "duration": 20,
        "icd_count": 2,
        "modifier_count": 1,
        "has_modifier_25": 0,
        "procedures_count": 1,
        "past_denial_rate": 0.1,
        "primary_icd": "M54.5"
    }
    response = client.post("/predict", json=claim_data)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "predicted" in data
    assert "icd_ccs_id" in data
    assert isinstance(data["risk_score"], float)
    assert data["predicted"] in [0, 1]
    assert data["icd_ccs_id"] != "Unknown"

def test_predict_denial_unknown_icd():
    """
    Test prediction when the primary_icd is not found in the CCS mapping.
    """
    claim_data = {
        "cpt": "99213",
        "payer": "Aetna",
        "pos": "11",
        "duration": 15,
        "icd_count": 1,
        "modifier_count": 0,
        "has_modifier_25": 0,
        "procedures_count": 1,
        "past_denial_rate": 0.05,
        "primary_icd": "INVALIDCODE" # An unknown ICD code
    }
    response = client.post("/predict", json=claim_data)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "predicted" in data
    assert "icd_ccs_id" in data
    assert data["icd_ccs_id"] == "Unknown"

def test_predict_denial_invalid_input_schema():
    """
    Test the API's response to a request that doesn't match the Pydantic model.
    """
    claim_data = {
        "cpt": "99213",
        "payer": "Cigna",
        # Missing several required fields like 'pos', 'duration', etc.
    }
    response = client.post("/predict", json=claim_data)
    # FastAPI should return a 422 Unprocessable Entity for validation errors
    assert response.status_code == 422
