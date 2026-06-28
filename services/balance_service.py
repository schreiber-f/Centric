from collections import defaultdict
from sqlmodel import select

from db.models import AufteilungsModus
from services.item_service import get_all_items
from services.consumer_service import get_all_consumers
from services.settlement_service import get_all_settlements
from services.person_service import get_all_persons
import streamlit as st


def calculate_consumer_cost(
    item: dict,
    consumer: dict,
    consumer_count: int,
) -> int:

    modus = consumer["modus"]

    if modus == AufteilungsModus.GLEICHMAESSIG:
        return round(item["gesamtbetrag_cent"] / consumer_count)

    if modus == AufteilungsModus.PROZENT:
        return round(item["gesamtbetrag_cent"] * consumer["wert"] / 100)

    if modus == AufteilungsModus.STUECKZAHL:

        menge = item["menge"]

        if not menge:
            return 0

        preis_pro_stueck = item["gesamtbetrag_cent"] / menge

        return round(preis_pro_stueck * consumer["wert"])

    raise ValueError(f"Unbekannter Modus: {modus}")


def apply_settlements(
    balances: dict[int, int],
    settlements: list[dict],
):

    for settlement in settlements:

        if not settlement["is_paid"]:
            continue

        balances[settlement["from_payer_id"]] += settlement["amount_cent"]
        balances[settlement["to_payer_id"]] -= settlement["amount_cent"]


@st.cache_data
def get_balances() -> dict[int, int]:

    persons = get_all_persons()
    items = get_all_items()
    consumers = get_all_consumers()
    settlements = get_all_settlements()

    paid = defaultdict(int)
    consumed = defaultdict(int)

    # item_id -> alle Consumer
    consumer_map = defaultdict(list)

    for consumer in consumers:
        consumer_map[consumer["item_id"]].append(consumer)

    # Wer hat bezahlt / konsumiert?
    for item in items:

        paid[item["buyer_id"]] += item["gesamtbetrag_cent"]

        item_consumers = consumer_map[item["id"]]

        if not item_consumers:
            continue

        consumer_count = len(item_consumers)

        for consumer in item_consumers:

            consumed[consumer["user_id"]] += calculate_consumer_cost(
                item=item,
                consumer=consumer,
                consumer_count=consumer_count,
            )

    balances = {}

    for person in persons:

        person_id = person["id"]

        balances[person_id] = paid[person_id] - consumed[person_id]

    apply_settlements(
        balances=balances,
        settlements=settlements,
    )

    return dict(balances)


@st.cache_data
def get_balance(person_id: int) -> int:
    return get_balances().get(person_id, 0)


@st.cache_data
def get_total_paid(person_id: int) -> int:

    return sum(
        item["gesamtbetrag_cent"]
        for item in get_all_items()
        if item["buyer_id"] == person_id
    )


@st.cache_data
def get_total_consumed(person_id: int) -> int:

    items = get_all_items()
    consumers = get_all_consumers()

    consumer_map = defaultdict(list)

    for consumer in consumers:
        consumer_map[consumer["item_id"]].append(consumer)

    total = 0

    for item in items:

        item_consumers = consumer_map[item["id"]]

        if not item_consumers:
            continue

        for consumer in item_consumers:

            if consumer["user_id"] != person_id:
                continue

            total += calculate_consumer_cost(
                item,
                consumer,
                len(item_consumers),
            )

    return total
