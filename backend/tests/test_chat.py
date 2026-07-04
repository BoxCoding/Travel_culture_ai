def test_chat_requires_auth(client):
    res = client.post("/api/chat", json={"message": "any hidden gems in Jaipur?"})
    assert res.status_code == 401


def test_chat_routes_intent_and_returns_reply(client, mock_gemini, auth_headers):
    res = client.post(
        "/api/chat",
        json={"message": "any hidden gems in Jaipur?"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["reply"] == "Jaipur has some wonderful hidden gems worth seeking out!"
    assert body["thread_id"]


def test_chat_preserves_thread_across_turns(client, mock_gemini, auth_headers):
    first = client.post("/api/chat", json={"message": "hi there"}, headers=auth_headers)
    thread_id = first.json()["thread_id"]

    second = client.post(
        "/api/chat",
        json={"message": "tell me more", "thread_id": thread_id},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["thread_id"] == thread_id


def test_chat_surfaces_gemini_failure_as_clean_502(client, mock_gemini, auth_headers):
    mock_gemini["classify_intent"].side_effect = RuntimeError("RESOURCE_EXHAUSTED: quota depleted")
    res = client.post("/api/chat", json={"message": "hi"}, headers=auth_headers)
    assert res.status_code == 502
    assert "RESOURCE_EXHAUSTED" in res.json()["detail"]
