def make(client, **kw):
    body = {"title": "Pay invoice", "amount": "150.00", "due_date": "2026-11-10", **kw}
    r = client.post("/tasks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get(client):
    t = make(client)
    assert t["status"] == "open" and t["amount"] == "150.00"
    assert client.get(f"/tasks/{t['id']}").json()["title"] == "Pay invoice"


def test_validation(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "amount": -1}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "status": "weird"}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "due_date": "not-a-date"}).status_code == 422


def test_list_filters(client):
    make(client, title="Old", due_date="2020-01-01")
    make(client, title="Done", status="done")
    make(client, title="Future", due_date="2999-01-01")
    assert len(client.get("/tasks").json()) == 3
    assert [t["title"] for t in client.get("/tasks?status=done").json()] == ["Done"]
    assert [t["title"] for t in client.get("/tasks?overdue=true").json()] == ["Old"]
    assert [t["title"] for t in client.get("/tasks?q=fut").json()] == ["Future"]


def test_update(client):
    t = make(client)
    r = client.patch(f"/tasks/{t['id']}", json={"status": "done"})
    assert r.json()["status"] == "done" and r.json()["title"] == "Pay invoice"
    assert client.patch(f"/tasks/{t['id']}", json={"status": "bad"}).status_code == 422


def test_delete_and_404(client):
    t = make(client)
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.get(f"/tasks/{t['id']}").status_code == 404
    assert client.delete("/tasks/999").status_code == 404
