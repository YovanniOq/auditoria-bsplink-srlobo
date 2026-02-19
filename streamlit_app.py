import streamlit as st
import pandas as pd
import base64
import os

# 1. Configuración de Marca y Página
st.set_page_config(page_title="Auditoría Eurekis | Digitalized Finance", layout="wide")

# Función para cargar imagen local y evitar errores de URL
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Encabezado con Simetría (Ajuste de Pintura)
col1, col2 = st.columns([1, 4])

with col1:
    # Intentamos cargar el logo de Eurekis
    logo_file = "logo_eurekis.png"
    if os.path.exists(logo_file):
        # Si el archivo existe, lo inyectamos directamente
        encoded_logo = get_base64_of_bin_file(logo_file)
        st.markdown(
            f'<img src="data:image/png;base64,{encoded_logo}" width="200" style="padding-top: 10px;">',
            unsafe_allow_html=True
        )
    else:
        # Respaldo: Si no lo encuentra, te avisa pero no rompe el diseño
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_eurekis.png", width=200)

with col2:
    st.markdown("<h1 style='margin-bottom: 0;'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #808495; margin-top: 0;'>Eurekis Digitalized Finance & Big Data | Proyecto World2fly</p>", unsafe_allow_html=True)

st.divider()

# 2. Lógica de Carga de Datos (Histórico)
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

if df_raw is None:
    st.warning("⚠️ No se detectó 'ventas.xlsx' en la nube. Carga manual disponible:")
    archivo_manual = st.file_uploader("Subir ventas.xlsx", type=['xlsx'])
    if archivo_manual:
        df_raw = pd.read_excel(archivo_manual)
        df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]

# 3. Procesamiento y Filtros (Enero + Febrero)
if df_raw is not None:
    st.sidebar.header("Filtros de Auditoría")
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

    # Cálculo de KPIs
    total_auditado = df[TOTAL].abs().sum()
    total_recuperar = df_adms['MONTO_ADM'].sum()
    porcentaje = (total_recuperar / total_auditado * 100) if total_auditado > 0 else 0

    # 4. Dashboard Ejecutivo
    st.subheader(f"📊 Certificación Mensual: {', '.join(filtro_mes)}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total a Reclamar", f"{total_recuperar:,.2f} €")
    m4.metric("% Recuperación", f"{porcentaje:.2f}%")

    st.divider()
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO', 'MES_NOMBRE']], 
                 use_container_width=True, hide_index=True)
    
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Eurekis", data=csv, file_name='Auditoria_Eurekis.csv')
