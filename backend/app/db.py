from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import get_database_url

SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def init_engine():
    database_url = get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal.configure(bind=engine)
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_engine()
    app.state.db_engine = engine
    try:
        yield
    finally:
        engine.dispose()


def get_db(request: Request):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
