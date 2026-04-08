import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

#Mock everything before importing the app
mock_model    = MagicMock()
mock_scaler   = MagicMock()
mock_encoders = MagicMock()

with patch.dict('sys.modules', {
    'torch': MagicMock(),
    'joblib': MagicMock(),
    'numpy': MagicMock(),
    'sklearn': MagicMock(),
    'sklearn.preprocessing': MagicMock(),
}):
    with patch('api.model._model',    mock_model), \
         patch('api.model.scaler',    mock_scaler), \
         patch('api.model.encoders',  mock_encoders), \
         patch('database.init_db',    return_value=None), \
         patch('database.SessionLocal', MagicMock()):

        from api.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "person_age":                  28,
    "person_income":               45000,
    "person_home_ownership":       "RENT",
    "person_emp_length":           3.0,
    "loan_intent":                 "PERSONAL",
    "loan_grade":                  "C",
    "loan_amnt":                   8000,
    "loan_int_rate":               13.5,
    "loan_percent_income":         0.18,
    "cb_person_default_on_file":   "N",
    "cb_person_cred_hist_length":  4
}

#Tests
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    with patch('api.main._model',    mock_model), \
         patch('api.main.scaler',    mock_scaler), \
         patch('api.main.encoders',  mock_encoders):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_predict_valid():
    mock_db = MagicMock()
    with patch('api.main.predict') as mock_predict, \
         patch('api.main.get_db', return_value=iter([mock_db])):
        mock_predict.return_value = {
            "risk_probability": 0.43,
            "decision":         "RISKY",
            "threshold":        0.4
        }
        response = client.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert "risk_probability" in data
        assert "decision"         in data
        assert "threshold"        in data
        assert data["decision"] in ["SAFE", "RISKY"]


def test_predict_invalid_missing_fields():
    response = client.post("/predict", json={"person_age": 28})
    assert response.status_code == 422


def test_predict_invalid_grade():
    with patch('api.main.predict') as mock_predict, \
         patch('api.main.get_db', return_value=iter([MagicMock()])):
        mock_predict.side_effect = ValueError("Unknown value 'Z' for 'loan_grade'")
        bad_payload = {**VALID_PAYLOAD, "loan_grade": "Z"}
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422


def test_metrics_shape():
    mock_db = MagicMock()
    mock_db.query.return_value.count.return_value = 10
    mock_db.query.return_value.filter.return_value.count.return_value = 3
    with patch('api.main.get_db', return_value=iter([mock_db])):
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_predictions" in data
        assert "risky"             in data
        assert "safe"              in data
        assert "risky_rate"        in data


def test_batch_predict():
    mock_db = MagicMock()
    with patch('api.main.predict') as mock_predict, \
         patch('api.main.get_db', return_value=iter([mock_db])):
        mock_predict.return_value = {
            "risk_probability": 0.2,
            "decision":         "SAFE",
            "threshold":        0.4
        }
        response = client.post("/predict/batch", json={"applicants": [VALID_PAYLOAD, VALID_PAYLOAD]})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["results"]) == 2