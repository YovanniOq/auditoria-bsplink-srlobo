import streamlit as st
import pandas as pd
import os

# 1. Configuración de Marca Eurekis
st.set_page_config(page_title="Auditoría Eurekis | Digitalized Finance", layout="wide")

# Encabezado Simétrico (Ajustado para el logo de Eurekis)
col1, col2 = st.columns([1, 4])
with col1:
    # Espaciado superior para alineación perfecta
    st.markdown("<div style='padding-top: 20px;'>", unsafe_allow_html=True)
    # Cambiamos la búsqueda al nuevo nombre del archivo: logo_eurekis.png
    logo_path = "logo_eurekis.png" 
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        # Intento de respaldo con URL (asegúrate de que el nombre coincida en GitHub)
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_eurekis.png", width=200)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='margin-bottom: 0;'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: gray; margin-top: 0;'>Eurekis Digitalized Finance & Big Data | Proyecto World2fly</p>", unsafe_allow_html=True)

st.divider()

# 2. Lógica de Carga de Datos
@st.cache_data
def cargar_datos(source):
    try:
        data = pd.read_excel(source)
        data.columns = [str(c).strip().upper() for c in data.columns]
        if 'FECHA VENTA' in data.columns:
            data['FECHA VENTA'] = pd.to_datetime(data['FECHA VENTA'], errors='coerce')
            data['MES_NOMBRE'] = data['FECHA VENTA'].dt.month_name()
        return data
    except:
        return None

url_nube = "https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/ventas.xlsx"
df_raw = cargar_datos(url_nube)

if df_raw is None:
    st.warning("⚠️ Conexión con ventas.xlsx pendiente en la nube. Carga manual disponible:")
    archivo_manual = st.file_uploader("Cargar archivo de ventas", type=['xlsx'])
    if archivo_manual:
        df_raw = cargar_datos(archivo_manual)

# 3. Procesamiento y Filtros por Mes
if df_raw is not None:
    st.sidebar.header("Filtros de Auditoría")
    meses = df_raw['MES_NOMBRE'].dropna().unique().tolist()
    filtro_mes = st.sidebar.multiselect("Seleccionar Meses:", options=meses, default=meses)
    
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
            return abs(fila[L8]), f"Diferencia Tasa L8"
        return 0, None

    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar(x)), axis=1)
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # Cálculo de % de Efectividad
    monto_total_auditado = df[TOTAL].abs().sum()
    monto_recuperado = df_adms['MONTO_ADM'].sum()
    porcentaje_recuperacion = (monto_recuperado / monto_total_auditado * 100) if monto_total_auditado > 0 else 0

    # 4. Dashboard Ejecutivo (4 métricas)
    st.subheader(f"📊 Certificación de Recuperación: {', '.join(filtro_mes)}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Billetes Auditados", f"{len(df)}")
    m2.metric("Casos con ADM", f"{len(df_adms)}")
    m3.metric("Total a Reclamar", f"{monto_recuperado:,.2f} €")
    m4.metric("% Recuperación", f"{porcentaje_recuperacion:.2f}%")

    st.divider()
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO', 'MES_NOMBRE']], 
                 use_container_width=True, hide_index=True)
    
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Eurekis", data=csv, file_name='Auditoria_Eurekis_W2fly.csv')
