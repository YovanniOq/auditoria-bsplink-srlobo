import os
import zipfile
import pandas as pd
import re

PATH = r'C:\Auditoria_Eurekis\Data_Ventas_2026'

def extraer_ticket(texto):
    # Busca el primer número largo (10-13 dígitos) que suele ser el ticket
    match = re.search(r'\d{10,13}', texto)
    return match.group(0)[-10:] if match else None

print(f"--- ESCANEANDO ARCHIVOS CON BKS EN: {PATH} ---")

hallazgos = []

if not os.path.exists(PATH):
    print("!!! Carpeta no encontrada.")
else:
    zips = [f for f in os.listdir(PATH) if f.lower().endswith('.zip')]
    for z_name in zips:
        try:
            with zipfile.ZipFile(os.path.join(PATH, z_name), 'r') as z:
                for internal in z.namelist():
                    with z.open(internal) as f:
                        lineas = f.read().decode('latin-1', errors='ignore').splitlines()
                        
                        tkts = {}
                        cpns = {}

                        for l in lineas:
                            # Si la línea tiene BKS y es Reembolso
                            if 'BKS' in l and 'RFND' in l:
                                tkt = extraer_ticket(l)
                                if tkt:
                                    tkts[tkt] = {'Agencia': l[37:44].strip(), 'Zip': z_name}
                                    cpns[tkt] = set()
                            
                            # Si la línea tiene BAR (Cupones)
                            if 'BAR' in l:
                                tkt_b = extraer_ticket(l)
                                # Buscamos el número de cupón (suele ser un dígito solo)
                                # Intentamos buscar un dígito aislado después del ticket
                                match_cpn = re.search(r'\s(\d)\s', l) 
                                if tkt_b in cpns:
                                    # Si no lo halla por espacio, probamos posición fija de BAR
                                    cpn_val = l[37:38] if l[37:38].isdigit() else (match_cpn.group(1) if match_cpn else None)
                                    if cpn_val:
                                        cpns[tkt_b].add(int(cpn_val))

                        for t, c_set in cpns.items():
                            # REGLA: Si reembolsaron el 2 (o más) pero NO el 1
                            if len(c_set) > 0 and 1 not in c_set:
                                hallazgos.append({
                                    'Ticket': t,
                                    'Agencia': tkts[t]['Agencia'],
                                    'Cupones': sorted(list(c_set)),
                                    'Archivo': tkts[t]['Zip']
                                })
        except Exception as e:
            print(f"Error en {z_name}: {e}")

if hallazgos:
    df = pd.DataFrame(hallazgos)
    df.to_csv(r'C:\Auditoria_Eurekis\REPORTE_INFRACCIONES.csv', index=False)
    print(f"--- ¡LISTO! Se encontraron {len(df)} infracciones ---")
else:
    print("--- No se hallaron infracciones. ¿Seguro que hay reembolsos parciales en estos archivos? ---")
