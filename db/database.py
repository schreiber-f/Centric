from sqlmodel import create_engine, Session
from contextlib import contextmanager
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = st.secrets.get(
    "DATABASE_URL",
    os.getenv("DATABASE_URL"),
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
