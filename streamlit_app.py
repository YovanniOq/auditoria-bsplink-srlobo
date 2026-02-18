import streamlit as st
import pandas as pd

# 1. Configuración de Marca Sr Lobo
st.set_page_config(page_title="Auditoría de Reembolsos", layout="wide")

col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("logo_srlobo.png", width=200)
    except:
        st.info("Sube 'logo_srlobo.png' a GitHub")

with col2:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos")

st.divider()

# 2. Motor de Auditoría con Precisión Contable
archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Columnas clave
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VTA, F_VUE = 'FECHA VENTA', 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Limpieza técnica
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    # Lógica de cálculo: No-Show vs Tasa L8
    def calcular_auditoria(row):
        # Caso 1: No-Show (Venta posterior al vuelo y monto significativo)
        if (row[F_VTA] > row[F_VUE]) and abs(row[TOTAL]) > 100:
            return abs(row[TOTAL]), "Penalidad No-Show (Tarifa Completa)"
        # Caso 2: Tasa L8 (Solo reclamamos la diferencia de la tasa)
        elif abs(row[L8]) > 0:
            return abs(row[L8]), f"Diferencia Tasa L8 ({abs(row[L8])})"
        return 0, None

    # Aplicamos el motor de cálculo
    df[['MONTO_ADM', 'JUSTIFICACION']] = df.apply(lambda x: pd.Series(calcular_auditoria(x)), axis=1)

    # Filtramos solo los 11 casos reales
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # 3. Panel de Control (Dashboard)
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total Real a Reclamar", f"{df_adms['MONTO_ADM'].sum():,.2f}")

    # 4. Tabla Detallada para World2fly
    st.subheader("Desglose de Billetes para Reclamación")
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'JUSTIFICACION']], 
                 use_container_width=True, hide_index=True)

    # 5. Exportación Certificada
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de Certificación", data=csv, 
                       file_name='Certificacion_Reclamos_SrLobo.csv', mime='text/csv')
