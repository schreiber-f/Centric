import streamlit as st
import pandas as pd
import plotly.express as px

from services.person_service import get_all_persons
from services.item_service import get_all_items
from services.settlement_service import get_all_settlements

st.set_page_config(page_title="Centric Dashboard", layout="wide")

st.title("📊 Centric Dashboard")

persons = get_all_persons()
items = get_all_items()
settlements = get_all_settlements()

person_df = pd.DataFrame(persons)
item_df = pd.DataFrame(items)
settlement_df = pd.DataFrame(settlements)

# -----------------------
# KPIs
# -----------------------

total_spent = item_df["gesamtbetrag_cent"].sum() / 100 if not item_df.empty else 0

total_settled = (
    settlement_df["amount_cent"].sum() / 100 if not settlement_df.empty else 0
)

open_amount = total_spent - total_settled

c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Personen", len(person_df))
c2.metric("🛒 Einkäufe", len(item_df))
c3.metric("💰 Ausgaben", f"{total_spent:.2f} €")
c4.metric("⚖️ Offen", f"{open_amount:.2f} €")

# -----------------------
# Käuferanalyse
# -----------------------

if not item_df.empty:

    buyer_stats = item_df.groupby("buyer_id")["gesamtbetrag_cent"].sum().reset_index()

    buyer_stats["betrag_euro"] = buyer_stats["gesamtbetrag_cent"] / 100

    buyer_stats = buyer_stats.merge(
        person_df,
        left_on="buyer_id",
        right_on="id",
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            buyer_stats,
            x="name",
            y="betrag_euro",
            title="💳 Ausgaben pro Person",
            text_auto=True,
        )

        fig.update_layout(xaxis_title=None, yaxis_title="€")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            buyer_stats,
            names="name",
            values="betrag_euro",
            hole=0.65,
            title="🥧 Anteil an Ausgaben",
        )

        st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Top Artikel
# -----------------------

if not item_df.empty:

    expensive = item_df.nlargest(10, "gesamtbetrag_cent")

    expensive["preis"] = expensive["gesamtbetrag_cent"] / 100

    fig = px.bar(
        expensive,
        x="preis",
        y="name",
        orientation="h",
        title="🔥 Teuerste Artikel",
        text_auto=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# -----------------------
# Artikelhäufigkeit
# -----------------------

if not item_df.empty:

    counts = (
        item_df.groupby("name")
        .size()
        .reset_index(name="anzahl")
        .sort_values(
            "anzahl",
            ascending=False,
        )
        .head(10)
    )

    fig = px.treemap(
        counts,
        path=["name"],
        values="anzahl",
        title="📦 Häufig gekaufte Artikel",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# -----------------------
# Einheitenverteilung
# -----------------------

if not item_df.empty and "einheit" in item_df.columns:

    units = item_df[item_df["einheit"].notna()]

    if not units.empty:

        fig = px.sunburst(
            units,
            path=["einheit"],
            title="⚖️ Verteilung der Einheiten",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

# -----------------------
# Settlements
# -----------------------

if not settlement_df.empty:

    settlement_df["amount_euro"] = settlement_df["amount_cent"] / 100

    fig = px.histogram(
        settlement_df,
        x="amount_euro",
        nbins=20,
        title="💸 Settlement Beträge",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# -----------------------
# Saldoberechnung
# -----------------------

saldo = {}

for p in persons:
    saldo[p["id"]] = 0

for item in items:
    saldo[item["buyer_id"]] += item["gesamtbetrag_cent"] / 100

for settlement in settlements:

    amount = settlement["amount_cent"] / 100

    saldo[settlement["from_payer_id"]] += amount

    saldo[settlement["to_payer_id"]] -= amount

balance_df = pd.DataFrame(
    [
        {
            "Person": p["name"],
            "Saldo": saldo[p["id"]],
        }
        for p in persons
    ]
)

fig = px.bar(
    balance_df,
    x="Person",
    y="Saldo",
    color="Saldo",
    title="🏦 Aktueller Saldo",
    text_auto=True,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# -----------------------
# Einkäufe
# -----------------------

st.divider()
st.subheader("🧾 Einkäufe")

if not item_df.empty:

    display_df = item_df.copy()

    display_df["preis"] = display_df["gesamtbetrag_cent"] / 100

    st.dataframe(
        display_df,
        use_container_width=True,
    )
