"""
Database Layer for Catalog Microservice:
Uses PostgreSQL (via SQLAlchemy) for relational product inventory.
Features automatic table creation, initial data seeding, and local SQLite fallback.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Kubernetes Service DNS or local environment variable
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres-service")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "catalog_db")

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
FALLBACK_SQLITE_URL = "sqlite:///catalog.db"

DATA_JSON = os.path.join(Path(__file__).resolve().parent, "products.json")

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, default=4.5)
    brand = Column(String(100))
    description = Column(String(1000))
    tags = Column(JSON)  # Stores array of tags as JSON

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "price": self.price,
            "rating": self.rating,
            "brand": self.brand,
            "description": self.description,
            "tags": self.tags or []
        }


# Determine active database engine (PostgreSQL or local fallback)
engine = None
db_type = "unknown"

try:
    # Try connecting to PostgreSQL
    pg_engine = create_engine(POSTGRES_URL, connect_args={"connect_timeout": 3})
    with pg_engine.connect() as conn:
        pass
    engine = pg_engine
    db_type = "PostgreSQL"
    print(f"✅ Connected to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
except Exception:
    # Use SQLite for seamless local execution without requiring local Postgres daemon
    engine = create_engine(FALLBACK_SQLITE_URL, connect_args={"check_same_thread": False})
    db_type = "SQLite (Local Dev Mode - PostgreSQL Ready)"
    print(f"ℹ️ PostgreSQL not reachable at {POSTGRES_HOST}. Using {db_type}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes tables and seeds initial catalog if empty"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        count = session.query(ProductModel).count()
        if count == 0 and os.path.exists(DATA_JSON):
            with open(DATA_JSON, "r", encoding="utf-8") as f:
                items = json.load(f)
            for item in items:
                prod = ProductModel(
                    id=item["id"],
                    title=item["title"],
                    category=item["category"],
                    price=item["price"],
                    rating=item["rating"],
                    brand=item["brand"],
                    description=item["description"],
                    tags=item.get("tags", [])
                )
                session.add(prod)
            session.commit()
            print(f"✅ Seeded {len(items)} products into {db_type} database!")
    finally:
        session.close()


def get_all_products(category: str = None) -> List[Dict[str, Any]]:
    session = SessionLocal()
    try:
        query = session.query(ProductModel)
        if category and category.lower() != "all":
            query = query.filter(ProductModel.category.ilike(category))
        products = query.all()
        return [p.to_dict() for p in products]
    finally:
        session.close()


def get_product_by_id(product_id: int) -> Dict[str, Any]:
    session = SessionLocal()
    try:
        prod = session.query(ProductModel).filter(ProductModel.id == product_id).first()
        return prod.to_dict() if prod else None
    finally:
        session.close()


def get_all_categories() -> List[str]:
    session = SessionLocal()
    try:
        results = session.query(ProductModel.category).distinct().all()
        return sorted([r[0] for r in results])
    finally:
        session.close()
