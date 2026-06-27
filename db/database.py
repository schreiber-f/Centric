from sqlmodel import create_engine, Session
from contextlib import contextmanager

DB_URL = "sqlite:///fairshare_v2.db"

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
