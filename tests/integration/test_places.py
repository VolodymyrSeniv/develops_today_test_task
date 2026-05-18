BASE = "/api/v1/projects"


async def _create_project(client, name: str = "Test Project", places: list | None = None) -> dict:
    body: dict = {"name": name}
    if places:
        body["places"] = places
    r = await client.post(BASE, json=body)
    assert r.status_code == 201
    return r.json()


async def test_add_place_success(client):
    project = await _create_project(client)
    project_id = project["id"]

    r = await client.post(f"{BASE}/{project_id}/places", json={"external_id": 1001})
    assert r.status_code == 201
    data = r.json()
    assert data["external_id"] == 1001
    assert data["title"] == "Nighthawks"
    assert data["is_visited"] is False


async def test_add_place_project_not_found(client):
    r = await client.post(f"{BASE}/9999/places", json={"external_id": 1001})
    assert r.status_code == 404


async def test_add_place_invalid_artwork(client):
    project = await _create_project(client)
    r = await client.post(f"{BASE}/{project['id']}/places", json={"external_id": 9999})
    assert r.status_code == 422


async def test_add_place_duplicate(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    r = await client.post(f"{BASE}/{project['id']}/places", json={"external_id": 1001})
    assert r.status_code == 409


async def test_add_place_limit_exceeded(client):
    places = [{"external_id": 1001}, {"external_id": 1002}, {"external_id": 1003}]
    project = await _create_project(client, places=places)
    project_id = project["id"]

    for i in range(7):
        external_id = 2000 + i
        from app.application.ports.artwork_service import ArtworkData
        from tests.integration.conftest import KNOWN_ARTWORKS

        KNOWN_ARTWORKS[external_id] = ArtworkData(
            id=external_id, title=f"Art {i}", artist_display=None, image_url=None
        )
        r = await client.post(f"{BASE}/{project_id}/places", json={"external_id": external_id})
        if i < 7:
            assert r.status_code in (201, 422)

    r = await client.post(f"{BASE}/{project_id}/places", json={"external_id": 3000})
    assert r.status_code == 422


async def test_get_place_success(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    r = await client.get(f"{BASE}/{project_id}/places/{place_id}")
    assert r.status_code == 200
    assert r.json()["external_id"] == 1001


async def test_get_place_not_found(client):
    project = await _create_project(client)
    r = await client.get(f"{BASE}/{project['id']}/places/9999")
    assert r.status_code == 404


async def test_list_places(client):
    project = await _create_project(client, places=[{"external_id": 1001}, {"external_id": 1002}])
    project_id = project["id"]

    r = await client.get(f"{BASE}/{project_id}/places")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_list_places_filter_by_visited(client):
    project = await _create_project(client, places=[{"external_id": 1001}, {"external_id": 1002}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={"is_visited": True})

    r = await client.get(f"{BASE}/{project_id}/places", params={"is_visited": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["is_visited"] is True


async def test_list_places_project_not_found(client):
    r = await client.get(f"{BASE}/9999/places")
    assert r.status_code == 404


async def test_update_place_notes(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    r = await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={"notes": "Stunning!"})
    assert r.status_code == 200
    assert r.json()["notes"] == "Stunning!"


async def test_update_place_mark_visited(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    r = await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={"is_visited": True})
    assert r.status_code == 200
    assert r.json()["is_visited"] is True


async def test_all_places_visited_completes_project(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={"is_visited": True})

    r = await client.get(f"{BASE}/{project_id}")
    assert r.status_code == 200
    assert r.json()["is_completed"] is True


async def test_update_place_empty_body(client):
    project = await _create_project(client, places=[{"external_id": 1001}])
    project_id = project["id"]
    place_id = project["places"][0]["id"]

    r = await client.patch(f"{BASE}/{project_id}/places/{place_id}", json={})
    assert r.status_code == 422


async def test_update_place_not_found(client):
    project = await _create_project(client)
    r = await client.patch(f"{BASE}/{project['id']}/places/9999", json={"notes": "x"})
    assert r.status_code == 404
