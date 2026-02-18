import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auditoría Sr Lobo", layout="wide")
st.markdown("## Auditoría de Reembolsos Directos BSPLink")
st.caption("Revenue Accounting: Certificación de Tasa L8 y Tarifas")

archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    TKT, F_REEM, F_VUE, COL_TOTAL, COL_L8 = 'DOCUMENT_NUMBER', 'FECHA VENTA', 'MARKETING_FLIGHT_DEPARTURE_DATE', 'TOTAL', 'TASA L8'
    
    df[F_REEM] = pd.to_datetime(df[F_REEM], errors='coerce')
    df[F_VUE] = pd.to_datetime(df[F_VUE], errors='coerce')
    df[COL_TOTAL] = pd.to_numeric(df[COL_TOTAL], errors='coerce').fillna(0)
    df[COL_L8] = pd.to_numeric(df[COL_L8], errors='coerce').fillna(0)

    df_res = df.groupby(TKT, as_index=False).agg({F_REEM:'first', F_VUE:'first', COL_TOTAL:'sum', COL_L8:'sum'})
    
    mask_l8 = df_res[COL_L8].abs() > 0
    mask_tarifa = (df_res[F_REEM] > df_res[F_VUE]) & (df_res[COL_TOTAL].abs() > 100)
    df_adms = df_res[mask_l8 | mask_tarifa].copy()

    df_adms['REC_TARIFA'] = df_adms.apply(lambda x: abs(x[COL_TOTAL]) if (x[F_REEM] > x[F_VUE] and abs(x[COL_TOTAL]) > 100) else 0, axis=1)
    df_adms['REC_L8'] = df_adms[COL_L8].abs()
    df_adms['TOTAL_ADM'] = df_adms['REC_TARIFA'] + df_adms['REC_L8']

    st.metric("Total a Recuperar (ADM)", f"{df_adms['TOTAL_ADM'].sum():.2f}")
    st.dataframe(df_adms[[TKT, 'REC_TARIFA', 'REC_L8', 'TOTAL_ADM']], use_container_width=True, hide_index=True)
