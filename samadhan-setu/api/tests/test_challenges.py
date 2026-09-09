def test_create_and_get_challenge(client, citizen_token):
    r = client.post(
        "/api/v1/challenges",
        data={
            "title": "Primary health centre lacks doctor in Ranchi",
            "description": "The primary health centre serving multiple panchayats in Ranchi has been without a resident doctor for over a year, and essential medicines are frequently out of stock.",
            "district": "Ranchi",
            "beneficiaries_estimate": "500",
        },
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "AI_TRIAGED"
    assert body["domain"] == "healthcare"
    assert body["ai_confidence"] is not None
    assert isinstance(body["ai_keywords"], list)

    r2 = client.get(f"/api/v1/challenges/{body['id']}")
    assert r2.status_code == 200
    assert r2.json()["title"] == body["title"]


def test_create_challenge_requires_auth(client):
    r = client.post(
        "/api/v1/challenges",
        data={
            "title": "Some unauthenticated challenge",
            "description": "This should be rejected because there is no auth token attached to the request at all.",
            "district": "Ranchi",
        },
    )
    assert r.status_code == 401


def test_list_challenges_pagination(client, citizen_token):
    for i in range(3):
        client.post(
            "/api/v1/challenges",
            data={
                "title": f"Water scarcity issue number {i} in Dhanbad",
                "description": "Villagers in this area face acute drinking water shortage every summer as hand pumps run dry across the block.",
                "district": "Dhanbad",
            },
            headers={"Authorization": f"Bearer {citizen_token}"},
        )
    r = client.get("/api/v1/challenges", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["page_size"] == 2
    assert len(body["items"]) <= 2
    assert body["total"] >= 3


def test_upvote_toggle(client, citizen_token):
    r = client.post(
        "/api/v1/challenges",
        data={
            "title": "Street lighting absent in colony, Bokaro",
            "description": "A newly developed residential colony lacks street lighting, raising safety concerns for women and the elderly after dark.",
            "district": "Bokaro",
        },
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    cid = r.json()["id"]
    r1 = client.post(f"/api/v1/challenges/{cid}/upvote", headers={"Authorization": f"Bearer {citizen_token}"})
    assert r1.json()["upvote_count"] == 1
    r2 = client.post(f"/api/v1/challenges/{cid}/upvote", headers={"Authorization": f"Bearer {citizen_token}"})
    assert r2.json()["upvote_count"] == 0
