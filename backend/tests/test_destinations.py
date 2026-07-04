def test_list_destinations_returns_seeded_catalog(client):
    res = client.get("/api/destinations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(d["name"] == "Jaipur" for d in data)
    assert data[0]["id"] == "jaipur"  # slug id, not an integer


def test_list_destinations_filters_by_query(client):
    res = client.get("/api/destinations", params={"q": "Jaipur"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Jaipur"


def test_list_destinations_filters_by_region_case_insensitive(client):
    res = client.get("/api/destinations", params={"region": "asia"})
    assert res.status_code == 200
    assert all(d["region"] == "Asia" for d in res.json())


def test_get_destination_by_id(client):
    res = client.get("/api/destinations/jaipur")
    assert res.status_code == 200
    assert res.json()["name"] == "Jaipur"


def test_get_unknown_destination_returns_404(client):
    res = client.get("/api/destinations/atlantis")
    assert res.status_code == 404


def test_hidden_gems_generates_and_caches_on_first_request(client, mock_gemini):
    first = client.get("/api/destinations/jaipur/hidden-gems")
    assert first.status_code == 200
    gems = first.json()
    assert len(gems) == 2
    assert gems[0]["ai_generated"] is True
    assert gems[0]["destination_id"] == "jaipur"
    assert mock_gemini["hidden_gems"].call_count == 1

    second = client.get("/api/destinations/jaipur/hidden-gems")
    assert second.status_code == 200
    assert second.json() == gems
    # cached on the second request -- Gemini should not be called again
    assert mock_gemini["hidden_gems"].call_count == 1


def test_hidden_gems_unknown_destination_returns_404(client, mock_gemini):
    res = client.get("/api/destinations/atlantis/hidden-gems")
    assert res.status_code == 404
    mock_gemini["hidden_gems"].assert_not_called()


def test_heritage_generates_and_caches(client, mock_gemini):
    first = client.get("/api/destinations/jaipur/heritage")
    assert first.status_code == 200
    body = first.json()
    assert body["narrative"]
    assert body["theme"] == "__heritage__"
    assert mock_gemini["heritage"].call_count == 1

    second = client.get("/api/destinations/jaipur/heritage")
    assert second.json()["narrative"] == body["narrative"]
    assert mock_gemini["heritage"].call_count == 1


def test_events_generates_and_caches(client, mock_gemini):
    res = client.get("/api/destinations/jaipur/events")
    assert res.status_code == 200
    assert res.json()[0]["name"] == "Teej Festival"
    client.get("/api/destinations/jaipur/events")
    assert mock_gemini["events"].call_count == 1


def test_experiences_generates_and_caches(client, mock_gemini):
    res = client.get("/api/destinations/jaipur/experiences")
    assert res.status_code == 200
    body = res.json()[0]
    assert body["name"] == "Blue pottery workshop"
    # `type` from the LLM response is exposed as `category` on the wire, per CONTRACT.md
    assert body["category"] == "workshop"
    client.get("/api/destinations/jaipur/experiences")
    assert mock_gemini["experiences"].call_count == 1


def test_ai_content_surfaces_gemini_failure_as_clean_502(client, mock_gemini):
    mock_gemini["hidden_gems"].side_effect = RuntimeError("RESOURCE_EXHAUSTED: quota depleted")
    res = client.get("/api/destinations/jaipur/hidden-gems")
    assert res.status_code == 502
    assert "RESOURCE_EXHAUSTED" in res.json()["detail"]
