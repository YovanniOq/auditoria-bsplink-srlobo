import os
import zipfile
import pandas as pd
import re

# RUTAS BASADAS EN TUS GUIONES BAJOS
PATH_BASE = r'C:\Auditoria_Eurekis'
CARPETAS = ['Data_Ventas_2025', 'Data_Ventas_2026']

def limpiar(txt):
    return re.sub(r'\D', '', str(txt)).lstrip('0')[-10:]

def parse_monto(val):
    if not val or val.strip() == "": return 0.0
    mapping = {'{':0,'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'}':0,'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9}
    val = val.strip()
    if not val: return 0.0
    last_char = val[-1]
    if last_char in mapping:
        digit = mapping[last_char]
        sign = -1 if last_char in '}JKLMNOPQR' else 1
        return sign * (int(val[:-1]) * 10 + digit) / 100.0
    return float(val) / 100.0 if str(val).isdigit() else 0.0

print("--- REINICIANDO MOTOR INTEGRAL (RECUPERANDO AUDITORÍA PRINCIPAL) ---")

reembolsos_totales = []  # LA AUDITORÍA PRINCIPAL (485+ casos)
infracciones_cupon2 = [] # EL ADICIONAL (Infracción de uso)

for carpeta in CARPETAS:
    ruta_full = os.path.join(PATH_BASE, carpeta)
    if not os.path.exists(ruta_full):
        continue
    
    print(f"Escaneando datos en: {carpeta}...")
    for root, _, files in os.walk(ruta_full):
        for file in files:
            if file.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as z:
                        for name in z.namelist():
                            with z.open(name) as f:
                                lineas = f.read().decode('latin-1', errors='ignore').splitlines()
                                t_info, t_cpns = {}, {}
                                
                                for l in lineas:
                                    # Captura de datos básicos del reembolso
                                    if l.startswith('BKS') and 'RFND' in l:
                                        t = limpiar(l[24:37])
                                        r = limpiar(l[44:58])
                                        t_info[t] = {
                                            'RTDN': r, 'Agencia': l[37:44].strip(),
                                            'Monto': parse_monto(l[50:61]), 'Fecha': l[11:17], 'ZIP': file
                                        }
                                        t_cpns[t] = set()
                                    
                                    # Captura de cupones para el análisis de uso
                                    if l.startswith('BAR'):
                                        tb = limpiar(l[24:37])
                                        cp = l[37:38].strip()
                                        if tb in t_cpns and cp.isdigit():
                                            t_cpns[tb].add(int(cp))

                                for tk, cn in t_cpns.items():
                                    if tk not in t_info: continue
                                    info = t_info[tk]
                                    
                                    # 1. AUDITORÍA PRINCIPAL: Reembolsos Totales (1-2-3-4 o Directos)
                                    # Aquí es donde recuperamos tus 485 casos
                                    if cn == {1, 2, 3, 4} or (info['RTDN'] == tk):
                                        reembolsos_totales.append({
                                            'Ticket': tk, 'Agencia': info['Agencia'], 
                                            'Monto': info['Monto'], 'Fecha': info['Fecha'], 'Archivo': info['ZIP']
                                        })
                                    
                                    # 2. AUDITORÍA ADICIONAL: Solo si NO incluye el cupón 1
                                    elif 1 not in cn and len(cn) > 0:
                                        infracciones_cupon2.append({
                                            'Ticket': tk, 'Agencia': info['Agencia'], 
                                            'Cupones': sorted(list(cn)), 'Monto': info['Monto'],
                                            'Motivo': 'ADM: Posible Cupón 1 ya volado'
                                        })
                except: continue

# EXPORTACIÓN DE RESULTADOS
if reembolsos_totales:
    df_totales = pd.DataFrame(reembolsos_totales).drop_duplicates(subset=['Ticket', 'Monto'])
    df_totales.to_csv(os.path.join(PATH_BASE, 'Auditoria_Principal_TOTALES.csv'), index=False)
    print(f"✅ Auditoría Principal recuperada: {len(df_totales)} registros.")

if infracciones_cupon2:
    df_adic = pd.DataFrame(infracciones_cupon2).drop_duplicates(subset=['Ticket', 'Monto'])
    df_adic.to_csv(os.path.join(PATH_BASE, 'Auditoria_ADICIONAL_Cupon2.csv'), index=False)
    print(f"✅ Auditoría Adicional completada: {len(df_adic)} registros.")

print("\n--- PROCESO FINALIZADO CON ÉXITO ---")
