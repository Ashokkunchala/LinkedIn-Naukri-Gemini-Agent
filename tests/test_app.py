# ruff: noqa: E402
import os
import tempfile

with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
    database_path = tmp.name
os.environ["DATABASE_PATH"] = database_path
os.environ["APP_API_KEY"] = "test-key"

from fastapi.testclient import TestClient
from career_agent.db import init_db
from career_agent.main import app

init_db()  # TestClient isn't used as a context manager, so initialize the isolated test DB explicitly.
client = TestClient(app)
H = {"X-API-Key": "test-key"}

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["external_platform_actions"] == "disabled"

def test_monitor_is_honest_and_five_minutes():
    r = client.get("/api/monitor/status")
    assert r.status_code == 200
    assert r.json()["interval_seconds"] >= 300
    assert r.json()["active"] is False

def test_job_score():
    r = client.post("/api/jobs", headers=H, json={
        "title": "Engineer", "description": "Kubernetes AWS Terraform",
        "skills": ["Kubernetes", "AWS", "Go"]
    })
    assert r.status_code == 200 and r.json()["fit_score"] == 67

def test_approval_is_record_only():
    a = client.post("/api/approvals", headers=H, json={
        "action_type": "submit_application", "target": "Example role", "payload": {}
    }).json()
    d = client.post(f"/api/approvals/{a['id']}/decision", headers=H, json={"decision": "approve"})
    assert d.status_code == 200 and d.json()["external_action_executed"] is False

def test_decision_once():
    a = client.post("/api/approvals", headers=H, json={
        "action_type": "edit_profile", "target": "headline", "payload": {}
    }).json()
    p = f"/api/approvals/{a['id']}/decision"
    assert client.post(p, headers=H, json={"decision": "reject"}).status_code == 200
    assert client.post(p, headers=H, json={"decision": "approve"}).status_code == 409

def test_short_description_rejected():
    r = client.post("/api/jobs", headers=H, json={"title": "X", "description": "tiny"})
    assert r.status_code == 422
