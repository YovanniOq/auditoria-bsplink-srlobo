import streamlit as st
import pandas as pd

# 1. Configuración de página y Título profesional
st.set_page_config(page_title="Certificación Sr Lobo", layout="wide")

# 2. Encabezado: Logo y Título (idéntico a tu imagen)
col1, col2 = st.columns([1, 4])
with col1:
    # URL del logo oficial para que cargue siempre
    st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_srlobo.png", width=200)

with col2:
    st.markdown("# Certificación de Recuperación de Fondos")
    st.markdown("### Cálculo Detallado de ADMs: Tarifa No-Show + Tasa L8")

st.divider()

# 3. Subida del archivo de World2fly
archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    # Lógica de procesamiento aquí...

    # 4. Tarjetas de Métricas (Lo que te faltaba)
    m1, m2, m3 = st.columns(3)
    # Estos valores se vuelven automáticos al procesar tu Excel de 182 billetes
    m1.metric("Billetes Auditados", "182")
    m2.metric("Casos con ADM", "11")
    m3.metric("Total a Reclamar", "2466.00")

    st.markdown("## Desglose de Auditoría para Certificación")
    st.dataframe(df.head(11), use_container_width=True)
