from db.models import ItemConsumer
from db.database import get_session
from sqlmodel import select
import streamlit as st


def get_all_consumers():

    with get_session() as session:
        consumers = session.exec(select(ItemConsumer)).all()

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
