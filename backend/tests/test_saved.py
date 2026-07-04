def test_save_requires_auth(client, mock_gemini):
    gems = client.get("/api/destinations/jaipur/hidden-gems").json()
    res = client.post(
        f"/api/experiences/{gems[0]['id']}/save",
        json={"item_type": "hidden_gem", "destination_id": "jaipur"},
    )
    assert res.status_code == 401


def test_save_and_list_hidden_gem(client, mock_gemini, auth_headers):
    gems = client.get("/api/destinations/jaipur/hidden-gems").json()
    gem = gems[0]

    save_res = client.post(
        f"/api/experiences/{gem['id']}/save",
        json={"item_type": "hidden_gem", "destination_id": "jaipur"},
        headers=auth_headers,
    )
    assert save_res.status_code == 201
    saved = save_res.json()
    assert saved["item_type"] == "hidden_gem"
    assert saved["item"]["name"] == gem["name"]

    list_res = client.get("/api/me/saved", headers=auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert items[0]["item"]["name"] == gem["name"]


def test_save_invalid_item_type_returns_400(client, mock_gemini, auth_headers):
    res = client.post(
        "/api/experiences/whatever/save",
        json={"item_type": "not-a-real-type", "destination_id": "jaipur"},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_save_nonexistent_item_returns_404(client, mock_gemini, auth_headers):
    res = client.post(
        "/api/experiences/does-not-exist/save",
        json={"item_type": "hidden_gem", "destination_id": "jaipur"},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_saved_list_is_scoped_per_user(client, mock_gemini, bridge_token):
    gems = client.get("/api/destinations/jaipur/hidden-gems").json()
    gem = gems[0]

    alice_headers = {"Authorization": f"Bearer {bridge_token(sub='alice')}"}
    bob_headers = {"Authorization": f"Bearer {bridge_token(sub='bob')}"}

    client.post(
        f"/api/experiences/{gem['id']}/save",
        json={"item_type": "hidden_gem", "destination_id": "jaipur"},
        headers=alice_headers,
    )

    assert len(client.get("/api/me/saved", headers=alice_headers).json()) == 1
    assert len(client.get("/api/me/saved", headers=bob_headers).json()) == 0


def test_me_saved_requires_auth(client):
    res = client.get("/api/me/saved")
    assert res.status_code == 401
