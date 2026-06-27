from balance_service import get_balances


def calculate_debts():

    balances = get_balances()

    creditors = []
    debtors = []

    for payer_id, balance in balances.items():

        if balance > 0:
            creditors.append([payer_id, balance])

        elif balance < 0:
            debtors.append([payer_id, abs(balance)])

    debts = []

    creditor_index = 0

    for debtor_id, debt_amount in debtors:

        remaining = debt_amount

        while remaining > 0 and creditor_index < len(creditors):

            creditor_id, credit_amount = creditors[creditor_index]

            transfer = min(
                remaining,
                credit_amount,
            )

            debts.append(
                {
                    "from_payer_id": debtor_id,
                    "to_payer_id": creditor_id,
                    "amount_cent": transfer,
                }
            )

            remaining -= transfer

            creditors[creditor_index][1] -= transfer

            if creditors[creditor_index][1] == 0:
                creditor_index += 1

    return debts
