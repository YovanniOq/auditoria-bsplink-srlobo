import streamlit as st
import pandas as pd
import base64
import os

# 1. Configuración de Marca y Página
st.set_page_config(page_title="Auditoría Eurekis | Digitalized Finance", layout="wide")

# Estilo Personalizado de Colores (Azul Eurekis y Turquesa)
st.markdown("""
    <style>
    .titulo-eurekis { color: #003366; font-weight: bold; margin-bottom: 0px; }
    .subtitulo-eurekis { color: #00C2B2; font-size: 20px; font-weight: 500; margin-top: 0px; }
    .metric-label { color: #003366 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. Encabezado Simétrico (Pintura y Centrado)
col1, col2 = st.columns([1, 4])

with col1:
    # Ajustamos el padding-top para centrar el logo verticalmente con el título
    st.markdown("<div style='padding-top: 35px;'>", unsafe_allow_html=True)
    logo_file = "Logo.png"
    if os.path.exists(logo_file):
        encoded_logo = get_base64(logo_file)
        st.markdown(f'<img src="data:image/png;base64,{encoded_logo}" width="180">', unsafe_allow_html=True)
    else:
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/Logo.png", width=180)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 class='titulo-eurekis'>Auditoría de Eurekis | <span style='color:#00C2B2'>Digitalized Finance</span></h1>", unsafe_allow_html=True)
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
    # Filtros laterales estilizados
    st.sidebar.markdown("<h2 style='color:#003366;'>Configuración</h2>", unsafe_allow_html=True)
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

    # KPIs
    total_recuperar = df_adms['MONTO_ADM'].sum()
    porcentaje = (total_recuperar / df[TOTAL].abs().sum() * 100) if df[TOTAL].abs().sum() > 0 else 0

    # 4. Dashboard con Contraste de Color
    st.markdown(f"<h3 style='color:#003366;'>📊 Certificación Mensual: <span style='color:#00C2B2;'>{', '.join(filtro_mes)}</span></h3>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos Detectados", len(df_adms))
    m3.metric("Total a Reclamar", f"{total_recuperar:,.2f} €")
    m4.metric("% Recuperación", f"{porcentaje:.
