import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_read_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user(client):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "dob": "01/01/2000",
        "ssn_last4": "1234",
        "phone": "5551234567",
        "email": "test@example.com",
        "zip_code": "76201"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Test"
    assert "id" in data
    return data["id"]

def test_analyze_endpoint(client):
    request_data = {
        "has_texas_license": False,
        "age": 25
    }
    response = client.post("/api/analyze", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_service"] == "Apply for first time Texas DL/Permit"
    assert data["confidence"] > 0.5
