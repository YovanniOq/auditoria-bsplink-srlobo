import streamlit as st
import pandas as pd
import os

# 1. Configuración de la página
st.set_page_config(page_title="Auditoría de Reembolsos | Sr Lobo", layout="wide")

# 2. Encabezado con Logo (Ajustado a logo.png)
col1, col2 = st.columns([1, 4])

with col1:
    # Ahora buscamos el nombre exacto que tienes en GitHub
    logo_path = "logo.png"
    
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)
    else:
        # Intento de respaldo con la URL directa de tu repositorio
        st.image("https://raw.githubusercontent.com/YovanniOq/auditoria-bsplink-srlobo/main/logo.png", width=220)

with col2:
    st.markdown("# Auditoría de Reembolsos")
    st.markdown("### Certificación de Recuperación de Fondos - World2fly")
