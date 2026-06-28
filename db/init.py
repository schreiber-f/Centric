from sqlmodel import SQLModel
from db.database import engine
from db.models import *


def init_db():
    SQLModel.metadata.clear()
    SQLModel.metadata.create_all(engine)
