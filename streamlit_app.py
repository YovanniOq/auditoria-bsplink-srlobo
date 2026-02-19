import streamlit as st
import pandas as pd
import os

# 1. Configuración de Marca Eurekis
st.set_page_config(page_title="Auditoría Eurekis | Digitalized Finance", layout="wide")

# Encabezado con Simetría Total (Ajuste de Pintura)
col1, col2 = st.columns([1, 4])

with col1:
    # Espaciado para bajar el logo y que quede simétrico con el título
    st.markdown("<div style='padding-top: 10px;'>", unsafe_allow_html=True)
    
    # URL RAW Directa de tu repositorio (Asegúrate que el nombre en GitHub sea logo_eurekis.png)
    url_logo = "https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_eurekis.png"
    
    # Intentamos cargar desde la URL directa para evitar errores de ruta local
    st.image(url_logo, width=200)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='margin-bottom: 0;'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #808495; margin-top: 0;'>Eurekis Digitalized Finance & Big Data | Proyecto World2fly</p>", unsafe_allow_html=True)

st.divider()

# 2. Lógica de Carga de Datos (Histórico Mensual)
@st.cache_data
def cargar_datos_nube():
    url_ventas = "https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/ventas.xlsx"
    try:
        data = pd.read_excel(url_ventas)
        data.columns = [str(c).strip().upper() for c in data.columns]
        if 'FECHA VENTA' in data.columns:
            data['FECHA VENTA'] = pd.to_datetime(data['FECHA VENTA'], errors='coerce')
            # Extraer el nombre del mes para el filtro lateral
            data['MES_NOMBRE'] = data['FECHA VENTA'].dt.month_name()
        return data
    except:
        return None

df_raw = cargar_datos_nube()

# Si falla la nube, permitir carga manual
if df_raw is None:
    st.warning("⚠️ No se detectó 'ventas.xlsx' en la nube. Carga manual:")
    archivo_manual = st.file_uploader("Subir ventas.xlsx", type=['xlsx'])
    if archivo_manual:
        df_raw = pd.read_excel(archivo_manual)
        df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]

# 3. Procesamiento y Filtros (Enero + Febrero)
if df_raw is not None:
    # Filtro en barra lateral
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

    # 4. Dashboard Ejecutivo con % de Eficiencia
    st.subheader(f"📊 Certificación Mensual: {', '.join(filtro_mes)}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total a Reclamar", f"{total_recuperar:,.2f} €")
    m4.metric("% Recuperación", f"{porcentaje:.2f}%")

    st.divider()
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO', 'MES_NOMBRE']], 
                 use_container_width=True, hide_index=True)
    
    # Exportación
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Eurekis", data=csv, file_name='Auditoria_Eurekis.csv')
