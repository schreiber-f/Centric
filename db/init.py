from sqlmodel import SQLModel
from db.database import engine


def init_db():
    SQLModel.metadata.clear()
    SQLModel.metadata.create_all(engine)
