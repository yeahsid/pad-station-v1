from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_pressure_transducer_datastream():
    response = client.get("/pressure/pressure_transducer_1/datastream")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain"
    assert response.text == "data1\ndata2\ndata3\n"  # Replace with expected datastream

    # Add more assertions as needed