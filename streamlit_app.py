import streamlit as st
import pandas as pd
import os

# 1. Configuración de la página (Pestaña del navegador)
st.set_page_config(page_title="Auditoría de Reembolsos | Sr Lobo", layout="wide")

# 2. Encabezado Profesional (Logo y Títulos)
col1, col2 = st.columns([1, 3])

with col1:
    # Espaciado para bajar el logo un poco y que no quede pegado al techo
    st.write("##") 
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)
    else:
        # Respaldo por si falla la ruta local
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo.png", width=220)

with col2:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos - World2fly")
    st.caption("Revenue Accounting: Análisis de Tasa L8 y Penalidades No-Show")

st.divider()

# 3. Zona de Carga de Datos
st.subheader("📁 Carga de Información")
archivo = st.file_uploader("Arrastra aquí tu archivo de ventas.xlsx", type=['xlsx'])

if archivo:
    # Lectura del Excel
    df = pd.read_excel(archivo)
    
    # Limpieza de nombres de columnas (quitar espacios y poner en mayúsculas)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Mapeo de columnas clave
    TKT = 'DOCUMENT_NUMBER'
    L8 = 'TASA L8'
    TOTAL = 'TOTAL'
    F_VTA = 'FECHA VENTA'
    F_VUE = 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Conversión técnica de datos (Fechas y Números)
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    # --- LÓGICA DE AUDITORÍA DE PRECISIÓN ---
    def auditar_fila(fila):
        # Caso A: No-Show (Vendido después del vuelo y monto relevante)
        if (fila[F_VTA] > fila[F_VUE]) and abs(fila[TOTAL]) > 100:
            return abs(fila[TOTAL]), "Penalidad No-Show (Total)"
        
        # Caso B: Error Tasa L8 (Solo reclamamos la diferencia de 8.63 o 8.65)
        elif abs(fila[L8]) > 0:
            return abs(fila
