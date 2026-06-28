from collections import deque

from services.balance_service import get_balances
from services.settlement_service import create_settlement, get_all_settlements
import streamlit as st


def split_balances(
    balances: dict[int, int],
) -> tuple[list[list[int]], list[list[int]]]:
    """
    Rückgabe:
        creditors = [[person_id, guthaben], ...]
        debtors   = [[person_id, schuld], ...]
    """

    creditors = []
    debtors = []

    for person_id, balance in balances.items():

        if balance > 0:
            creditors.append([person_id, balance])

        elif balance < 0:
            debtors.append([person_id, -balance])

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    return creditors, debtors


def calculate_debts() -> list[dict]:
    """
    Berechnet die minimale Anzahl an Überweisungen.
    """

    balances = get_balances()

    creditors, debtors = split_balances(balances)

    creditors = deque(creditors)
    debtors = deque(debtors)

    debts = []

    while creditors and debtors:

        creditor_id, credit = creditors[0]
        debtor_id, debt = debtors[0]

        amount = min(credit, debt)

        debts.append(
            {
                "from_payer_id": debtor_id,
                "to_payer_id": creditor_id,
                "amount_cent": amount,
            }
        )

        credit -= amount
        debt -= amount

        creditors.popleft()
        debtors.popleft()

        if credit > 0:
            creditors.appendleft([creditor_id, credit])

        if debt > 0:
            debtors.appendleft([debtor_id, debt])

    return debts


def get_debts_for_person(
    person_id: int,
) -> list[dict]:
    """
    Alle offenen Überweisungen einer Person.
    """

    return [
        debt
        for debt in calculate_debts()
        if debt["from_payer_id"] == person_id or debt["to_payer_id"] == person_id
    ]


def get_creditors_for_person(
    person_id: int,
) -> list[dict]:
    """
    Wen muss diese Person bezahlen?
    """

    return [debt for debt in calculate_debts() if debt["from_payer_id"] == person_id]


def get_debtors_for_person(
    person_id: int,
) -> list[dict]:
    """
    Wer muss dieser Person Geld überweisen?
    """

    return [debt for debt in calculate_debts() if debt["to_payer_id"] == person_id]


def get_total_debt(
    person_id: int,
) -> int:
    """
    Positive Zahl = Person bekommt Geld.
    Negative Zahl = Person schuldet Geld.
    """

    return get_balances().get(person_id, 0)


def create_settlements_from_debts() -> list[dict]:
    """
    Erstellt aus den aktuell berechneten Schulden neue Settlements.

    Falls bereits unbezahlte Settlements existieren,
    werden keine neuen erstellt.
    """

    open_settlements = [
        settlement for settlement in get_all_settlements() if not settlement["is_paid"]
    ]

    if open_settlements:
        raise ValueError("Es existieren bereits offene Settlements.")

    created = []

    for debt in calculate_debts():

        if debt["amount_cent"] <= 0:
            continue

        created.append(
            create_settlement(
                from_payer_id=debt["from_payer_id"],
                to_payer_id=debt["to_payer_id"],
                amount_cent=debt["amount_cent"],
            )
        )

    return created
