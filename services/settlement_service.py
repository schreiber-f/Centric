from sqlmodel import select
from typing import Sequence
from db.models import (
    Settlement,
)
from db.database import get_session


def create_settlement(
    from_payer_id: int,
    to_payer_id: int,
    amount_cent: int,
):

    with get_session() as session:

        settlement = Settlement(
            from_payer_id=from_payer_id,
            to_payer_id=to_payer_id,
            amount_cent=amount_cent,
        )

        session.add(settlement)
        session.flush()
        session.refresh(settlement)

        return {
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
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
                "note": settlement.note,
            }
            if settlement
            else None
        )


def get_all_settlements():

    with get_session() as session:

        settlements = session.exec(select(Settlement)).all()

        return [
            {
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
                "note": settlement.note,
            }
            for settlement in settlements
        ]


def update_settlement(
    settlement_id: int,
    amount_cent: int,
):

    with get_session() as session:

        settlement = session.get(
            Settlement,
            settlement_id,
        )

        if settlement is None:
            return None

        settlement.amount_cent = amount_cent

        session.add(settlement)
        session.flush()
        session.refresh(settlement)

        return (
            {
                "from_payer_id": settlement.from_payer_id,
                "to_payer_id": settlement.to_payer_id,
                "amount_cent": settlement.amount_cent,
                "created_at": settlement.created_at,
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

        return True
