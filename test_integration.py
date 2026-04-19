import os, httpx, pytest

BASE_URL = "http://localhost:8000"

@pytest.fixture()
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_full_crud_lifecycle(client):
    #CREATE
    response = client.post("/fruits", json={"name": "Mango", "price": 3.0, "in_season": True})
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Mango"
    fruit_id = created["id"]

    #READ
    response = client.get(f"/fruits/{fruit_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Mango"

    #UPDATE
    response = client.put(f"/fruits/{fruit_id}", json={"price": 2.5})
    assert response.status_code == 200
    assert response.json()["price"] == 2.5
    assert response.json()["name"] == "Mango"

    #DELETE
    response = client.delete(f"/fruits/{fruit_id}")
    assert response.status_code == 204 # no response

    #READ again
    response = client.get(f"/fruits/{fruit_id}")
    assert response.status_code == 404

def test_cheapest_fruit(client):
    response = client.get("/fruits/cheapest")
    assert response.status_code == 200
    cheapest = response.json()

    all_fruits = client.get("/fruits")
    assert all_fruits.status_code == 200
    min_price = min(f["price"] for f in all_fruits.json())

    assert cheapest["price"] == min_price

def test_created_fruit_appears_in_list(client):
    response = client.post("/fruits", json={"name": "Kiwi", "price": 2.0, "in_season": True})
    assert response.status_code == 200
    created_id = response.json()["id"]

    all_fruits = client.get("/fruits")
    assert any(f["id"] == created_id for f in all_fruits.json())

