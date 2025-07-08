import streamlit as st
import pandas as pd
import requests

# ===========================================================
# FUNCION: Cargar datos desde SECOP Integrado
# ===========================================================
def load_data_from_api(limit: int = 1000) -> pd.DataFrame:
    """
    Carga datos desde la API de SECOP Integrado (datos.gov.co).
    Args:
        limit (int): Límite de registros (por defecto 1000 para pruebas).
    Returns:
        pd.DataFrame: DataFrame con los datos cargados o vacío si falla.
    """
    api_url = f"https://www.datos.gov.co/resource/rpmr-utcd.json?$limit={limit}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al conectar con la API: {e}")
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
    return pd.DataFrame()

# ===========================================================
# FUNCION: Mostrar pestaña de carga de datos
# ===========================================================
def show_data_tab():
    st.header("📥 Carga de Datos desde SECOP Integrado")

    st.markdown("""
    Este conjunto de datos proviene del portal [datos.gov.co](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd).
    
    Haz clic en el botón para obtener datos directamente desde la API de **SECOP Integrado**.
    """)

    if st.button("🔄 Cargar datos"):
        with st.spinner("Cargando datos desde la API de SECOP..."):
            df_raw = load_data_from_api()

        if not df_raw.empty:
            st.session_state['df_raw'] = df_raw
            st.success(f"✅ ¡Datos cargados exitosamente! ({len(df_raw)} filas)")
            st.dataframe(df_raw.head(10))
        else:
            st.warning("⚠️ No se encontraron datos o ocurrió un error.")
    else:
        st.info("Haz clic en el botón para cargar los datos.")
