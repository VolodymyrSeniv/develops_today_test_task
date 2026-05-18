BASE = "/api/v1/projects"


async def test_health_check(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_create_project_minimal(client):
    r = await client.post(BASE, json={"name": "Paris Trip"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Paris Trip"
    assert data["is_completed"] is False
    assert data["places"] == []


async def test_create_project_with_description_and_date(client):
    r = await client.post(
        BASE,
        json={"name": "Rome Tour", "description": "Ancient history", "start_date": "2026-08-01"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "Ancient history"
    assert data["start_date"] == "2026-08-01"


async def test_create_project_with_places(client):
    r = await client.post(
        BASE,
        json={"name": "Art Tour", "places": [{"external_id": 1001}, {"external_id": 1002}]},
    )
    assert r.status_code == 201
    data = r.json()
    assert len(data["places"]) == 2
    titles = {p["title"] for p in data["places"]}
    assert "Nighthawks" in titles
    assert "American Gothic" in titles


async def test_create_project_invalid_artwork_id(client):
    r = await client.post(BASE, json={"name": "Bad", "places": [{"external_id": 9999}]})
    assert r.status_code == 422


async def test_create_project_duplicate_places(client):
    r = await client.post(
        BASE,
        json={"name": "Dup", "places": [{"external_id": 1001}, {"external_id": 1001}]},
    )
    assert r.status_code == 422


async def test_create_project_too_many_places(client):
    places = [{"external_id": 1001}] * 11
    r = await client.post(BASE, json={"name": "Overflow", "places": places})
    assert r.status_code == 422


async def test_get_project(client):
    create = await client.post(BASE, json={"name": "Berlin"})
    project_id = create.json()["id"]

    r = await client.get(f"{BASE}/{project_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Berlin"


async def test_get_project_not_found(client):
    r = await client.get(f"{BASE}/9999")
    assert r.status_code == 404


async def test_list_projects(client):
    await client.post(BASE, json={"name": "Project A"})
    await client.post(BASE, json={"name": "Project B"})

    r = await client.get(BASE)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_list_projects_filter_by_completed(client):
    await client.post(BASE, json={"name": "Active"})

    r = await client.get(BASE, params={"is_completed": "false"})
    assert r.status_code == 200
    assert all(not p["is_completed"] for p in r.json()["items"])


async def test_list_projects_pagination(client):
    for i in range(5):
        await client.post(BASE, json={"name": f"Project {i}"})

    r = await client.get(BASE, params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


async def test_update_project(client):
    create = await client.post(BASE, json={"name": "Old Name"})
    project_id = create.json()["id"]

    r = await client.put(f"{BASE}/{project_id}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


async def test_update_project_not_found(client):
    r = await client.put(f"{BASE}/9999", json={"name": "Ghost"})
    assert r.status_code == 404


async def test_update_project_empty_body(client):
    create = await client.post(BASE, json={"name": "Existing"})
    project_id = create.json()["id"]

    r = await client.put(f"{BASE}/{project_id}", json={})
    assert r.status_code == 422


async def test_delete_project(client):
    create = await client.post(BASE, json={"name": "To Delete"})
    project_id = create.json()["id"]

    r = await client.delete(f"{BASE}/{project_id}")
    assert r.status_code == 204

    r = await client.get(f"{BASE}/{project_id}")
    assert r.status_code == 404


async def test_delete_project_not_found(client):
    r = await client.delete(f"{BASE}/9999")
    assert r.status_code == 404


async def test_delete_project_with_visited_place_blocked(client):
    create = await client.post(
        BASE, json={"name": "Has Visited", "places": [{"external_id": 1001}]}
    )
    project_id = create.json()["id"]
    place_id = create.json()["places"][0]["id"]

    await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={"is_visited": True})

    r = await client.delete(f"{BASE}/{project_id}")
    assert r.status_code == 409
