from collections import defaultdict
from sqlmodel import select

from db.models import (
    Person,
    Item,
    ItemConsumer,
    Settlement,
)
from db.database import get_session


def get_balances():

    with get_session() as session:

        payers = session.exec(select(Person)).all()
        items = session.exec(select(Item)).all()
        consumers = session.exec(select(ItemConsumer)).all()
        settlements = session.exec(select(Settlement)).all()

    paid = defaultdict(int)
    consumed = defaultdict(int)

    for item in items:
        paid[item.buyer_id] += item.gesamtbetrag_cent

    for consumer in consumers:
        consumed[consumer.user_id] += round(consumer.wert)

    balances = {}

    for payer in payers:

        payer_id = payer.id

        if payer_id is None:
            continue

        balances[payer_id] = paid[payer_id] - consumed[payer_id]

    for settlement in settlements:

        balances[settlement.from_payer_id] += settlement.amount_cent
        balances[settlement.to_payer_id] -= settlement.amount_cent

    return balances
