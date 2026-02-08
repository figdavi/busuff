from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from app.models import BaseORM
from typing import Generator, Annotated
import os

# DB config
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = "postgresql+psycopg2"

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False)


def init_db():
    BaseORM.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Cria uma nova sessão de banco de dados (SessionLocal),
    a entrega para o código chamador (yield) e garante que ela
    será fechada (db.close()) no bloco finally, mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]
