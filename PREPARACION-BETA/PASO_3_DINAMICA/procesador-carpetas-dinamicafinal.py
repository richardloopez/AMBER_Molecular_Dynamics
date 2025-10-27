#!/usr/bin/env python3
import os
import shutil
import subprocess

# Lista de scripts a copiar
scripts_to_use = ["dinamica_GPU_CTC+md1x4_CTC.sh", "dinamica_GPU_CTC.py", "md1x4_CTC.sh"]  # Evitar duplicados, corregir extensión según corresponda

script1_name = "dinamica_GPU_CTC+md1x4_CTC.sh"
script1_name_no_ext = os.path.splitext(script1_name)[0]
current_dir = os.getcwd()

# Listar carpetas en el directorio actual (excluye archivos)
folders = [f for f in os.listdir('.') if os.path.isdir(f)]

print(f"Total folders to process: {len(folders)}")
print("\nStarting sequential processing in each folder...\n")

for folder in folders:
    # Copia los scripts a la carpeta destino si no existen
    for script in scripts_to_use:
        source = os.path.join(current_dir, script)
        destination = os.path.join(folder, script)
        try:
            if not os.path.exists(destination):
                shutil.copy2(source, destination)
            os.chmod(destination, 0o777)  # Asigna permisos de ejecutar a todos
        except Exception as e:
            print(f"Error copying or chmod {script} to {folder}: {e}")


    # Ejecuta el script con sbatch dentro de la carpeta
    log_path = os.path.join(folder, f"{script1_name_no_ext}.log")
    try:
        with open(log_path, 'w') as log_file:
            subprocess.run(
                ["sbatch", script1_name],
                cwd=folder,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                check=True
            )
        print(f"Completed processing for folder: {folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing folder: {folder}, Exit code: {e.returncode}")
    except Exception as e:
        print(f"General error in folder {folder}: {e}")

print("\nAll folders have been processed sequentially.\n")
