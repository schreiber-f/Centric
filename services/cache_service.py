import streamlit as st


def clear_cache():
    """Löscht sämtliche berechneten Daten."""

    st.cache_data.clear()
