import os
import zipfile
import pandas as pd

# RUTA MAESTRA
PATH = r'C:\Auditoria_Eurekis\Data_Ventas_2026'

print(f"--- INICIANDO ESCÁNER AGRESIVO EN: {PATH} ---")

hallazgos = []

if not os.path.exists(PATH):
    print("!!! ERROR: La carpeta C:\Auditoria_Eurekis\Data_Ventas_2026 no existe.")
else:
    # Listamos TODO lo que haya en la carpeta
    archivos = [f for f in os.listdir(PATH) if f.lower().endswith('.zip')]
    print(f"Archivos ZIP localizados: {len(archivos)}")

    for zip_name in archivos:
        full_path = os.path.join(PATH, zip_name)
        try:
            with zipfile.ZipFile(full_path, 'r') as z:
                for internal_file in z.namelist():
                    with z.open(internal_file) as f:
                        # Leemos línea a línea de forma segura
                        content = f.read().decode('latin-1', errors='ignore').splitlines()
                        
                        # Diccionarios temporales por archivo interno
                        tkts = {}
                        cpns = {}

                        for line in content:
                            # Buscamos el reembolso (BKS)
                            if line.startswith('BKS') and 'RFND' in line:
                                t = line[24:37].strip()[-10:]
                                tkts[t] = {
                                    'Agencia': line[37:44].strip(),
                                    'Fecha': line[11:17],
                                    'Zip': zip_name
                                }
                                cpns[t] = set()
                            
                            # Buscamos los cupones (BAR)
                            if line.startswith('BAR'):
                                tb = line[24:37].strip()[-10:]
                                c = line[37:38].strip()
                                if tb in cpns and c.isdigit():
                                    cpns[tb].add(int(c))

                        # Al terminar el archivo, guardamos si es infracción (Sin Cupón 1)
                        for t, c_set in cpns.items():
                            if len(c_set) > 0 and 1 not in c_set:
                                info = tkts[t]
                                hallazgos.append({
                                    'Ticket': t,
                                    'Agencia': info['Agencia'],
                                    'Cupones': sorted(list(c_set)),
                                    'Archivo': info['Zip']
                                })
        except Exception as e:
            print(f"No se pudo leer {zip_name}: {e}")

if hallazgos:
    df = pd.DataFrame(hallazgos)
    df.to_csv(r'C:\Auditoria_Eurekis\RESULTADO_FINAL_CUPON2.csv', index=False)
    print(f"--- ¡ÉXITO! Se encontraron {len(df)} infracciones de Cupón 2 ---")
    print("Revisa el archivo: C:\Auditoria_Eurekis\RESULTADO_FINAL_CUPON2.csv")
else:
    print("--- El escaneo terminó pero no se encontraron coincidencias ---")
