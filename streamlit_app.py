import streamlit as st
import pandas as pd

# 1. Configuración de la página y Estilo
st.set_page_config(page_title="Auditoría de Reembolsos | Sr Lobo", layout="wide")

# 2. Encabezado con Logo y Título Profesional
col1, col2 = st.columns([1, 4])

with col1:
    # Intenta cargar el logo localmente desde tu repositorio
    try:
        st.image("logo_srlobo.png", width=220)
    except:
        # Si GitHub tarda en reconocer el archivo, usa el link directo
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo_srlobo.png", width=220)

with col2:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos - World2fly")
    st.caption("Revenue Accounting: Auditoría de Tasa L8 y Penalidades No-Show")

st.divider()

# 3. Motor de Auditoría Inteligente
archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Mapeo de columnas (asegúrate que coincidan con tu Excel)
    TKT, L8, TOTAL = 'DOCUMENT_NUMBER', 'TASA L8', 'TOTAL'
    F_VTA, F_VUE = 'FECHA VENTA', 'MARKETING_FLIGHT_DEPARTURE_DATE'

    # Limpieza de datos
    df[F_VTA] = pd.to_datetime(df[F_VTA], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[TOTAL] = pd.to_numeric(df[TOTAL], errors='coerce').fillna(0)
    df[L8] = pd.to_numeric(df[L8], errors='coerce').fillna(0)

    # Lógica de Auditoría de Precisión (No infla los montos)
    def auditar_registro(fila):
        # Caso A: No-Show (Vendido después del vuelo) -> Reclamo el total del billete
        if (fila[F_VTA] > fila[F_VUE]) and abs(fila[TOTAL]) > 100:
            return abs(fila[TOTAL]), "Penalidad No-Show"
        # Caso B: Error Tasa L8 -> Reclamo ÚNICAMENTE los 8.63 o 8.65
        elif abs(fila[L8]) > 0:
            return abs(fila[L8]), f"Diferencia Tasa L8 ({abs(fila[L8])})"
        return 0, None

    # Aplicamos el motor de cálculo
    df[['MONTO_ADM', 'MOTIVO']] = df.apply(lambda x: pd.Series(auditar_registro(x)), axis=1)
    df_adms = df[df['MONTO_ADM'] > 0].copy()

    # 4. Panel de Resultados (Métricas)
    m1, m2, m3 = st.columns(3)
    m1.metric("Billetes Auditados", len(df))
    m2.metric("Casos con ADM", len(df_adms))
    m3.metric("Total Real a Reclamar", f"{df_adms['MONTO_ADM'].sum():,.2f} €")

    # 5. Tabla Detallada para Certificación
    st.subheader("Desglose de Auditoría Certificada")
    st.dataframe(df_adms[[TKT, TOTAL, L8, 'MONTO_ADM', 'MOTIVO']], 
                 use_container_width=True, hide_index=True)

    # 6. Exportación para Sergio
    csv = df_adms.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de ADMs", data=csv, 
                       file_name='Certificacion_SrLobo_Auditoria.csv', mime='text/csv')

else:
    st.info("👋 Bienvenido. Por favor, sube el archivo 'ventas.xlsx' para iniciar la certificación de los 182 billetes.")
