import streamlit as st
import pandas as pd
from sqlmodel import select

from db.models import (
    Person,
    Item,
    ItemConsumer,
    Settlement,
)
from db.database import get_session

st.set_page_config(
    page_title="Datenbank Debug",
    layout="wide",
)

st.title("🛠️ Datenbank-Debug")

# daten laden

with get_session() as session:

    persons = [p.model_dump() for p in session.exec(select(Person)).all()]

    items = [i.model_dump() for i in session.exec(select(Item)).all()]

    consumers = [c.model_dump() for c in session.exec(select(ItemConsumer)).all()]

    settlements = [s.model_dump() for s in session.exec(select(Settlement)).all()]


# -----------------------------

# Statistik

# -----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👤 Personen",
    len(persons),
)

col2.metric(
    "🛒 Einkäufe",
    len(items),
)

col3.metric(
    "🔗 Verteilungen",
    len(consumers),
)

col4.metric(
    "💸 Ausgleiche",
    len(settlements),
)

st.divider()

# Personen

st.subheader("👤 persons")

if persons:

    df = pd.DataFrame(persons)

    st.dataframe(
        df,
        width="stretch",
    )

    with st.expander("JSON anzeigen"):
        st.json(persons)

else:
    st.info("Keine Personen vorhanden.")

# Items

st.subheader("🛒 items")

if items:

    df = pd.DataFrame(items)

    st.dataframe(
        df,
        width="stretch",
    )

    with st.expander("JSON anzeigen"):
        st.json(items)

else:
    st.info("Keine Einkäufe vorhanden.")

# ItemConsumer

st.subheader("🔗 item_consumers")

if consumers:

    df = pd.DataFrame(consumers)

    st.dataframe(
        df,
        width="stretch",
    )

    with st.expander("JSON anzeigen"):
        st.json(consumers)


else:
    st.info("Keine Verteilungen vorhanden.")


# Settlements

st.subheader("💸 settlements")

if settlements:

    df = pd.DataFrame(settlements)

    st.dataframe(
        df,
        width="stretch",
    )

    with st.expander("JSON anzeigen"):
        st.json(settlements)

else:
    st.info("Keine Ausgleichszahlungen vorhanden.")

# -----------------------------

# Danger Zone

# -----------------------------

st.divider()

with st.expander("🚨 Danger Zone"):

    st.warning("Löscht alle Daten aus der Datenbank.")

    confirm = st.checkbox("Ja, wirklich alles löschen")

    if confirm and st.button("🗑️ Datenbank leeren"):

        with get_session() as session:

            for settlement in session.exec(select(Settlement)).all():
                session.delete(settlement)

            for consumer in session.exec(select(ItemConsumer)).all():
                session.delete(consumer)

            for item in session.exec(select(Item)).all():
                session.delete(item)

            for person in session.exec(select(Person)).all():
                session.delete(person)

        st.success("Datenbank erfolgreich geleert.")

        st.rerun()
