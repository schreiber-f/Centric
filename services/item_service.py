from db.models import Item, ItemConsumer, AufteilungsModus, Einheit
from db.database import get_session
from services.person_service import get_all_persons
from services.calculation_service import recalculate_item_consumers
from services.cache_service import clear_cache
from sqlmodel import select
from typing import Optional
import streamlit as st


def create_item(
    name: str,
    betrag_cent: int,
    buyer_id: int,
    menge: Optional[float] = None,
    einheit: Optional[Einheit] = None,
):

    with get_session() as session:

        item = Item(
            name=name,
            gesamtbetrag_cent=betrag_cent,
            buyer_id=buyer_id,
            menge=menge,
            einheit=einheit,
        )
        session.add(item)
        session.flush()

        item_id = item.id

        if item_id is None:
            raise ValueError("Item-ID fehlt")

        modus: AufteilungsModus = AufteilungsModus.GLEICHMAESSIG
        consumers = get_all_persons()
        wert_pro_person = betrag_cent / len(consumers)

        for consumer in consumers:
            consumer_id = consumer["id"]

            if consumer_id is None:
                raise ValueError(f"Consumer id von {consumer["name"]} fehlt")

            session.add(
                ItemConsumer(
                    item_id=item_id,
                    user_id=consumer_id,
                    modus=modus,
                    wert=wert_pro_person,
                )
            )

        recalculate_item_consumers(item_id)

        session.refresh(item)
        clear_cache()
        return {
            "id": item.id,
            "name": item.name,
            "gesamtbetrag_cent": item.gesamtbetrag_cent,
            "buyer_id": item.buyer_id,
            "menge": item.menge,
            "einheit": item.einheit,
        }


@st.cache_data(show_spinner=False)
def get_consumer(
    consumer_id: int,
):

    with get_session() as session:
        consumer = session.get(
            ItemConsumer,
            consumer_id,
        )

        return (
            {
                "id": consumer.id,
                "item_id": consumer.item_id,
                "user_id": consumer.user_id,
                "modus": consumer.modus,
                "wert": consumer.wert,
            }
            if consumer
            else None
        )


@st.cache_data(show_spinner=False)
def get_item_consumers(
    item_id: int,
):

    with get_session() as session:

        consumers = session.exec(
            select(ItemConsumer).where(ItemConsumer.item_id == item_id)
        ).all()

        return [
            {
                "id": consumer.id,
                "item_id": consumer.item_id,
                "user_id": consumer.user_id,
                "modus": consumer.modus,
                "wert": consumer.wert,
            }
            for consumer in consumers
        ]


def update_consumer(
    consumer_id: int,
    modus: AufteilungsModus | None = None,
    wert: float | None = None,
    user_id: int | None = None,
):

    with get_session() as session:

        consumer = session.get(
            ItemConsumer,
            consumer_id,
        )

        if consumer is None:
            return None

        if modus is not None:
            consumer.modus = modus

        if wert is not None:
            consumer.wert = wert

        if user_id is not None:
            consumer.user_id = user_id

        session.add(consumer)
        session.flush()
        session.refresh(consumer)
        clear_cache()

        return {
            "id": consumer.id,
            "item_id": consumer.item_id,
            "user_id": consumer.user_id,
            "modus": consumer.modus,
            "wert": consumer.wert,
        }


def delete_consumer(
    consumer_id: int,
) -> bool:

    with get_session() as session:

        consumer = session.get(
            ItemConsumer,
            consumer_id,
        )

        if consumer is None:
            return False

        session.delete(consumer)
        clear_cache()

        return True


@st.cache_data(show_spinner=False)
def get_item(
    item_id: int,
):
    with get_session() as session:

        item = session.get(
            Item,
            item_id,
        )

        return (
            {
                "id": item.id,
                "name": item.name,
                "gesamtbetrag_cent": item.gesamtbetrag_cent,
                "buyer_id": item.buyer_id,
                "menge": item.menge,
                "einheit": item.einheit,
            }
            if item
            else None
        )


@st.cache_data(show_spinner=False)
def get_all_items():

    with get_session() as session:

        items = session.exec(select(Item)).all()

        return [
            {
                "id": item.id,
                "name": item.name,
                "gesamtbetrag_cent": item.gesamtbetrag_cent,
                "buyer_id": item.buyer_id,
                "menge": item.menge,
                "einheit": item.einheit,
            }
            for item in items
        ]


def update_item(
    item_id: int,
    name: str | None = None,
    betrag_cent: int | None = None,
    buyer_id: int | None = None,
    menge: float | None = None,
    einheit: Einheit | None = None,
):

    with get_session() as session:

        item = session.get(
            Item,
            item_id,
        )

        if item is None:
            return None

        if name is not None:
            item.name = name

        if betrag_cent is not None:
            item.gesamtbetrag_cent = betrag_cent

        if buyer_id is not None:
            item.buyer_id = buyer_id

        if menge is not None:
            item.menge = menge

        if einheit is not None:
            item.einheit = einheit

        session.add(item)
        session.flush()
        session.refresh(item)
        clear_cache()

        return {
            "id": item.id,
            "name": item.name,
            "gesamtbetrag_cent": item.gesamtbetrag_cent,
            "buyer_id": item.buyer_id,
            "menge": item.menge,
            "einheit": item.einheit,
        }


def delete_item(item_id: int) -> bool:

    with get_session() as session:

        item = session.get(Item, item_id)

        if item is None:
            return False

        consumers = session.exec(
            select(ItemConsumer).where(ItemConsumer.item_id == item_id)
        ).all()

        for consumer in consumers:
            session.delete(consumer)

        session.delete(item)
        clear_cache()

        return True


def add_all_persons_as_consumers(
    item_id: int,
    persons: list[dict],
    modus: AufteilungsModus = AufteilungsModus.GLEICHMAESSIG,
):

    with get_session() as session:

        for p in persons:

            existing = session.exec(
                select(ItemConsumer).where(
                    ItemConsumer.item_id == item_id,
                    ItemConsumer.user_id == p["id"],
                )
            ).first()

            if existing:
                continue

            session.add(
                ItemConsumer(
                    item_id=item_id,
                    user_id=p["id"],
                    modus=modus,
                    wert=1.0,
                )
            )

        session.commit()
        clear_cache()


def create_consumer(
    item_id: int,
    user_id: int,
    modus: AufteilungsModus = AufteilungsModus.GLEICHMAESSIG,
    wert: float = 1.0,
):
    """
    Fügt einen neuen Consumer zu einem Item hinzu.
    """

    with get_session() as session:

        # optional: verhindern dass Person doppelt drin ist
        existing = session.exec(
            select(ItemConsumer).where(
                ItemConsumer.item_id == item_id,
                ItemConsumer.user_id == user_id,
            )
        ).first()

        if existing:
            raise ValueError("User ist bereits Consumer dieses Items")

        consumer = ItemConsumer(
            item_id=item_id,
            user_id=user_id,
            modus=modus,
            wert=wert,
        )

        session.add(consumer)
        session.flush()
        session.refresh(consumer)
        clear_cache()

        return {
            "id": consumer.id,
            "item_id": consumer.item_id,
            "user_id": consumer.user_id,
            "modus": consumer.modus,
            "wert": consumer.wert,
        }
