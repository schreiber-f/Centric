from sqlmodel import create_engine, Session
from contextlib import contextmanager
import streamlit as st
import os
from dotenv import load_dotenv
from db.models import Person, Item, ItemConsumer, Settlement

load_dotenv()

DB_URL = st.secrets.get(
    "NEON_CONNECTION",
    os.getenv("NEON_CONNECTION"),
)

engine = create_engine(DB_URL, echo=False)


@contextmanager
def get_session():
    """Öffnet die Session, speichert bei Erfolg oder rollt bei Fehlern zurück."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
