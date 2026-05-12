import os
import zipfile
import pandas as pd
import re

# RUTA MAESTRA EN C:
PATH_BASE = r'C:\Auditoria_Eurekis'

# AJUSTADO CON GUIONES BAJOS SEGÚN TU CONFIRMACIÓN
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

print("--- INICIANDO MOTOR DE AUDITORÍA (SR LOBO - EUREKIS) ---")

reembolsos_totales = []
infracciones_cupon2 = []

for carpeta in CARPETAS:
    ruta_full = os.path.join(PATH_BASE, carpeta)
    if not os.path.exists(ruta_full):
        print(f"!!! Error: No se pudo encontrar la carpeta '{carpeta}'")
        continue
    
    print(f"Buscando en: {carpeta}...")
    for root, _, files in os.walk(ruta_full):
        for file in files:
            if file.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as z:
                        for name in z.namelist():
                            with z.open(name) as f:
                                lines = f.read().decode('latin-1', errors='ignore').splitlines()
                                t_info = {}
                                t_cpns = {}
                                for l in lines:
                                    if l.startswith('BKS') and 'RFND' in l:
                                        t = limpiar(l[24:37])
                                        r = limpiar(l[44:58])
                                        t_info[t] = {
                                            'RTDN': r, 'Agencia': l[37:44].strip(),
                                            'Monto': parse_monto(l[50:61]), 'Fecha': l[11:17]
                                        }
                                        t_cpns[t] = set()
                                    if l.startswith('BAR'):
                                        tb = limpiar(l[24:37])
                                        cp = l[37:38].strip()
                                        if tb in t_cpns and cp.isdigit():
                                            t_cpns[tb].add(int(cp))

                                for tk, cn in tkt_cpns.items():
                                    info = t_info[tk]
                                    # Filtro de Reembolsos Totales
                                    if cn == {1, 2, 3, 4} or (info['RTDN'] == tk and len(cn) == 0):
                                        reembolsos_totales.append({'Ticket': tk, 'Agencia': info['Agencia'], 'Monto': info['Monto'], 'Fecha': info['Fecha']})
                                    # Filtro de Infracción Cupón 2 (Ida volada, vuelta reembolsada)
                                    elif 1 not in cn and 2 in cn:
                                        infracciones_cupon2.append({'Ticket': tk, 'Agencia': info['Agencia'], 'Cupones': sorted(list(cn)), 'Monto_Fuga': info['Monto'], 'Motivo': 'ADM: Cupón 2 RFND con Cupón 1 Volado'})
                except Exception as e:
                    print(f"Error procesando {file}: {e}")

# CREACIÓN DE REPORTES FINALES
if reembolsos_totales:
    pd.DataFrame(reembolsos_totales).to_csv(os.path.join(PATH_BASE, '1_Reembolsos_Totales.csv'), index=False)
if infracciones_cupon2:
    pd.DataFrame(infracciones_cupon2).to_csv(os.path.join(PATH_BASE, '2_Infracciones_Cupón2.csv'), index=False)

print(f"--- PROCESO FINALIZADO ---")
print(f"Reporte 1 (Totales): {len(reembolsos_totales)} hallazgos.")
print(f"Reporte 2 (Infracciones): {len(infracciones_cupon2)} hallazgos.")
