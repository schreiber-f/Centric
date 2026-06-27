from typing import Sequence

from sqlmodel import select

from db.models import Person
from db.database import get_session


def create_person(name: str):
    with get_session() as session:
        person = Person(name=name.strip())
        session.add(person)
        session.flush()
        session.refresh(person)
        return (
            {
                "id": person.id,
                "name": person.name,
            }
            if person
            else None
        )


def get_all_persons():
    with get_session() as session:
        persons = session.exec(select(Person)).all()

        return [
            {
                "id": p.id,
                "name": p.name,
            }
            for p in persons
        ]


def get_person_by_id(person_id: int):
    with get_session() as session:
        person = session.get(Person, person_id)
        return (
            {
                "id": person.id,
                "name": person.name,
            }
            if person
            else None
        )
