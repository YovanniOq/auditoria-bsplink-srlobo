import os
import zipfile
import pandas as pd
import re

# --- CONFIGURACIÓN DE RUTAS ---
# Basado en tu imagen, están en la raíz de C:
CARPETAS = [r'C:\Data_Ventas_2025', r'C:\Data_Ventas_2026']

def limpiar_tkt(txt):
    return re.sub(r'\D', '', str(txt)).lstrip('0')[-10:]

def parse_monto_iata(val):
    if not val or val.strip() == "": return 0.0
    mapping = {'{':0,'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
               '}':0,'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9}
    val = val.strip()
    last_char = val[-1] if val else ""
    if last_char in mapping:
        digit = mapping[last_char]
        sign = -1 if last_char in '}JKLMNOPQR' else 1
        return sign * (int(val[:-1]) * 10 + digit) / 100.0
    return float(val) / 100.0 if str(val).isdigit() else 0.0

def ejecutar_motor():
    print("🚀 Ejecutando Motor de Auditoría Integral...")
    totales = []
    infracciones = []

    for ruta in CARPETAS:
        if not os.path.exists(ruta):
            print(f"⚠️ Carpeta no encontrada: {ruta}")
            continue
        
        print(f"📂 Analizando: {ruta}")
        archivos_zip = [f for f in os.listdir(ruta) if f.lower().endswith('.zip')]
        
        for zip_name in archivos_zip:
            try:
                with zipfile.ZipFile(os.path.join(ruta, zip_name), 'r') as z:
                    for hot_file in z.namelist():
                        with z.open(hot_file) as f:
                            lines = f.read().decode('latin-1', errors='ignore').splitlines()
                            t_info, t_cpns = {}, {}
                            
                            for l in lines:
                                # Registro de Reembolso (BKS)
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = limpiar_tkt(l[24:37])
                                    t_info[t] = {
                                        'Ticket': t,
                                        'Agencia': l[37:44].strip(),
                                        'Monto': parse_monto_iata(l[50:61]),
                                        'Fecha': l[11:17],
                                        'Archivo': zip_name
                                    }
                                    t_cpns[t] = set()

                                # Registro de Cupones (BAR)
                                if l.startswith('BAR'):
                                    tb = limpiar_tkt(l[24:37])
                                    cp = l[37:38].strip()
                                    if tb in t_cpns and cp.isdigit():
                                        t_cpns[tb].add(int(cp))
                            
                            # Aplicar Reglas de Negocio
                            for tk, cn in t_cpns.items():
                                if tk in t_info:
                                    # REGLA SERGIO: Cupón 2 devuelto sin el 1 (Infracción)
                                    if 1 not in cn and 2 in cn:
                                        infracciones.append({**t_info[tk], 'Error': 'Cupón 2 devuelto sin Cupón 1'})
                                    else:
                                        totales.append(t_info[tk])
            except:
                continue

    # Guardar resultados en C:\ para que los encuentres rápido
    if totales or infracciones:
        if totales:
            pd.DataFrame(totales).drop_duplicates().to_csv(r'C:\REEMBOLSOS_GENERALES.csv', index=False)
        if infracciones:
            pd.DataFrame(infracciones).drop_duplicates().to_csv(r'C:\INFRACCIONES_CUPONES.csv', index=False)
        
        print(f"\n✅ PROCESO FINALIZADO")
        print(f"📊 Reembolsos Totales: {len(totales)}")
        print(f"⚠️ Infracciones Cupones: {len(infracciones)}")
        print("📁 Reportes generados en C:\\")
    else:
        print("❌ No se detectó información de reembolsos.")

if __name__ == "__main__":
    ejecutar_motor()
