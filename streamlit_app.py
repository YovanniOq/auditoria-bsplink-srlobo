import streamlit as st
import os
import zipfile
import pandas as pd

st.set_page_config(page_title="Auditoría Sr Lobo", layout="wide")
st.title("📊 Auditoría de Reembolsos - Eurekis")

PATH_BASE = r'C:\Auditoria_Eurekis'
CARPETAS = ['Data_Ventas_2025', 'Data_Ventas_2026']

if st.button('🚀 EJECUTAR AUDITORÍA COMPLETA'):
    reembolsos_totales = []
    infracciones_cupon2 = []
    
    for carpeta in CARPETAS:
        ruta = os.path.join(PATH_BASE, carpeta)
        if not os.path.exists(ruta): continue
        
        st.write(f"Analizando: {carpeta}...")
        archivos = [f for f in os.listdir(ruta) if f.lower().endswith('.zip')]
        
        for file in archivos:
            try:
                with zipfile.ZipFile(os.path.join(ruta, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            t_info, t_cpns = {}, {}
                            for l in lines:
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = l[24:37].strip()[-10:]
                                    t_info[t] = {'Agencia': l[37:44].strip(), 'Monto': l[50:61].strip(), 'Fecha': l[11:17]}
                                    t_cpns[t] = set()
                                if l.startswith('BAR'):
                                    tb = l[24:37].strip()[-10:]
                                    cp = l[37:38].strip()
                                    if tb in t_cpns and cp.isdigit(): t_cpns[tb].add(int(cp))

                            for tk, cn in t_cpns.items():
                                if tk not in t_info: continue
                                # Regla 1: Auditoría que ya teníamos avanzada
                                if cn == {1, 2, 3, 4} or len(cn) == 0:
                                    reembolsos_totales.append({'Ticket': tk, 'Agencia': t_info[tk]['Agencia'], 'Monto': t_info[tk]['Monto'], 'Fecha': t_info[tk]['Fecha']})
                                # Regla 2: Adicional de Cupón 2
                                elif 1 not in cn and 2 in cn:
                                    infracciones_cupon2.append({'Ticket': tk, 'Agencia': t_info[tk]['Agencia'], 'Monto': t_info[tk]['Monto'], 'Cupones': sorted(list(cn))})
            except: continue

    st.success("✅ ¡Proceso Terminado!")
    st.subheader(f"🏆 Auditoría Principal: {len(reembolsos_totales)} registros encontrados")
    st.dataframe(pd.DataFrame(reembolsos_totales).drop_duplicates())
    
    st.subheader(f"⚠️ Infracciones Cupón 2: {len(infracciones_cupon2)} casos detectados")
    st.dataframe(pd.DataFrame(infracciones_cupon2).drop_duplicates())
