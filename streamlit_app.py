import streamlit as st
import pandas as pd

st.title("🐺 Auditoría Sr Lobo")
st.write("Si ves esto, el servidor funciona correctamente.")

archivo = st.file_uploader("Cargar archivo ventas.xlsx", type=['xlsx'])

if archivo:
    try:
        df = pd.read_excel(archivo)
        st.success(f"Éxito: {len(df)} registros cargados.")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
