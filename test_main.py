import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, Base, FruitModel, get_db, _fruit_response

TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _get_test_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _get_test_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add_all([
        FruitModel(name="Apple",  price=1.20, in_season=True),
        FruitModel(name="Banana", price=0.80, in_season=True),
        FruitModel(name="Orange", price=1.00, in_season=False),
    ])
    db.commit()
    db.close()
    yield


def test_fruit_response():
    fruit = FruitModel(id=4, name="Mango", price=3.0, in_season=True)
    result = _fruit_response(fruit)
    assert result == {"id": 4, "name": "Mango", "price": 3.0, "in_season": True}


def test_list_fruits():
    response = client.get("/fruits")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_cheapest_fruit():
    response = client.get("/fruits/cheapest")
    assert response.status_code == 200
    assert response.json()["name"] == "Banana"
    assert response.json()["price"] == 0.80


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
    db = TestingSession()
    db.query(FruitModel).delete()
    db.commit()
    db.close()
    response = client.get("/fruits/cheapest")
    assert response.status_code == 404
