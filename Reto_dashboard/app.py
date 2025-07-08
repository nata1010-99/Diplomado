import streamlit as st
from Dashboard_clase.cargar_datos import show_data_tab  # Solo importas esta pestaña por ahora

# Título de la app
st.set_page_config(page_title="Dashboard SECOP", layout="wide")
st.title("📊 Dashboard SECOP - Prototipo Inicial")

# Solo una pestaña: carga de datos
tabs = st.tabs(["📥 Carga de Datos"])

with tabs[0]:
    show_data_tab()