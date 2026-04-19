import pytest
from fastapi.testclient import TestClient

from main import app, _fruit_response

@pytest.fixture(autouse=True)
def reset_fruits_api():
    import main
    original_fruits = {
        1: {"name": "Apple", "price": 1.20, "in_season": True},
        2: {"name": "Banana", "price": 0.80, "in_season": True},
        3: {"name": "Orange", "price": 1.00, "in_season": False},
    }
    main.FRUITS.clear()
    main.FRUITS.update(original_fruits)
    main._next_id = 4
    yield

client = TestClient(app)

def test_fruit_response():
    data = {"name": "Mango", "price": 3, "in_season": True}
    result = _fruit_response(4, data)
    assert result == {"id": 4, "name": "Mango", "price": 3, "in_season": True}

def test_list_fruits():
    response = client.get("/fruits")
    assert response.status_code == 200
    fruits = response.json()
    assert len(fruits) == 3

def test_get_cheapest_fruit():
    response = client.get("/fruits/cheapest")
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Banana", "price": 0.80, "in_season": True}

def test_list_fruits_in_season_true():
    response = client.get("/fruits?in_season=true")
    assert response.status_code == 200
    fruits = response.json()
    assert all(f["in_season"] is True for f in fruits)
    assert len(fruits) == 2

def test_list_fruits_in_season_false():
    response = client.get("/fruits?in_season=false")
    assert response.status_code == 200
    fruits = response.json()
    assert all(f["in_season"] is False for f in fruits)
    assert len(fruits) == 1

def test_get_fruit_not_found():
    response = client.get("/fruits/9999")
    assert response.status_code == 404

def test_post_fruit_invalid_body():
    response = client.post("/fruits", json={"price": "not-a-number"})
    assert response.status_code == 422

def test_put_fruit_not_found():
    response = client.put("/fruits/9999", json={"price": 1.0})
    assert response.status_code == 404

def test_delete_fruit_not_found():
    response = client.delete("/fruits/9999")
    assert response.status_code == 404

def test_cheapest_fruit_no_fruits():
    import main
    main.FRUITS.clear()
    response = client.get("/fruits/cheapest")
    assert response.status_code == 404

