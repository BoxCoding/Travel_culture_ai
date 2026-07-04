def test_recommendations_returns_llm_shaped_response(client, mock_gemini):
    res = client.post(
        "/api/recommendations",
        json={
            "interests": ["heritage", "architecture"],
            "budget": "mid-range",
            "duration_days": 5,
            "region": "Asia",
            "travel_style": "slow travel",
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["summary"]
    assert data["attractions"][0]["name"] == "Hawa Mahal"
    assert data["hidden_gems"][0]["name"] == "Panna Meena ka Kund"


def test_recommendations_builds_catalog_from_firestore(client, mock_gemini):
    """The recommendation prompt is only as good as the catalog we hand the LLM --
    make sure it's actually built from the seeded Firestore destinations, not empty."""
    client.post("/api/recommendations", json={"interests": ["food"]})

    assert mock_gemini["recommendations"].called
    _, kwargs = mock_gemini["recommendations"].call_args
    catalog = kwargs["catalog"]
    assert len(catalog) >= 1
    assert any(d["name"] == "Jaipur" for d in catalog)
    assert kwargs["interests"] == ["food"]


def test_recommendations_region_filter_narrows_catalog(client, mock_gemini):
    client.post("/api/recommendations", json={"interests": [], "region": "Asia"})
    _, kwargs = mock_gemini["recommendations"].call_args
    assert all(d["region"] == "Asia" for d in kwargs["catalog"])


def test_recommendations_unknown_region_falls_back_to_full_catalog(client, mock_gemini):
    """No destination matches 'Antarctica' -- should fall back to the full catalog
    rather than sending the LLM an empty list."""
    client.post("/api/recommendations", json={"interests": [], "region": "Antarctica"})
    _, kwargs = mock_gemini["recommendations"].call_args
    assert len(kwargs["catalog"]) >= 1


def test_recommendations_missing_interests_defaults_to_empty_list(client, mock_gemini):
    res = client.post("/api/recommendations", json={})
    assert res.status_code == 200


def test_recommendations_does_not_require_auth(client, mock_gemini):
    """Per CONTRACT.md, /api/recommendations has optional auth -- anonymous browsing works."""
    res = client.post("/api/recommendations", json={"interests": ["food"]})
    assert res.status_code == 200


def test_recommendations_surfaces_gemini_failure_as_clean_502(client, mock_gemini):
    mock_gemini["recommendations"].side_effect = RuntimeError("RESOURCE_EXHAUSTED: quota depleted")

    res = client.post("/api/recommendations", json={"interests": ["food"]})

    assert res.status_code == 502
    assert "RESOURCE_EXHAUSTED" in res.json()["detail"]


def test_recommendations_malformed_body_returns_422(client, mock_gemini):
    res = client.post("/api/recommendations", json={"interests": "not-a-list"})
    assert res.status_code == 422
