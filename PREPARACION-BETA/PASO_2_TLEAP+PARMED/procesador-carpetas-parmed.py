#!/usr/bin/env python3
import os
import shutil
import subprocess

# Ruta del script que quieres copiar y ejecutar en cada carpeta
script1_name = "lanzador_dinamica_solo-parmed.py"
script1_name_no_ext = os.path.splitext(script1_name)[0]
current_dir = os.getcwd()

script2_name = "dinamica.py"
script2_name_no_ext = os.path.splitext(script2_name)[0]


# Listar carpetas en el directorio actual (excluye archivos)
folders = [f for f in os.listdir('.') if os.path.isdir(f)]

print(f"Total folders to process: {len(folders)}")
print("\nStarting sequential processing in each folder...\n")

for folder in folders:    
    # SCRIPT 1 (el general, importante)
    
    # Ruta destino del script (dentro de la carpeta)
    dest_script1_path = os.path.join(folder, script1_name)
    
    # Copiar el script si no existe ya
    if not os.path.exists(dest_script1_path):
        shutil.copy2(os.path.join(current_dir, script1_name), dest_script1_path)
        
    
    # SCRIPT 2 (subordinado, es lanzado por el script 1)
    
    dest_script2_path = os.path.join(folder, script2_name)
    if not os.path.exists(dest_script2_path):
        shutil.copy2(os.path.join(current_dir, script2_name), dest_script2_path)

    log_path = os.path.join(folder, f"{script1_name_no_ext}.log")
    try:
        with open(log_path, 'w') as log_file:
            subprocess.run(
                ["python3", script1_name],
                cwd=folder,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                check=True
            )
        print(f"Completed processing for folder: {folder}")
    except subprocess.CalledProcessError:
        print(f"Error processing folder: {folder}")

print("\nAll folders have been processed sequentially.\n")


