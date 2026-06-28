from sqlmodel import SQLModel, Field, create_engine, Session
from typing import List, Optional
from enum import Enum
from contextlib import contextmanager
from datetime import datetime, timezone


class AufteilungsModus(str, Enum):
    GLEICHMAESSIG = "Gleichmäßig"
    PROZENT = "Prozent"
    STUECKZAHL = "Stückzahl"


class Einheit(str, Enum):
    STUECK = "Stück"
    GRAMM = "Gramm"
    MILILITER = "Mililiter"


SQLModel.metadata.clear()


class Person(SQLModel, table=True):
    __tablename__: str = "persons"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)


class Item(SQLModel, table=True):
    __tablename__: str = "items"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    gesamtbetrag_cent: int
    menge: float | None = None
    einheit: Einheit | None = None
    buyer_id: int = Field(foreign_key="persons.id")


class ItemConsumer(SQLModel, table=True):
    __tablename__: str = "item_consumers"
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id")
    user_id: int = Field(foreign_key="persons.id")
    modus: AufteilungsModus
    wert: float


class Settlement(SQLModel, table=True):
    __tablename__: str = "settlements"

    id: Optional[int] = Field(default=None, primary_key=True)

    from_payer_id: int = Field(foreign_key="persons.id")
    to_payer_id: int = Field(foreign_key="persons.id")

    amount_cent: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    note: str | None = None
