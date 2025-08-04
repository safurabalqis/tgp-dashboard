import time
from main import app

def test_impact_route_response():
    client = app.test_client()

    start_time = time.time()
    response = client.get('/environment')
    end_time = time.time()

    duration = end_time - start_time

    # ✅ Response code must be 200
    assert response.status_code == 200

    # ✅ Check content if expected (optional)
    # assert b"Some expected content" in response.data

    # ✅ Response time should be under 1 second
    print(f"/impact response time: {duration:.4f} seconds")
    assert duration < 1.0
