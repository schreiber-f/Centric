import streamlit as st
from db.init import init_db

# 1. Datenbank initialisieren
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# 2. Seiten definieren (Wir erstellen eine echte extra Datei für die Startseite)
home_seite = st.Page(
    "pages/0_home.py", title="📊 Abrechnung & Übersicht", icon="💰", default=True
)
adder_seite = st.Page("pages/1_adder.py", title="Personen und Items adden", icon="➕")
distribution_page = st.Page(
    "pages/2_distribution.py",
    title="Artikel & Verteilung",
    icon="📊",
)
debug_seite = st.Page("pages/3_debug.py", title="Datenbank Debug", icon="⚙️")

# 3. Navigation anzeigen
pg = st.navigation(
    {
        "Hauptmenü": [home_seite],
        "Verwaltung": [adder_seite, distribution_page, debug_seite],
    }
)

pg.run()
