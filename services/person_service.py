from sqlmodel import select, delete, or_

from db.models import Person, Settlement, Item, ItemConsumer
from db.database import get_session
from services.calculation_service import (
    recalculate_item_consumers,
)
from services.cache_service import clear_cache
import streamlit as st


def create_person(name: str):
    with get_session() as session:
        person = Person(name=name.strip())
        session.add(person)
        session.flush()
        session.refresh(person)
        clear_cache()
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


def delete_person(person_id: int) -> bool:
    with get_session() as session:
        person = session.get(Person, person_id)
        if person is None:
            return False

        # 1. Settlements direkt löschen
        session.exec(
            delete(Settlement).where(
                or_(
                    Settlement.from_payer_id == person_id,
                    Settlement.to_payer_id == person_id,
                )
            )
        )

        # 2. Alle Consumptions der Person holen, um zu wissen, welche Items wir später neu berechnen müssen
        consumptions = session.exec(
            select(ItemConsumer).where(ItemConsumer.user_id == person_id)
        ).all()

        items_to_recalculate = set()
        for c in consumptions:
            items_to_recalculate.add(c.item_id)

        # 3. Alle Items finden, die DIESER Person gehören
        owned_items = session.exec(select(Item).where(Item.buyer_id == person_id)).all()
        owned_item_ids = [item.id for item in owned_items]

        # 4. JETZT DIE LÖSCHUNGEN IN DER RICHTIGEN REIHENFOLGE ERZWINGEN:

        # A) Zuerst alle Consumer-Einträge entfernen, die zu den Items der Person gehören...
        if owned_item_ids:
            session.exec(
                delete(ItemConsumer).where(ItemConsumer.item_id.in_(owned_item_ids))  # type: ignore
            )

        session.exec(
            delete(ItemConsumer).where(ItemConsumer.user_id == person_id)  # type: ignore
        )

        if owned_item_ids:
            session.exec(
                delete(Item).where(Item.id.in_(owned_item_ids))  # type: ignore
            )

        # Entferne die gelöschten Items aus unserer Neuberechnungs-Liste
        for o_id in owned_item_ids:
            items_to_recalculate.discard(o_id)

        # 5. Die Datenbank anweisen, die Löschungen jetzt durchzuführen
        session.flush()

        # 6. Übrig gebliebene Items neu berechnen (da nun eine Person fehlt)
        for item_id in items_to_recalculate:
            recalculate_item_consumers(item_id)

        # 7. Als allerletztes die Person selbst löschen
        session.delete(person)

        session.commit()
        clear_cache()
        return True
