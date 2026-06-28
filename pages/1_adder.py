import streamlit as st
import json

from services import create_person, get_all_persons, delete_person
from services.item_service import create_item
from db import Einheit

st.title("➕ Daten hinzufügen")

tab_person, tab_item = st.tabs(["👤 Person", "🛒 Einkauf"])

# -------------------------
# PERSON
# -------------------------
with tab_person:
    st.subheader("Neue Person")

    with st.form("person_form", clear_on_submit=True):
        person_name = st.text_input("Name")
        submit_person = st.form_submit_button("Person erstellen")

        if submit_person:
            if person_name.strip():
                create_person(person_name.strip())
                st.success(f"{person_name} angelegt", icon="✅")
            else:
                st.error("Name fehlt")


# -------------------------
# EINKAUF
# -------------------------
with tab_item:
    st.subheader("Neuer Einkauf")

    persons = get_all_persons()

    if not persons:
        st.warning("Bitte zuerst Personen anlegen.")
        st.stop()

    person_options = {p["name"]: p["id"] for p in persons}

    # -------------------------
    # FORM
    # -------------------------
    with st.form("item_form", clear_on_submit=True):

        tab_fields, tab_json = st.tabs(["📋 Einzelne Felder", "💻 JSON einfügen"])

        # =========================
        # MANUELLE EINGABE
        # =========================
        with tab_fields:

            item_name = st.text_input("Artikel")
            amount_euro = st.number_input(
                "Preis (€)",
                min_value=0.0,
                step=0.01,
            )

            with st.expander("Optional: Menge & Einheit"):

                einheit = st.selectbox("Einheit", options=[e.value for e in Einheit])

                menge = st.number_input(
                    "Menge",
                    min_value=1,
                    step=1,
                )

            buyer_name = st.selectbox(
                "Bezahlt von",
                options=list(person_options.keys()),
            )

            submit_item = st.form_submit_button("Einkauf speichern")

            if submit_item:

                buyer_id = person_options[buyer_name]

                payload = {
                    "name": item_name,
                    "betrag_cent": int(round(amount_euro * 100)),
                    "buyer_id": buyer_id,
                }

                # nur speichern wenn aktiv
                if menge > 0:
                    payload["einheit"] = einheit
                    payload["menge"] = float(menge)

                create_item(**payload)

                st.success("Item gespeichert")
                st.toast("Gespeichert!", icon="🛒")

        # =========================
        # JSON MODE
        # =========================
        with tab_json:

            st.subheader("JSON-Struktur einfügen")

            json_input = st.text_area(
                "Füge hier dein JSON ein:",
                placeholder="""[
    {
        "name": "Cola",
        "gesamtbetrag_cent": 400,
        "buyer_id": 1,
        "einheit": null,
        "menge": null
    }
]""",
                height=250,
            )

            submitted_json = st.form_submit_button("JSON verarbeiten")

            if submitted_json:

                try:
                    parsed_data = json.loads(json_input)

                    # optional: direkt speichern
                    if isinstance(parsed_data, list):

                        for item in parsed_data:
                            create_item(
                                name=item["name"],
                                betrag_cent=item["gesamtbetrag_cent"],
                                buyer_id=item["buyer_id"],
                                einheit=item.get("einheit"),
                                menge=item.get("menge"),
                            )

                        st.success("JSON erfolgreich importiert!")
                        st.toast("Import abgeschlossen", icon="📦")

                    else:
                        st.error("JSON muss eine Liste sein")

                except json.JSONDecodeError as e:
                    st.error(f"Ungültiges JSON: {e}")


# -------------------------
# FOOTER
# -------------------------
st.divider()
st.subheader("Teilnehmer")

for person in get_all_persons():
    # Wir erstellen zwei Spalten: Eine breite für den Namen, eine schmale für den Button
    col1, col2 = st.columns([0.8, 0.2])

    with col1:
        st.write(person["name"])

    with col2:
        # Ein eindeutiger Key ist wichtig, da wir in einer Schleife sind
        if st.button("Löschen", key=f"delete_{person['id']}"):
            if delete_person(person["id"]):
                st.success(f"{person['name']} wurde gelöscht.")
                st.rerun()  # Aktualisiert die Ansicht sofort
            else:
                st.error("Fehler beim Löschen der Person.")
