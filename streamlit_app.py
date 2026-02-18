import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auditoría de Reembolsos", layout="wide")

# 1. Encabezado Profesional
col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("logo_srlobo.png", width=200)
    except:
        st.info("Sube 'logo_srlobo.png' a GitHub para ver el logo.")

with col2:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos")

st.divider()

# 2. Carga de Datos
archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # --- MOTOR DE AUDITORÍA ---
    # Identificamos columnas (ajustar si los nombres en el Excel cambian)
    TKT = 'DOCUMENT_NUMBER'
    L8 = 'TASA L8'
    TOTAL = 'TOTAL'
    F_VTA = 'FECHA VENTA'
    F_VUE = 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Convertir formatos
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')

    # Lógica de detección:
    # Caso A: Tasa L8 (8.63 o 8.65 detectados)
    es_l8 = df[L8].abs() > 0
    
    # Caso B: No-Show (Vendido después del vuelo y monto > 100)
    es_noshow = (df[F_VTA] > df[F_VUE]) & (df[TOTAL].abs() > 100)

    # Creamos la columna de MOTIVO
    df['MOTIVO_ADM'] = ""
    df.loc[es_l8, 'MOTIVO_ADM'] = "Tasa L8 Pendiente"
    df.loc[es_noshow, 'MOTIVO_ADM'] = "Penalidad No-Show"
    df.loc[es_l8 & es_noshow, 'MOTIVO_ADM'] = "L8 + No-Show"

    # Filtramos solo los 11 casos de interés
    df_final = df[df['MOTIVO_ADM'] != ""].copy()

    # 3. Métricas Visuales
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_final))
    m3.metric("Total a Reclamar", f"{df_final[TOTAL].abs().sum():,.2f}")

    # 4. Tabla Detallada con el Motivo (Lo que faltaba)
    st.subheader("Detalle de Billetes para Reclamar")
    columnas_ver = [TKT, F_VTA, TOTAL, 'MOTIVO_ADM']
    st.dataframe(df_final[columnas_ver], use_container_width=True, hide_index=True)

    # Botón para descargar el reporte para Sergio
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de Certificación", data=csv, file_name='Certificacion_SrLobo.csv')
