import streamlit as st
import pandas as pd
import base64
import os

# 1. Configuración de Marca y Página
st.set_page_config(page_title="Auditoría Eurekis | Digitalized Finance", layout="wide")

# Pintura Personalizada: Colores de Eurekis (Azul #2B57A7 y Cian #1DA6E0)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .titulo-eurekis { color: #2B57A7; font-weight: 800; margin-bottom: 0px; font-size: 42px; }
    .subtitulo-eurekis { color: #1DA6E0; font-size: 20px; font-weight: 600; margin-top: 0px; }
    [data-testid="stMetricValue"] { color: #2B57A7 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #555555 !important; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. Encabezado Simétrico (Logo Centrado y Colores)
col1, col2 = st.columns([1, 4])

with col1:
    # Bajamos el logo para centrarlo con las dos líneas de texto
    st.markdown("<div style='padding-top: 35px;'>", unsafe_allow_html=True)
    logo_file = "Logo.png"
    if os.path.exists(logo_file):
        encoded_logo = get_base64(logo_file)
        st.markdown(f'<img src="data:image/png;base64,{encoded_logo}" width="200">', unsafe_allow_html=True)
    else:
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/Logo.png", width=200)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 class='titulo-eurekis'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-eurekis'>Eurekis Digitalized Finance & Big Data | Proyecto World2fly</p>", unsafe_allow_html=True)

st.divider()

# 3. Motor de Carga Histórica
@st.cache_data
def cargar_datos_nube():
    url_ventas = "https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/ventas.xlsx"
    try:
        data = pd.read_excel(url_ventas)
        data.columns = [str(c).strip().upper() for c in data.columns]
        if 'FECHA VENTA' in data.columns:
            data['FECHA VENTA'] = pd.to_datetime(data['FECHA VENTA'], errors='coerce')
            data['MES_NOMBRE'] = data['FECHA VENTA'].dt.month_name()
        return data
    except:
        return None

df_raw = cargar_datos_nube()

if df_raw is not None:
    # Filtros laterales
    st.sidebar.markdown("<h2 style='color:#2B57A7;'>Filtros Globales</h2>", unsafe_allow_html=True)
    meses_disponibles = df_raw['MES_NOMBRE'].dropna().unique().tolist()
    filtro_mes = st.sidebar.multiselect("Seleccionar Período:", options=meses_disponibles, default=meses_disponibles)
    
    df = df_raw[df_raw['MES_NOMBRE'].isin(filtro_mes)].copy()

    # Motor de Auditoría
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VUE, F_VTA = 'MARKETING_FLIGHT_DEPARTURE_DATE', 'FECHA VENTA'
    
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    def auditar(fila):
        if (fila[F_VTA] > fila[F_VUE]) and abs(fila[TOTAL]) > 100:
            return abs(fila[TOTAL]), "Penalidad No-Show"
        elif abs(fila[L8]) > 0:
            return abs(fila[L8]), "Diferencia Tasa L8"
        return 0, None

    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar(x)), axis=1)
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # Cálculo de KPIs (Corregido)
    total_auditado = df[TOTAL].abs().sum()
    total_recuperar = df_adms['MONTO_ADM'].sum()
    porcentaje = (total_recuperar / total_auditado * 100) if total_auditado > 0 else 0

    # 4. Dashboard Ejecutivo
    st.markdown(f"<h3 style='color:#2B57A7;'>📊 Reporte Consolidado: <span style='color:#1DA6E0;'>{', '.join(filtro_mes)}</span></h3>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total a Reclamar", f"{total_recuperar:,.2f} €")
    m4.metric("% Recuperación", f"{porcentaje:.2f}%")

    st.divider()
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO', 'MES_NOMBRE']], 
                 use_container_width=True, hide_index=True)
    
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Eurekis Certificado", data=csv, file_name='Auditoria_Eurekis_W2fly.csv')
