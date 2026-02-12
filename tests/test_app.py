import os
import sys
from urllib.parse import quote

# Ensure src is on path so we can import the FastAPI `app`
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(ROOT, "src")
sys.path.insert(0, SRC_PATH)

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_user_for_pytest@example.com"

    # Ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # If a previous test run left the email, remove it first
        client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")

    # Sign up
    signup = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Verify present
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    participants2 = resp2.json()[activity]["participants"]
    assert email in participants2

    # Unregister
    unregister = client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert unregister.status_code == 200
    assert "Unregistered" in unregister.json().get("message", "")

    # Verify removed
    resp3 = client.get("/activities")
    assert resp3.status_code == 200
    participants3 = resp3.json()[activity]["participants"]
    assert email not in participants3
