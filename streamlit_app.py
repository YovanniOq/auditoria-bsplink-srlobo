import streamlit as st
import pandas as pd

# 1. Configuración Visual Profesional
st.set_page_config(page_title="Auditoría de Reembolsos", layout="wide")

# Diseño de Encabezado con Logo
col_logo, col_tit = st.columns([1, 3])
with col_logo:
    # Intenta cargar el logo si ya lo subiste a GitHub
    st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_srlobo.png", width=220)

with col_tit:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos")

st.divider()

# 2. Motor de Auditoría Inteligente (Lógica de VS Code)
archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Mapeo de columnas del Excel de 182 billetes
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VTA, F_VUE = 'FECHA VENTA', 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Conversión técnica de datos
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    # --- CÁLCULO DE RECLAMO EXACTO ---
    def auditar_fila(row):
        # Caso No-Show: Se reclama la tarifa completa por error de fecha
        if (row[F_VTA] > row[F_VUE]) and abs(row[TOTAL]) > 100:
            return abs(row[TOTAL]), "Penalidad No-Show"
        # Caso Tasa L8: SOLO se reclama el valor de la tasa (8.63/8.65)
        elif abs(row[L8]) > 0:
            return abs(row[L8]), f"Diferencia Tasa L8"
        return 0, None

    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar_fila(x)), axis=1)
    df_final = df[df['MONTO_ADM'] > 0].copy()

    # 3. Métricas de la Certificación (Idénticas a tu referencia)
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_final))
    m3.metric("Total a Reclamar", f"{df_final['MONTO_ADM'].sum():,.2f}")

    # 4. Tabla de Detalle para Sergio
    st.subheader("Desglose de Auditoría para Certificación")
    st.dataframe(df_final[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO']], 
                 use_container_width=True, hide_index=True)

    # Exportación para reporte oficial
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de ADMs", data=csv, 
                       file_name='Reporte_Auditoria_Lobo.csv', mime='text/csv')
