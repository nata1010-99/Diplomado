import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr
from cargar_datos_secop import get_df_raw
import unidecode
import re  # ✅ Para reemplazo con expresiones regulares

df_raw = get_df_raw(limit=50000)  

def normalizar_nombre_departamento(nombre):
    if pd.isna(nombre):
        return ""
    nombre = unidecode.unidecode(nombre)
    nombre = nombre.lower().strip()
    nombre = nombre.replace("-", " ").replace("_", " ").replace(".", "")
    nombre = re.sub(r"\s+", " ", nombre)  # ✅ Reemplazo de múltiples espacios
    return nombre

def show_visualizations_tab():
    st.header("📊 Visualizaciones de contratación pública")

    # ---------- Cargar población ----------
    ruta_2005 = "../Datos/Info_2005_2019.xlsx"
    ruta_2020 = "../Datos/Info_2020_2035.xlsx"
    df_2005_2019 = pd.read_excel(ruta_2005)
    df_2020_2035 = pd.read_excel(ruta_2020)
    df_pob = pd.concat([df_2005_2019, df_2020_2035], ignore_index=True)
    df_pob = df_pob[df_pob['ÁREA GEOGRÁFICA'].str.lower() == 'total']
    df_pob = df_pob[df_pob['AÑO'].notna()]
    df_pob['AÑO'] = df_pob['AÑO'].astype(int)

    # ---------- Tasa de contratos por 1.000 habitantes ----------
    st.subheader("🏙️ ¿Qué departamentos presentan mayor tasa de contratos por cada 1.000 habitantes?")

    año_reciente = df_pob['AÑO'].max()
    df_pob_ult = df_pob[df_pob['AÑO'] == año_reciente]
    df_pob_departamento = df_pob_ult.groupby('DPNOM', as_index=False)['Población'].sum()
    df_pob_departamento.rename(columns={'DPNOM': 'departamento_entidad', 'Población': 'poblacion_2035'}, inplace=True)
    df_pob_departamento['departamento_entidad'] = df_pob_departamento['departamento_entidad'].apply(normalizar_nombre_departamento)

    df_filtrado = df_raw[df_raw['departamento_entidad'].notna()]
    df_filtrado = df_filtrado[df_filtrado['departamento_entidad'].str.strip() != ""]
    
    df_contratos_por_dep = df_filtrado.groupby('departamento_entidad', as_index=False).size()
    df_contratos_por_dep.rename(columns={'size': 'num_contratos'}, inplace=True)
    df_contratos_por_dep['departamento_entidad'] = df_contratos_por_dep['departamento_entidad'].apply(normalizar_nombre_departamento)

    df_tasa = pd.merge(df_contratos_por_dep, df_pob_departamento, on='departamento_entidad', how='left')
    df_tasa['contratos_por_1000_hab'] = (df_tasa['num_contratos'] / df_tasa['poblacion_2035']) * 1000
    df_top = df_tasa.sort_values(by='contratos_por_1000_hab', ascending=False).head(10)

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_top, x='contratos_por_1000_hab', y='departamento_entidad', palette='viridis', ax=ax1)
    ax1.set_title("Top 10 departamentos con mayor tasa de contratación por 1.000 habitantes")
    ax1.set_xlabel("Contratos por cada 1.000 habitantes")
    ax1.set_ylabel("Departamento")
    st.pyplot(fig1)

    # ---------- Población vs número de contratos ----------
    st.subheader("📈 ¿Se corresponde el volumen de contratación con la población?")

    df_pob_2035 = df_pob[df_pob['AÑO'] == 2035]
    df_poblacion = df_pob_2035.groupby('DPNOM')['Población'].sum().reset_index()
    df_poblacion.rename(columns={'DPNOM': 'departamento_entidad', 'Población': 'poblacion_2035'}, inplace=True)
    df_poblacion['departamento_entidad'] = df_poblacion['departamento_entidad'].apply(normalizar_nombre_departamento)

    df_contratos_pob = df_contratos_por_dep.merge(df_poblacion, on='departamento_entidad', how='inner')

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_contratos_pob, x='poblacion_2035', y='num_contratos', ax=ax2)
    ax2.set_title("Relación entre población y número de contratos por departamento")
    ax2.set_xlabel("Población estimada en 2035")
    ax2.set_ylabel("Número de contratos")
    ax2.grid(True)
    st.pyplot(fig2)

    if len(df_contratos_pob) >= 2:
        corr, _ = pearsonr(df_contratos_pob['poblacion_2035'], df_contratos_pob['num_contratos'])
        st.markdown(f"📈 **Correlación de Pearson**: `{corr:.2f}`")
    else:
        st.warning("⚠️ No hay suficientes datos para calcular la correlación. Verifica que los nombres de los departamentos coincidan entre archivos.")

    st.markdown("""
    > El gráfico muestra una correlación positiva fuerte entre la población y el número de contratos.
    > Los departamentos con más población tienden a tener más contratos. Sin embargo, se observan outliers
    > como Bogotá o Antioquia con volúmenes desproporcionadamente altos.
    """)

    # ---------- Evolución mensual del valor contratado ----------
    st.subheader("📅 Evolución mensual del valor total contratado por tipo de contrato")

    df = df_raw.copy()
    df['tipo_de_contrato'] = df['tipo_de_contrato'].fillna("").str.strip().str.lower()

    df['fecha_inicio_ejecuci_n'] = pd.to_datetime(df['fecha_inicio_ejecuci_n'], errors='coerce')
    df = df[df['fecha_inicio_ejecuci_n'].notna()]
    df['anio_mes'] = df['fecha_inicio_ejecuci_n'].dt.to_period('M')

    df_evolucion = df.groupby(['anio_mes', 'tipo_de_contrato'])['valor_contrato'].sum().reset_index()
    df_evolucion['anio_mes'] = df_evolucion['anio_mes'].dt.to_timestamp()
    df_evolucion_reciente = df_evolucion[df_evolucion['anio_mes'].dt.year >= 2018]

    fig3, ax3 = plt.subplots(figsize=(14, 7))
    sns.lineplot(data=df_evolucion_reciente, x='anio_mes', y='valor_contrato', hue='tipo_de_contrato', ax=ax3, marker='o')
    ax3.set_title("Evolución mensual del valor total contratado por tipo de contrato (desde 2018)")
    ax3.set_xlabel("Fecha")
    ax3.set_ylabel("Valor total contratado")
    ax3.legend(title='Tipo de contrato', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    st.markdown("""
    - 📉 **Fluctuaciones claras**: Se observan altibajos marcados en los valores mensuales.
    - 📌 **Picos en ciertos meses**: Probablemente relacionados con cierres fiscales o planes de inversión.
    - 😷 **Caídas notables**: Posiblemente por pandemia, recortes presupuestales o cambios administrativos.
    """)

    # ---------- Totales por tipo de contrato ----------
    st.subheader("💰 ¿Qué tipo de contratos concentran mayores valores?")

    totales_por_tipo = df_evolucion.groupby('tipo_de_contrato')['valor_contrato'].sum().sort_values(ascending=False)
    st.bar_chart(totales_por_tipo)

    st.markdown("""
    - 🏆 **Prestación de servicios** domina ampliamente el valor total contratado (más de 10.7 billones).
    - 🛒 Le siguen **compraventa** y **suministro**, con valores también muy elevados.
    - 🔨 Otros tipos como **obra**, **crédito** y **consultoría** tienen montos menores en comparación.
    """)

    # ---------- Mostrar tabla pivote opcional ----------
    with st.expander("🔍 Ver tabla mensual por tipo de contrato"):
        df_pivot = df_evolucion_reciente.pivot(index='anio_mes', columns='tipo_de_contrato', values='valor_contrato').fillna(0)
        st.dataframe(df_pivot, use_container_width=True)
