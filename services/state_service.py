import streamlit as st
from services.person_service import get_all_persons
from services.item_service import get_all_items
from services.consumer_service import get_all_consumers
from services.settlement_service import get_all_settlements
from services.balance_service import get_balances
from services.debt_service import calculate_debts


@st.cache_data(ttl=2)
def recompute_state():
    items = get_all_items()
    consumers = get_all_consumers()
    persons = get_all_persons()
    settlements = get_all_settlements()

    balances = get_balances()
    debts = calculate_debts()

    return {
        "items": items,
        "consumers": consumers,
        "balances": balances,
        "debts": debts,
        "settlements": settlements,
        "persons": persons,
    }
