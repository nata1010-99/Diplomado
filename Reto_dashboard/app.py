import streamlit as st
from cargar_datos_secop import show_data_tab
from visualizaciones_secop import show_visualizations_tab
from transformacion_secop import show_transformations_tab  

st.set_page_config(page_title="Dashboard SECOP", layout="wide")
st.title("📊 Dashboard SECOP - Prototipo Inicial")

# ✅ Agregar pestaña de Transformaciones
tabs = st.tabs(["📋 Carga de Datos", "📈 Visualizaciones", "🔧 Transformaciones"])

with tabs[0]:
    show_data_tab()

with tabs[1]:
    show_visualizations_tab()

with tabs[2]:
    show_transformations_tab()  

