import streamlit as st
import os
import zipfile
import pandas as pd
import re

st.set_page_config(page_title="Auditoría Sr Lobo", layout="wide")
st.title("📊 Auditoría de Reembolsos - Eurekis")

# Ruta con guiones bajos tal como confirmaste
PATH_BASE = r'C:\Auditoria_Eurekis'
CARPETAS = ['Data_Ventas_2025', 'Data_Ventas_2026']

def limpiar(txt):
    return re.sub(r'\D', '', str(txt)).lstrip('0')[-10:]

if st.button('🚀 EJECUTAR PROCESAMIENTO'):
    reembolsos = []
    
    for carpeta in CARPETAS:
        ruta_full = os.path.join(PATH_BASE, carpeta)
        if not os.path.exists(ruta_full):
            st.error(f"❌ Carpeta no encontrada: {ruta_full}")
            continue
        
        st.write(f"Procesando: {carpeta}...")
        archivos = [f for f in os.listdir(ruta_full) if f.lower().endswith('.zip')]
        
        for file in archivos:
            try:
                with zipfile.ZipFile(os.path.join(ruta_full, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            for l in lines:
                                if l.startswith('BKS') and 'RFND' in l:
                                    reembolsos.append({
                                        'Ticket': limpiar(l[24:37]),
                                        'Agencia': l[37:44].strip(),
                                        'Fecha': l[11:17],
                                        'Archivo': file
                                    })
            except: continue

    if reembolsos:
        df = pd.DataFrame(reembolsos).drop_duplicates()
        st.success(f"✅ Se han recuperado {len(df)} registros.")
        st.dataframe(df)
        st.download_button("📥 Descargar Reporte CSV", df.to_csv(index=False), "Auditoria_Eurekis.csv")
    else:
        st.warning("⚠️ No se detectaron datos. Revisa que los archivos ZIP contengan información.")
