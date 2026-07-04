def test_storytelling_generates_and_returns_story(client, mock_gemini):
    res = client.post("/api/storytelling", json={"destination_id": "jaipur"})
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Dawn Over the Pink City"
    assert body["theme"] == "general"
    assert body["ai_generated"] is True


def test_storytelling_caches_by_theme(client, mock_gemini):
    client.post("/api/storytelling", json={"destination_id": "jaipur", "theme": "food"})
    client.post("/api/storytelling", json={"destination_id": "jaipur", "theme": "food"})
    assert mock_gemini["story"].call_count == 1

    # a different theme is a cache miss and should generate again
    client.post("/api/storytelling", json={"destination_id": "jaipur", "theme": "festivals"})
    assert mock_gemini["story"].call_count == 2


def test_storytelling_unknown_destination_returns_404(client, mock_gemini):
    res = client.post("/api/storytelling", json={"destination_id": "atlantis"})
    assert res.status_code == 404


def test_storytelling_missing_destination_id_returns_422(client, mock_gemini):
    res = client.post("/api/storytelling", json={})
    assert res.status_code == 422
