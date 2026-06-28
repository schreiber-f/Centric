import streamlit as st
import pandas as pd

from services.person_service import get_all_persons
from services.debt_service import (
    calculate_debts,
    create_settlements_from_debts,
)
from services.settlement_service import (
    get_all_settlements,
    update_settlement,
)

st.set_page_config(layout="wide")

st.title("💸 Kostenabwicklung")

persons = get_all_persons()
person_lookup = {p["id"]: p["name"] for p in persons}

# --------------------------------------------------
# Berechnete Schulden
# --------------------------------------------------

st.header("📋 Offene Schulden")

debts = calculate_debts()

if debts:

    debt_df = pd.DataFrame(
        [
            {
                "Von": person_lookup[d["from_payer_id"]],
                "An": person_lookup[d["to_payer_id"]],
                "Betrag (€)": round(d["amount_cent"] / 100, 2),
            }
            for d in debts
        ]
    )

    st.dataframe(
        debt_df,
        hide_index=True,
        use_container_width=True,
    )

    if st.button(
        "💾 Als Settlements übernehmen",
        type="primary",
    ):

        create_settlements_from_debts()

        st.success("Settlements erstellt")

        st.rerun()

else:

    st.success("🎉 Es bestehen keine offenen Schulden.")

st.divider()

# --------------------------------------------------
# Settlements
# --------------------------------------------------

st.header("🤝 Settlements")

settlements = get_all_settlements()

if settlements:

    rows = []

    for settlement in settlements:

        rows.append(
            {
                "id": settlement["id"],
                "Von": person_lookup[settlement["from_payer_id"]],
                "An": person_lookup[settlement["to_payer_id"]],
                "Betrag (€)": settlement["amount_cent"] / 100,
                "Bezahlt": settlement["is_paid"],
                "Datum": settlement["created_at"],
            }
        )

    df = pd.DataFrame(rows)

    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=[
            "id",
            "Von",
            "An",
            "Betrag (€)",
            "Datum",
        ],
        column_config={"Bezahlt": st.column_config.CheckboxColumn("Bezahlt")},
    )

    if st.button("💾 Änderungen speichern"):

        for _, row in edited.iterrows():

            update_settlement(
                settlement_id=int(row["id"]),
                is_paid=bool(row["Bezahlt"]),
            )

        st.success("Settlements aktualisiert")

        st.rerun()

else:

    st.info("Noch keine Settlements vorhanden.")

st.divider()

# --------------------------------------------------
# Statistiken
# --------------------------------------------------

paid = sum(s["amount_cent"] for s in settlements if s["is_paid"])

open_amount = sum(s["amount_cent"] for s in settlements if not s["is_paid"])

c1, c2, c3 = st.columns(3)

c1.metric(
    "📄 Settlements",
    len(settlements),
)

c2.metric(
    "✅ Bezahlt",
    f"{paid/100:.2f} €",
)

c3.metric(
    "⌛ Offen",
    f"{open_amount/100:.2f} €",
)
