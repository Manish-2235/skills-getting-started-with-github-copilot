import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check that we have activities
    assert len(activities) > 0
    
    # Check activity structure
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First ensure the user isn't already signed up
    response = client.get("/activities")
    activities = response.json()
    if email in activities[activity_name]["participants"]:
        # Remove the user first
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify the user was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up a user who is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using an email we know exists
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_success():
    """Test successful unregistration from activity"""
    activity_name = "Chess Club"
    email = "test_unregister@mergington.edu"
    
    # First sign up the user
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Now unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify the user was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a user who isn't registered"""
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]