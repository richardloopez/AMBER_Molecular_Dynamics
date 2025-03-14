#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

#KEEP AN EYE ON THE INTERVAL AND KEEP FILES DEFINITIONS
import os
import shutil
import subprocess
import csv

# Name of the mmpbgsa script (make sure it matches) and the input.csv
MMPBSA_SCRIPT = "Each_Folder_General_Automated_MMPBSA_calculations.py"
CSV_FILE = "input_auto_multi_mmpbgsa.csv"

def crear_carpetas_y_copiar(csv_file, mmpbsa_script):
    """
    Read the CSV file, create the necessary folders, copy the files and modify the MMPBSA script.
    """
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line (header)

        for row in reader:
            to_folder, from_folder, start_frame, end_frame = row

            # 1. Generate the name of the new folder
            new_folder_name = f"TO_{to_folder}_FROM_{from_folder}_{start_frame}_{end_frame}"
            
            # 2. Create the folder
            if not os.path.exists(new_folder_name):
                os.makedirs(new_folder_name)
                print(f"Carpeta creada: {new_folder_name}")
            else:
                print(f"La carpeta {new_folder_name} ya existe. Continuando...")
                continue # Skip to the next record if the folder already exists

            # 3. Copy the contents of the "FROM" folder to the new folder.
            from_folder_path = from_folder  # We assume that the "FROM" folder is in the same directory.
            if os.path.exists(from_folder_path):
                for item in os.listdir(from_folder_path):
                    s = os.path.join(from_folder_path, item)
                    d = os.path.join(new_folder_name, item)
                    try:
                        if os.path.isdir(s):
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)
                    except Exception as e:
                        print(f"Error al copiar {s} a {d}: {e}")
                print(f"Contenido de {from_folder} copiado a {new_folder_name}")
            else:
                print(f"La carpeta {from_folder} no existe. Revise el archivo CSV.")
                continue # Skip to the next record if the FROM folder does not exist

            # 4. Copy the MMPBSA script to the new folder
            shutil.copy2(mmpbsa_script, new_folder_name)
            print(f"Script MMPBSA copiado a {new_folder_name}")

            # 5. Modify the MMPBSA script in the new folder
            mmpbsa_script_path = os.path.join(new_folder_name, mmpbsa_script)
            
            # Read the script content
            with open(mmpbsa_script_path, 'r') as f:
                lines = f.readlines()
            
            # Modify the line "startframe=..., endframe=..."
            with open(mmpbsa_script_path, 'w') as f:
                for line in lines:
                    if "startframe=" in line and "endframe=" in line:
                        f.write(f"   startframe={start_frame}, endframe={end_frame}, interval=10, keep_files=2\n") #########################################################CHANGE IF NECESSARY
                    else:
                        f.write(line)
            print(f"Script MMPBSA modificado en {new_folder_name}")

            # 6. Launch MMPBSA
            try:
                subprocess.run(["sbatch", mmpbsa_script], cwd=new_folder_name, check=True)
                print(f"Script MMPBSA lanzado en {new_folder_name}")
            except subprocess.CalledProcessError as e:
                print(f"Error al lanzar el script MMPBSA en {new_folder_name}: {e}")

if __name__ == "__main__":
    # Script starting point
    crear_carpetas_y_copiar(CSV_FILE, MMPBSA_SCRIPT)
    print("Proceso completado.")

