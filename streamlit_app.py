import streamlit as st
import pandas as pd
import os

# 1. Configuración de la página
st.set_page_config(page_title="Auditoría de Reembolsos | Sr Lobo", layout="wide")

# 2. Encabezado Simétrico (Logo y Título Nivelados)
# Ajustamos el ancho de las columnas: 1 para el logo, 4 para el texto
col1, col2 = st.columns([1, 4])

with col1:
    # Eliminamos el espacio extra para que el logo suba
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=210)
    else:
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo.png", width=210)

with col2:
    # Usamos markdown para un título limpio y alineado
    st.markdown("<h1 style='margin-bottom: 0;'>Auditoría de Reembolsos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 20px; color: gray; margin-top: 0;'>Certificación de Recuperación de Fondos - World2fly</p>", unsafe_allow_html=True)

st.divider()

# 3. Zona de Carga de Información
archivo = st.file_uploader("Arrastra aquí tu archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Mapeo de columnas
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VTA, F_VUE = 'FECHA VENTA', 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Conversión de datos
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    # Lógica de Auditoría
    def auditar_fila(fila):
        if (fila[F_VTA] > fila[F_VUE]) and abs(fila[TOTAL]) > 100:
            return abs(fila[TOTAL]), "Penalidad No-Show"
        elif abs(fila[L8]) > 0:
            return abs(fila[L8]), f"Diferencia Tasa L8 ({abs(fila[L8])})"
        return 0, None

    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar_fila(x)), axis=1)
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # 4. Panel de Resultados (Métricas)
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total a Reclamar", f"{df_adms['MONTO_ADM'].sum():,.2f} €")

    # 5. Tabla Detallada
    st.subheader("Desglose de Auditoría Certificada")
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO']], 
                 use_container_width=True, hide_index=True)

    # 6. Botón de Exportación
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de ADMs", data=csv, 
                       file_name='Certificacion_SrLobo_Auditoria.csv', mime='text/csv')

else:
    st.info("👋 Por favor, sube el archivo 'ventas.xlsx' para iniciar la auditoría.")
