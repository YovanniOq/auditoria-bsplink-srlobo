import streamlit as st
import os
import zipfile
import pandas as pd
import re

st.set_page_config(page_title="Auditoría Sr Lobo", layout="wide")
st.title("📊 Auditoría Integral de Reembolsos - Eurekis")

# Configuración de Rutas
PATH_BASE = r'C:\Auditoria_Eurekis'
CARPETAS = ['Data_Ventas_2025', 'Data_Ventas_2026']

def limpiar_tkt(txt):
    return re.sub(r'\D', '', str(txt)).lstrip('0')[-10:]

def parse_monto_iata(val):
    if not val or val.strip() == "": return 0.0
    # Mapeo de caracteres para montos con signo IATA (HOT files)
    mapping = {'{':0,'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
               '}':0,'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9}
    val = val.strip()
    last_char = val[-1] if val else ""
    if last_char in mapping:
        digit = mapping[last_char]
        sign = -1 if last_char in '}JKLMNOPQR' else 1
        return sign * (int(val[:-1]) * 10 + digit) / 100.0
    return float(val) / 100.0 if str(val).isdigit() else 0.0

if st.button('🚀 DISPARAR AUDITORÍA COMPLETA'):
    totales = []
    infracciones = []
    
    for carpeta in CARPETAS:
        ruta_full = os.path.join(PATH_BASE, carpeta)
        if not os.path.exists(ruta_full): continue
        
        st.write(f"Procesando: {carpeta}...")
        archivos = [f for f in os.listdir(ruta_full) if f.lower().endswith('.zip')]
        
        for file in archivos:
            try:
                with zipfile.ZipFile(os.path.join(ruta_full, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            t_info, t_cpns = {}, {}
                            
                            for l in lines:
                                # Registro BKS: Datos del Ticket y Reembolso
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = limpiar_tkt(l[24:37])
                                    t_info[t] = {
                                        'RTDN': limpiar_tkt(l[44:58]),
                                        'Agencia': l[37:44].strip(),
                                        'Monto': parse_monto_iata(l[50:61]),
                                        'Fecha': l[11:17],
                                        'Archivo': file
                                    }
                                    t_cpns[t] = set()
                                
                                # Registro BAR: Cupones afectados
                                if l.startswith('BAR'):
                                    tb = limpiar_tkt(l[24:37])
                                    cp = l[37:38].strip()
                                    if tb in t_cpns and cp.isdigit():
                                        t_cpns[tb].add(int(cp))

                            # Aplicación de Reglas de Negocio al finalizar el archivo
                            for tk, cn in t_cpns.items():
                                if tk not in t_info: continue
                                item = t_info[tk]
                                
                                # REGLA 1: Reembolso Total (Lo avanzado anteriormente)
                                if cn == {1, 2, 3, 4} or (item['RTDN'] == tk):
                                    totales.append(item)
                                
                                # REGLA 2: Infracción de Tarifa (Cupón 2 sin Cupón 1)
                                elif 1 not in cn and 2 in cn:
                                    infracciones.append({
                                        'Ticket': tk, 'Agencia': item['Agencia'], 
                                        'Monto': item['Monto'], 'Cupones': sorted(list(cn)),
                                        'Error': 'Tramo 2 reembolsado con Tramo 1 usado'
                                    })
            except: continue

    # Visualización y Descarga
    if totales or infracciones:
        st.success(f"✅ Auditoría terminada. Procesados {len(totales) + len(infracciones)} registros.")
        
        tab1, tab2 = st.tabs(["🏆 Auditoría Principal", "⚠️ Infracciones Cupones"])
        
        with tab1:
            df_t = pd.DataFrame(totales).drop_duplicates()
            st.metric("Total Reembolsos", len(df_t))
            st.dataframe(df_t)
            st.download_button("Descargar Totales CSV", df_t.to_csv(index=False), "Totales.csv")
            
        with tab2:
            df_i = pd.DataFrame(infracciones).drop_duplicates()
            st.metric("Infracciones Detectadas", len(df_i))
            st.dataframe(df_i)
            st.download_button("Descargar Infracciones CSV", df_i.to_csv(index=False), "Infracciones.csv")
