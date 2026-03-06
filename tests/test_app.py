import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities data before each test
    for activity in activities.values():
        activity["participants"] = []


def test_get_activities():
    # Arrange: nothing to set up

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_success():
    # Arrange: nothing to set up

    # Act
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "Signed up test@mergington.edu for Chess Club" in response.json()["message"]
    # Check participant added
    get_resp = client.get("/activities")
    assert "test@mergington.edu" in get_resp.json()["Chess Club"]["participants"]


def test_signup_duplicate():
    # Arrange
    client.post("/activities/Chess Club/signup?email=test@mergington.edu")

    # Act
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Arrange: nothing to set up

    # Act
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success():
    # Arrange
    client.post("/activities/Chess Club/signup?email=test@mergington.edu")

    # Act
    response = client.delete("/activities/Chess Club/unregister?email=test@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "Removed test@mergington.edu from Chess Club" in response.json()["message"]
    # Check participant removed
    get_resp = client.get("/activities")
    assert "test@mergington.edu" not in get_resp.json()["Chess Club"]["participants"]


def test_unregister_not_registered():
    # Arrange: nothing to set up

    # Act
    response = client.delete("/activities/Chess Club/unregister?email=ghost@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]


def test_unregister_activity_not_found():
    # Arrange: nothing to set up

    # Act
    response = client.delete("/activities/Nonexistent/unregister?email=test@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
