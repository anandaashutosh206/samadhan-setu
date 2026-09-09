from app import models
from app.database import SessionLocal


def _register(client, role, org_name=None):
    import os

    email = f"{role.lower()}_{os.urandom(4).hex()}@test.com"
    r = client.post(
        "/api/v1/auth/register",
        json={"name": role, "email": email, "password": "Demo@1234", "role": role, "org_name": org_name},
    )
    assert r.status_code == 201
    return r.json()


def _make_university(name="BIT Sindri", code=None):
    import os

    db = SessionLocal()
    uni = models.University(
        name=name,
        code=code or f"CODE{os.urandom(3).hex()}",
        district="Dhanbad",
        type="Govt Engg",
        disciplines=["civil engineering", "environmental engineering"],
        research_areas=["water resource management"],
        has_incubation=True,
        naac_grade="A",
        lat=23.79,
        lng=86.63,
        capacity_score=70,
        active_project_count=0,
    )
    db.add(uni)
    db.commit()
    db.refresh(uni)
    uni_id = uni.id
    db.close()
    return uni_id


def test_full_lifecycle(client):
    citizen = _register(client, "CITIZEN")
    govt = _register(client, "GOVT_OFFICIAL")
    uadmin = _register(client, "UNIVERSITY_ADMIN", org_name="BIT Sindri")
    uni_id = _make_university()

    r = client.post(
        "/api/v1/challenges",
        data={
            "title": "Drinking water scarcity in Ranchi villages",
            "description": "Several hamlets face acute drinking water shortage every summer as hand pumps run dry, forcing women to walk over 3km daily.",
            "district": "Ranchi",
            "beneficiaries_estimate": "900",
        },
        headers={"Authorization": f"Bearer {citizen['access_token']}"},
    )
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.post(f"/api/v1/challenges/{cid}/validate", headers={"Authorization": f"Bearer {govt['access_token']}"})
    assert r.status_code == 200 and r.json()["status"] == "VALIDATED"

    r = client.post(
        "/api/v1/routing/assign",
        json={"challenge_id": cid, "university_id": uni_id, "match_score": 82.5, "match_reasons": ["match"]},
        headers={"Authorization": f"Bearer {govt['access_token']}"},
    )
    assert r.status_code == 201
    routing_id = r.json()["id"]

    r = client.post(f"/api/v1/routing/{routing_id}/accept", headers={"Authorization": f"Bearer {uadmin['access_token']}"})
    assert r.status_code == 200 and r.json()["status"] == "ACCEPTED"

    r = client.post(
        "/api/v1/proposals",
        json={
            "challenge_id": cid, "university_id": uni_id, "title": "Solar-powered borewell network",
            "approach": "Deploy solar pumps", "methodology": "Phased rollout",
            "expected_outcome": "24x7 water access", "budget_estimate": 500000, "timeline_weeks": 16, "trl_level": 4,
        },
        headers={"Authorization": f"Bearer {uadmin['access_token']}"},
    )
    assert r.status_code == 201
    pid = r.json()["id"]

    r = client.patch(f"/api/v1/proposals/{pid}/status", json={"status": "APPROVED"}, headers={"Authorization": f"Bearer {govt['access_token']}"})
    assert r.status_code == 200 and r.json()["status"] == "APPROVED"

    r = client.get("/api/v1/projects")
    projects = [p for p in r.json() if p["proposal_id"] == pid]
    assert len(projects) == 1
    project_id = projects[0]["id"]

    r = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Site survey complete", "order": 1},
        headers={"Authorization": f"Bearer {uadmin['access_token']}"},
    )
    assert r.status_code == 201
    mid = r.json()["id"]

    r = client.post(f"/api/v1/projects/milestones/{mid}/approve", headers={"Authorization": f"Bearer {govt['access_token']}"})
    assert r.status_code == 200 and r.json()["status"] == "APPROVED"

    r = client.post("/api/v1/ip", json={"project_id": project_id, "type": "PATENT", "title": "Solar borewell controller"}, headers={"Authorization": f"Bearer {uadmin['access_token']}"})
    assert r.status_code == 201
    r = client.post("/api/v1/ip", json={"project_id": project_id, "type": "COPYRIGHT", "title": "Monitoring dashboard"}, headers={"Authorization": f"Bearer {uadmin['access_token']}"})
    assert r.status_code == 201

    r = client.get("/api/v1/ip/verify-chain")
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["total_records"] >= 2

    r = client.get("/api/v1/analytics/overview")
    assert r.status_code == 200
    assert r.json()["total_challenges"] >= 1

    r = client.get(f"/api/v1/reports/challenge/{cid}.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 500

    r = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {uadmin['access_token']}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
