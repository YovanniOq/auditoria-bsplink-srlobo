import streamlit as st
import pandas as pd
import os

# 1. Configuración de Marca y Página
st.set_page_config(page_title="Auditoría Sr Lobo | Histórico", layout="wide")

# Encabezado Simétrico
col1, col2 = st.columns([1, 4])
with col1:
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=210)
    else:
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo.png", width=210)

with col2:
    st.markdown("<h1 style='margin-top: 10px; margin-bottom: 0;'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: gray; margin-top: 0;'>Panel de Control Histórico - World2fly</p>", unsafe_allow_html=True)

st.divider()

# 2. Carga Automática desde GitHub
@st.cache_data
def cargar_datos():
    url = "https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/ventas.xlsx"
    try:
        data = pd.read_excel(url)
        # Estandarizar columnas
        data.columns = [str(c).strip().upper() for c in data.columns]
        # Limpieza de fechas y creación de columna de Mes
        fecha_col = 'FECHA VENTA'
        data[fecha_col] = pd.to_datetime(data[fecha_col], errors='coerce')
        # Crear nombre de mes en español para el filtro
        data['MES'] = data[fecha_col].dt.month_name(locale='es_ES')
        return data
    except Exception as e:
        return None

df_raw = cargar_datos()

if df_raw is not None:
    # --- FILTROS EN BARRA LATERAL (Sidebar) ---
    st.sidebar.header("Filtros de Auditoría")
    meses_disponibles = df_raw['MES'].dropna().unique().tolist()
    seleccion_mes = st.sidebar.multiselect("Seleccionar Mes(es):", 
                                           options=meses_disponibles, 
                                           default=meses_disponibles)

    # Filtrar el DataFrame según la selección
    df = df_raw[df_raw['MES'].isin(seleccion_mes)].copy()

    # --- MOTOR DE AUDITORÍA ---
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VUE = 'MARKETING_FLIGHT_DEPARTURE_DATE'
    F_VTA = 'FECHA VENTA'

    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    def auditar(fila):
        if (fila[F_VTA] > fila[F_VUE]) and abs(fila[TOTAL]) > 100:
            return abs(fila[TOTAL]), "Penalidad No-Show"
        elif abs(fila[L8]) > 0:
            return abs(fila[L8]), f"Diferencia Tasa L8"
        return 0, None

    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar(x)), axis=1)
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # --- DASHBOARD ---
    st.subheader(f"📊 Resumen de Auditoría: {', '.join(seleccion_mes)}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("ADMs Detectados", len(df_adms))
    m3.metric("Total a Reclamar (€)", f"{df_adms['MONTO_ADM'].sum():,.2f}")

    # --- TABLA Y DESCARGA ---
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO', 'MES']], 
                 use_container_width=True, hide_index=True)

    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Seleccionado", data=csv, 
                       file_name=f'Auditoria_{"_".join(seleccion_mes)}.csv')

else:
    st.error("No se pudo conectar con el archivo en la nube.")
