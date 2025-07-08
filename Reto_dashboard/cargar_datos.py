import streamlit as st
import pandas as pd
import requests

# ================================================
# Función: load_secop_data
# ================================================
def load_secop_data(limit: int = 50000) -> pd.DataFrame:
    api_url = f"https://www.datos.gov.co/resource/rpmr-utcd.json?$limit={limit}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión con la API: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")
    return pd.DataFrame()

# ================================================
# Función: show_data_tab
# ================================================
def show_data_tab():
    st.header("📥 Carga de Datos del SECOP vía API")

    st.markdown("""
    Este conjunto de datos proviene del portal [datos.gov.co](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd).

    Presiona el botón para cargar los datos directamente desde la API.
    """)

    if st.button("🔄 Cargar datos"):
        with st.spinner("Cargando desde la API..."):
            df = load_secop_data()
        if not df.empty:
            st.session_state['df'] = df
            st.success(f"¡Datos cargados exitosamente! ({len(df)} filas)")
            st.dataframe(df.head(10))
        else:
            st.warning("No se encontraron datos.")