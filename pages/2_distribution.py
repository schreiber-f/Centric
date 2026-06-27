import streamlit as st
import pandas as pd

from db import AufteilungsModus, Einheit

from services.person_service import get_all_persons
from services.item_service import (
    get_all_items,
    get_item,
    update_item,
    delete_item,
    get_item_consumers,
    update_consumer,
    delete_consumer,
)

st.title("⚖️ Artikel & Verteilung")

items = get_all_items()

if not items:
    st.info("Keine Artikel vorhanden")
    st.stop()

item_options = {
    f"{item['name']} ({item['gesamtbetrag_cent']/100:.2f} €)": item["id"]
    for item in items
}

selected_label = st.selectbox(
    "Artikel auswählen",
    options=list(item_options.keys()),
)

item_id = item_options[selected_label]

item = get_item(item_id)

persons = get_all_persons()

person_lookup = {p["id"]: p["name"] for p in persons}

st.divider()

# Artikel bearbeiten
st.subheader("🛒 Artikeldaten")

if item:
    with st.form("item_edit_form"):

        name = st.text_input(
            "Name",
            value=item["name"],
        )

        preis = st.number_input(
            "Preis (€)",
            value=item["gesamtbetrag_cent"] / 100,
            min_value=0.0,
            step=0.01,
        )

        buyer_name = st.selectbox(
            "Bezahlt von",
            options=[p["name"] for p in persons],
            index=[p["id"] for p in persons].index(item["buyer_id"]),
        )

        use_quantity = item["menge"] is not None

        quantity_enabled = st.checkbox(
            "Menge verwenden",
            value=use_quantity,
        )

        menge = None
        einheit = None

        if quantity_enabled:

            menge = st.number_input(
                "Menge",
                value=float(item["menge"] or 1),
                min_value=0.0,
            )

            einheit = st.selectbox(
                "Einheit",
                options=[e.value for e in Einheit],
                index=0,
            )

        submit = st.form_submit_button("💾 Artikel speichern")

        if submit:

            buyer_id = next(p["id"] for p in persons if p["name"] == buyer_name)

            update_item(
                item_id=item_id,
                name=name,
                betrag_cent=int(preis * 100),
                buyer_id=buyer_id,
                menge=menge,
                einheit=Einheit(einheit),
            )

            st.success("Artikel gespeichert")
            st.rerun()

    # Consumer laden

    st.divider()
    st.subheader("👥 Verteilung")

    consumers = get_item_consumers(item_id)

    if not consumers:
        st.warning("Keine Consumer vorhanden")
        st.stop()

    # Modus bestimmen

    modus = consumers[0]["modus"]

    modus = st.selectbox(
        "Modus",
        options=list(AufteilungsModus),
        format_func=lambda m: m.value,
        index=list(AufteilungsModus).index(modus),
    )

    # Tabelle erzeugen

    rows = []

    for consumer in consumers:

        rows.append(
            {
                "consumer_id": consumer["id"],
                "Person": person_lookup.get(
                    consumer["user_id"],
                    "Unbekannt",
                ),
                "Wert": consumer["wert"],
            }
        )

    df = pd.DataFrame(rows)

    if modus == AufteilungsModus.GLEICHMAESSIG:

        st.info("Die Kosten werden automatisch auf alle Teilnehmer verteilt.")

        st.dataframe(
            df[["Person"]],
            use_container_width=True,
        )

        valid = True

    else:

        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            disabled=["consumer_id", "Person"],
        )

        total = edited["Wert"].sum()

        if modus == AufteilungsModus.PROZENT:

            valid = abs(total - 100) < 0.01

            if valid:
                st.success("✓ 100 %")
            else:
                st.error(f"Aktuell {total:.2f}%")

            total = edited["Wert"].sum()

        elif modus == AufteilungsModus.STUECKZAHL:

            max_amount = item["menge"] or 0

            valid = total <= max_amount

            if valid:
                st.success(f"{total}/{max_amount}")
            else:
                st.error(f"{total}/{max_amount}")

    if st.button(
        "💾 Verteilung speichern",
        disabled=not valid,
    ):

        for _, row in edited.iterrows():

            update_consumer(
                consumer_id=int(row["consumer_id"]),
                modus=modus,
                wert=float(row["Wert"]),
            )

        st.success("Verteilung gespeichert")
        st.rerun()

    st.divider()
    st.subheader("🗑️ Teilnehmer")

    consumer_map = {person_lookup[c["user_id"]]: c["id"] for c in consumers}

    selected_consumer = st.selectbox(
        "Teilnehmer entfernen",
        options=list(consumer_map.keys()),
    )

    if st.button("Teilnehmer entfernen"):

        delete_consumer(consumer_map[selected_consumer])

        st.rerun()

    st.divider()

    with st.expander("🚨 Danger Zone"):

        if st.button(
            "🗑️ Artikel löschen",
            type="primary",
        ):

            delete_item(item_id)

            st.success("Artikel gelöscht")
            st.rerun()
else:
    st.error("Es konnte kein Item gefunden werden")
