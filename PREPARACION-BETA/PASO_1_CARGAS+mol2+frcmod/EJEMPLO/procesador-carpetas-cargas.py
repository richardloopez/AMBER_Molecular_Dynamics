#!/usr/bin/env python3
import os
import subprocess
import concurrent.futures

# Listar carpetas en el directorio actual
folders = [f for f in os.listdir('.') if os.path.isdir(f)]

print(f"Total folders to process: {len(folders)}")
print("\nStarting parallel processing in each folder...\n")

def process_folder(folder):
    log_path = os.path.join(folder, "charges-antechamber-tleap.log")
    try:
        with open(log_path, 'w') as log_file:
            subprocess.run(
                ["python3", "charges-antechamber-tleap.py"],
                cwd=folder,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                check=True
            )
        return f"Completed processing for folder: {folder}"
    except subprocess.CalledProcessError:
        return f"Error processing folder: {folder}"

# Número de procesos en paralelo (ajusta según tu CPU)
max_workers = min(8, len(folders))

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = executor.map(process_folder, folders)

for result in results:
    print(result)

print("\nAll folders have been processed in parallel.\n")

