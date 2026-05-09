from __future__ import annotations
import os

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fruits.db"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FruitModel(Base):
    __tablename__ = "fruits"
    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String(100), nullable=False)
    price    = Column(Float, default=0.0)
    in_season = Column(Boolean, default=True)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fruits API", version="0.3.0")


@app.on_event("startup")
def seed():
    db = SessionLocal()
    if db.query(FruitModel).count() == 0:
        db.add_all([
            FruitModel(name="Apple",  price=1.20, in_season=True),
            FruitModel(name="Banana", price=0.80, in_season=True),
            FruitModel(name="Orange", price=1.00, in_season=False),
        ])
        db.commit()
    db.close()


class FruitCreate(BaseModel):
    name: str
    price: float = 0.0
    in_season: bool = True


class FruitUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    in_season: bool | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _fruit_response(fruit: FruitModel) -> dict:
    return {"id": fruit.id, "name": fruit.name, "price": fruit.price, "in_season": fruit.in_season}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/fruits/cheapest")
def get_cheapest_fruit(db: Session = Depends(get_db)):
    fruit = db.query(FruitModel).order_by(FruitModel.price).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="No fruits")
    return _fruit_response(fruit)


@app.get("/fruits")
def list_fruits(
    in_season: bool = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(FruitModel)
    if in_season is not None:
        q = q.filter(FruitModel.in_season == in_season)
    return [_fruit_response(f) for f in q.all()]


@app.get("/fruits/{fruit_id}")
def get_fruit(fruit_id: int, db: Session = Depends(get_db)):
    fruit = db.query(FruitModel).filter(FruitModel.id == fruit_id).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return _fruit_response(fruit)


@app.post("/fruits")
def add_fruit(body: FruitCreate, db: Session = Depends(get_db)):
    fruit = FruitModel(name=body.name, price=body.price, in_season=body.in_season)
    db.add(fruit)
    db.commit()
    db.refresh(fruit)
    return _fruit_response(fruit)


@app.put("/fruits/{fruit_id}")
def update_fruit(fruit_id: int, body: FruitUpdate, db: Session = Depends(get_db)):
    fruit = db.query(FruitModel).filter(FruitModel.id == fruit_id).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    if body.name is not None:
        fruit.name = body.name
    if body.price is not None:
        fruit.price = body.price
    if body.in_season is not None:
        fruit.in_season = body.in_season
    db.commit()
    db.refresh(fruit)
    return _fruit_response(fruit)


@app.delete("/fruits/{fruit_id}", status_code=204)
def delete_fruit(fruit_id: int, db: Session = Depends(get_db)):
    fruit = db.query(FruitModel).filter(FruitModel.id == fruit_id).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    db.delete(fruit)
    db.commit()
