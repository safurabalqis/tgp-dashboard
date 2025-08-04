import time
from main import app

def benchmark_route(path, expected_status=200, max_duration=1.0, expected_content=None):
    """
    Generic benchmark function for Flask routes.
    """
    client = app.test_client()

    start_time = time.time()
    response = client.get(path)
    end_time = time.time()

    duration = end_time - start_time

    print(f"{path} response time: {duration:.4f} seconds")

    # ✅ Status code check
    assert response.status_code == expected_status, f"{path} returned status {response.status_code}, expected {expected_status}"

    # ✅ Content check if provided
    if expected_content:
        assert expected_content.encode() in response.data, f"{path} does not contain expected content: {expected_content}"

    # ✅ Benchmark timing
    assert duration < max_duration, f"{path} took too long: {duration:.4f} seconds (limit: {max_duration}s)"

def test_environment_route():
    benchmark_route('/environment/', expected_status=200, max_duration=10.0)

def test_location_route():
    benchmark_route('/location', expected_status=200, max_duration=1.0)

def test_impact_route():
    benchmark_route('/impact', expected_status=200, max_duration=1.0)

def test_offense_route():
    benchmark_route('/offense/', expected_status=200, max_duration=10.0)
