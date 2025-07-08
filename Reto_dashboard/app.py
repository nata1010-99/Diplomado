from cargar_datos_secop import show_data_tab
import streamlit as st

# Título de la app
st.set_page_config(page_title="Dashboard SECOP", layout="wide")
st.title("📊 Dashboard SECOP - Prototipo Inicial")

# Solo una pestaña: carga de datos
tabs = st.tabs(["📥 Carga de Datos"])

with tabs[0]:
    show_data_tab()