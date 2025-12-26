import pytest
from app.main import app

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}  # Adjust based on your actual root response

# Add more tests as needed for your application functionality