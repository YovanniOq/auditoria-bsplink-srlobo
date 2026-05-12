import os
import zipfile
import pandas as pd
import re

# CONFIGURACIÓN DE RUTAS
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
    return float(val) / 100.0 if val.isdigit() else 0.0

print("--- INICIANDO MOTOR DE AUDITORÍA INTEGRAL (SR LOBO) ---")

reembolsos_totales = []
infracciones_cupon2 = []

for carpeta in CARPETAS:
    ruta_full = os.path.join(PATH_BASE, carpeta)
    if not os.path.exists(ruta_full): continue
    
    for root, _, files in os.walk(ruta_full):
        for file in files:
            if file.lower().endswith('.zip'):
                with zipfile.ZipFile(os.path.join(root, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            
                            tkt_info = {}
                            tkt_cpns = {}

                            for l in lines:
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = limpiar(l[24:37])
                                    r = limpiar(l[44:58])
                                    tkt_info[t] = {
                                        'RTDN': r,
                                        'Agencia': l[37:44].strip(),
                                        'Monto': parse_monto(l[50:61]),
                                        'Fecha': l[11:17],
                                        'Archivo': file
                                    }
                                    tkt_cpns[t] = set()

                                if l.startswith('BAR'):
                                    tb = limpiar(l[24:37])
                                    cp = l[37:38].strip()
                                    if tb in tkt_cpns and cp.isdigit():
                                        tkt_cpns[tb].add(int(cp))

                            for tk, cn in tkt_cpns.items():
                                info = tkt_info[tk]
                                
                                # CASO 1: Reembolso Total (Para ver errores de Tasa L8/Penalidad)
                                if cn == {1, 2, 3, 4} or (info['RTDN'] == tk and len(cn) == 0):
                                    reembolsos_totales.append({
                                        'Ticket': tk, 'Agencia': info['Agencia'], 
                                        'Monto': info['Monto'], 'Fecha': info['Fecha']
                                    })
                                
                                # CASO 2: Infracción Cupón 2 (No reembolsable si Cupón 1 se usó)
                                elif 1 not in cn and 2 in cn:
                                    infracciones_cupon2.append({
                                        'Ticket': tk, 'Agencia': info['Agencia'], 
                                        'Cupones': sorted(list(cn)), 'Monto_Tarifa_Fuga': info['Monto'],
                                        'Motivo': 'ADM: Reembolso Cupón 2 con Cupón 1 Volado'
                                    })

# GUARDAR RESULTADOS
if reembolsos_totales:
    pd.DataFrame(reembolsos_totales).to_csv(os.path.join(PATH_BASE, '1_Reembolsos_Totales.csv'), index=False)
if infracciones_cupon2:
    pd.DataFrame(infracciones_cupon2).to_csv(os.path.join(PATH_BASE, '2_Infracciones_Regla_Tarifa.csv'), index=False)

print(f"--- PROCESO FINALIZADO ---")
print(f"Totales detectados: {len(reembolsos_totales)}")
print(f"Infracciones Cupón 2 detectadas: {len(infracciones_cupon2)}")
