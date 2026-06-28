import streamlit as st
import pandas as pd
import plotly.express as px

from services.balance_service import get_total_paid, get_total_consumed
from services.state_service import recompute_state

st.set_page_config(page_title="Centric Dashboard", layout="wide")

st.title("📊 Centric Dashboard")

state = recompute_state()

persons = state["persons"]
items = state["items"]
settlements = state["settlements"]
debts = state["debts"]
balances = state["balances"]

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
if not person_df.empty and not item_df.empty:
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

# Balance breakdown
st.divider()
st.subheader("📊 Finanzstruktur pro Person")

rows = []

for p in persons:
    rows.append(
        {
            "name": p["name"],
            "paid": get_total_paid(p["id"]) / 100,
            "consumed": get_total_consumed(p["id"]) / 100,
            "balance": state["balances"].get(p["id"], 0) / 100,
        }
    )

df = pd.DataFrame(rows)

fig = px.bar(
    df,
    x="name",
    y=["paid", "consumed", "balance"],
    barmode="group",
    title="💰 Paid vs Consumed vs Balance",
)

st.plotly_chart(fig, use_container_width=True)

# Debt network flow
st.divider()
st.subheader("🔁 Optimale Geldflüsse")

if debts:

    debt_df = pd.DataFrame(debts)

    debt_df = debt_df.merge(person_df, left_on="from_payer_id", right_on="id")
    debt_df = debt_df.rename(columns={"name": "from"}).drop(columns=["id"])

    debt_df = debt_df.merge(person_df, left_on="to_payer_id", right_on="id")
    debt_df = debt_df.rename(columns={"name": "to"}).drop(columns=["id"])

    debt_df["amount"] = debt_df["amount_cent"] / 100

    fig = px.sunburst(
        debt_df, path=["from", "to"], values="amount", title="🌐 Geldfluss Netzwerk"
    )

    st.plotly_chart(fig, use_container_width=True)

# Schuldverteilung
st.divider()
st.subheader("💸 Schuldverteilung")

df = pd.DataFrame(
    [{"name": p["name"], "balance": balances[p["id"]] / 100} for p in persons]
)

fig = px.treemap(
    df,
    path=["name"],
    values=df["balance"].abs(),
    color="balance",
    color_continuous_scale="RdYlGn",
    title="📦 Schuld-/Guthabenverteilung",
)

st.plotly_chart(fig, use_container_width=True)


# Settlement progress
st.divider()
st.subheader("⚖️ Settlement Fortschritt")

settlement_df = pd.DataFrame(state["settlements"])

if not settlement_df.empty:

    settlement_df["amount"] = settlement_df["amount_cent"] / 100

    progress = settlement_df.groupby("is_paid")["amount"].sum().reset_index()

    progress["status"] = progress["is_paid"].map({True: "bezahlt", False: "offen"})

    fig = px.pie(
        progress, names="status", values="amount", title="🧾 Settlement Status"
    )

    st.plotly_chart(fig, use_container_width=True)


# System Komplexität
st.divider()
st.subheader("🧠 System-Komplexität")

summary = pd.DataFrame(
    [
        {
            "Personen": len(persons),
            "Items": len(items),
            "Transfers nötig": len(debts),
        }
    ]
)

fig = px.bar(
    summary.melt(),
    x="variable",
    y="value",
    text_auto=True,
    title="⚙️ Komplexität des Systems",
)

st.plotly_chart(fig, use_container_width=True)
