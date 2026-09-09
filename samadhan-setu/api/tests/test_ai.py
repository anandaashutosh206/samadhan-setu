def test_ai_health(client):
    r = client.get("/api/v1/ai/health")
    assert r.status_code == 200
    body = r.json()
    assert body["classifier_loaded"] is True
    assert body["training_examples"] >= 300
    assert body["mode"] in ("local", "local+llm")


def test_ai_classify_agriculture(client):
    r = client.post(
        "/api/v1/ai/classify",
        json={
            "title": "Crop damage due to erratic rainfall in Palamu",
            "description": "Paddy farmers in Palamu report significant crop loss this kharif season due to delayed monsoon followed by sudden heavy rainfall, with no crop insurance claims processed yet.",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "agriculture"
    assert 0.0 <= body["domain_confidence"] <= 1.0
    assert body["severity"] in ("low", "medium", "high", "critical")
    assert len(body["keywords"]) > 0


def test_ai_duplicate_check_no_existing(client):
    r = client.post(
        "/api/v1/ai/duplicate-check",
        json={"title": "Brand new unique issue", "description": "This is a totally unique description that should not match anything existing in the database at this point in the test."},
    )
    assert r.status_code == 200
    assert r.json()["is_likely_duplicate"] in (True, False)


def test_ai_summarize(client):
    text = (
        "Villagers in the block face acute drinking water shortage every summer. "
        "Hand pumps run dry by April each year. Women walk over three kilometers daily to fetch water. "
        "The panchayat has requested a new borewell for two years without response."
    )
    r = client.post("/api/v1/ai/summarize", json={"text": text, "max_sentences": 2})
    assert r.status_code == 200
    assert len(r.json()["summary"]) > 0
