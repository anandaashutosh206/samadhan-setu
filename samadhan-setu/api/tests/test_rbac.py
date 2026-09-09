def _make_challenge(client, token):
    r = client.post(
        "/api/v1/challenges",
        data={
            "title": "Illegal sand mining damaging riverbank in Sahibganj",
            "description": "Unregulated sand mining along the river is causing riverbank erosion and threatening nearby agricultural land and a village road.",
            "district": "Sahibganj",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_citizen_cannot_validate_challenge(client, citizen_token):
    cid = _make_challenge(client, citizen_token)
    r = client.post(f"/api/v1/challenges/{cid}/validate", headers={"Authorization": f"Bearer {citizen_token}"})
    assert r.status_code == 403


def test_govt_official_can_validate_challenge(client, citizen_token, govt_token):
    cid = _make_challenge(client, citizen_token)
    r = client.post(f"/api/v1/challenges/{cid}/validate", headers={"Authorization": f"Bearer {govt_token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "VALIDATED"


def test_citizen_cannot_patch_status(client, citizen_token):
    cid = _make_challenge(client, citizen_token)
    r = client.patch(
        f"/api/v1/challenges/{cid}/status",
        json={"status": "REJECTED"},
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert r.status_code == 403
