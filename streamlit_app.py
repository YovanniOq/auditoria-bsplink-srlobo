import os
import zipfile
import pandas as pd
import re

# --- CONFIGURACIÓN DE RUTAS (CORREGIDO SEGÚN TU IMAGEN) ---
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

def ejecutar_auditoria():
    print("🚀 Iniciando Auditoría Integral - Sr Lobo / Eurekis")
    reembolsos_totales = []
    infracciones_cupones = []

    for ruta_full in CARPETAS:
        if not os.path.exists(ruta_full):
            print(f"⚠️ Carpeta no encontrada: {ruta_full}")
            continue
        
        print(f"📂 Procesando: {ruta_full}")
        archivos = [f for f in os.listdir(ruta_full) if f.lower().endswith('.zip')]
        
        for file in archivos:
            try:
                with zipfile.ZipFile(os.path.join(ruta_full, file), 'r') as z:
                    for name in z.namelist():
                        with z.open(name) as f:
                            content = f.read().decode('latin-1', errors='ignore').splitlines()
                            t_info = {}
                            t_cpns = {}
                            
                            for l in content:
                                # Registro BKS: Datos de Reembolso
                                if l.startswith('BKS') and 'RFND' in l:
                                    t = limpiar_tkt(l[24:37])
                                    t_info[t] = {
                                        'Ticket': t,
                                        'Agencia': l[37:44].strip(),
                                        'Monto': parse_monto_iata(l[50:61]),
                                        'Fecha': l[11:17],
                                        'Archivo': file
                                    }
                                    t_cpns[t] = set()

                                # Registro BAR: Cupones
                                if l.startswith('BAR'):
                                    tb = limpiar_tkt(l[24:37])
                                    cp = l[37:38].strip()
                                    if tb in t_cpns and cp.isdigit():
                                        t_cpns[tb].add(int(cp))

                            for tk, cn in t_cpns.items():
                                if tk not in t_info: continue
                                reg = t_info[tk]
                                # Regla Sergio: Tramo 2 reembolsado con Tramo 1 volado (no aparece en el reembolso)
                                if 1 not in cn and 2 in cn:
                                    infracciones_cupones.append({**reg, 'Error': 'T2 reembolsado con T1 usado'})
                                else:
                                    reembolsos_totales.append(reg)
            except Exception as e:
                print(f"❌ Error en {file}: {e}")

    # Guardar Resultados en C:\ para fácil acceso
    if reembolsos_totales or infracciones_cupones:
        if reembolsos_totales:
            pd.DataFrame(reembolsos_totales).drop_duplicates().to_csv(r'C:\REEMBOLSOS_GENERALES.csv', index=False)
        if infracciones_cupones:
            pd.DataFrame(infracciones_cupones).drop_duplicates().to_csv(r'C:\INFRACCIONES_CUPONES.csv', index=False)
        
        print(f"\n✅ PROCESO COMPLETADO")
        print(f"📊 Reembolsos: {len(reembolsos_totales)}")
        print(f"⚠️ Infracciones: {len(infracciones_cupones)}")
        print("📁 Revisa tus archivos en la raíz de C:\\")
    else:
        print("❌ No se encontraron datos en las carpetas indicadas.")

if __name__ == "__main__":
    ejecutar_auditoria()
