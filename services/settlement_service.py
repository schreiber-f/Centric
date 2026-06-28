from sqlmodel import select
from typing import Sequence
from db.models import (
    Settlement,
)
from db.database import get_session
from services.cache_service import clear_cache
import streamlit as st


def create_settlement(
    from_payer_id: int,
    to_payer_id: int,
    amount_cent: int,
    is_paid: bool = False,
    note: str | None = None,
):

    with get_session() as session:

        settlement = Settlement(
            from_payer_id=from_payer_id,
            to_payer_id=to_payer_id,
            amount_cent=amount_cent,
            is_paid=is_paid,
            note=note,
        )

        session.add(settlement)
        session.flush()
        session.refresh(settlement)
        clear_cache()

        return {
            "id": settlement.id,
            "from_payer_id": settlement.from_payer_id,
            "to_payer_id": settlement.to_payer_id,
            "amount_cent": settlement.amount_cent,
        }


def get_settlement(
    settlement_id: int,
):

    with get_session() as session:
        settlement = session.get(
            Settlement,
            settlement_id,
        )
        return (
            {
                "id": settlement.id,
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
                "note": settlement.note,
            }
            if settlement
            else None
        )


@st.cache_data(show_spinner=False)
def get_all_settlements():

    with get_session() as session:

        settlements = session.exec(select(Settlement)).all()

        return [
            {
                "id": settlement.id,
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
                "is_paid": settlement.is_paid,
                "note": settlement.note,
            }
            for settlement in settlements
        ]


def update_settlement(
    settlement_id: int,
    from_payer_id: int | None = None,
    to_payer_id: int | None = None,
    amount_cent: int | None = None,
    note: str | None = None,
    is_paid: bool | None = None,
):

    with get_session() as session:

        settlement = session.get(
            Settlement,
            settlement_id,
        )

        if settlement is None:
            return None

        if amount_cent:
            settlement.amount_cent = amount_cent
        elif note:
            settlement.note = note
        elif not (is_paid is None):
            settlement.is_paid = is_paid
        elif from_payer_id:
            settlement.from_payer_id = from_payer_id
        elif to_payer_id:
            settlement.to_payer_id = to_payer_id

        session.add(settlement)
        session.flush()
        session.refresh(settlement)
        clear_cache()

        return (
            {
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
                "is_paid": settlement.is_paid,
                "note": settlement.note,
            }
            if settlement
            else None
        )


def delete_settlement(
    settlement_id: int,
) -> bool:

    with get_session() as session:

        settlement = session.get(
            Settlement,
            settlement_id,
        )

        if settlement is None:
            return False

        session.delete(settlement)
        clear_cache()

        return True
