import streamlit as st
import os
import zipfile
import pandas as pd
import re

st.set_page_config(page_title="Auditoría Sr Lobo BPO", layout="wide")
st.title("📊 Sistema de Auditoría de Reembolsos - Eurekis")

PATH_BASE = r'C:\Auditoria_Eurekis'
CARPETAS = ['Data_Ventas_2025', 'Data_Ventas_2026']

def limpiar(txt):
    return re.sub(r'\D', '', str(txt)).lstrip('0')[-10:]

def parse_monto(val):
    if not val or val.strip() == "": return 0.0
    mapping = {'{':0,'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'}':0,'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9}
    val = val.strip()
    last_char = val[-1] if val else ""
    if last_char in mapping:
        digit = mapping[last_char]
        sign = -1 if last_char in '}JKLMNOPQR' else 1
        return sign * (int(val[:-1]) * 10 + digit) / 100.0
    return float(val) / 100.0 if str(val).isdigit() else 0.0

if st.button('🚀 Disparar Auditoría Integral'):
    reembolsos_totales = []
    infracciones_cupon2 = []
    
    progreso = st.progress(0)
    status_text = st.empty()

    for i, carpeta in enumerate(CARPETAS):
        ruta_full = os.path.join(PATH_BASE, carpeta)
        if not os.path.exists(ruta_full):
            continue
        
        status_text.text(f"Analizando {carpeta}...")
        archivos = [f for f in os.listdir(ruta_full) if f.lower().endswith('.zip')]
        
        for file in archivos:
            try:
                with zipfile.ZipFile(os.path.join(ruta_full, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            t_info, t_cpns = {}, {}
                            for l in lines:
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = limpiar(l[24:37])
                                    t_info[t] = {'RTDN': limpiar(l[44:58]), 'Agencia': l[37:44].strip(), 'Monto': parse_monto(l[50:61]), 'Fecha': l[11:17]}
                                    t_cpns[t] = set()
                                if l.startswith('BAR'):
                                    tb = limpiar(l[24:37])
                                    cp = l[37:38].strip()
                                    if tb in t_cpns and cp.isdigit(): t_cpns[tb].add(int(cp))

                            for tk, cn in t_cpns.items():
                                if tk not in t_info: continue
                                info = t_info[tk]
                                if cn == {1, 2, 3, 4} or (info['RTDN'] == tk):
                                    reembolsos_totales.append({'Ticket': tk, 'Agencia': info['Agencia'], 'Monto': info['Monto'], 'Fecha': info['Fecha']})
                                elif 1 not in cn and 2 in cn:
                                    infracciones_cupon2.append({'Ticket': tk, 'Agencia': info['Agencia'], 'Cupones': str(sorted(list(cn))), 'Monto': info['Monto']})
            except: continue
        progreso.progress((i + 1) / len(CARPETAS))

    st.success("✅ ¡Auditoría completada!")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Totales")
        df1 = pd.DataFrame(reembolsos_totales).drop_duplicates()
        st.write(f"Encontrados: {len(df1)}")
        st.dataframe(df1)
    with c2:
        st.subheader("⚠️ Cupón 2")
        df2 = pd.DataFrame(infracciones_cupon2).drop_duplicates()
        st.write(f"Encontrados: {len(df2)}")
        st.dataframe(df2)
