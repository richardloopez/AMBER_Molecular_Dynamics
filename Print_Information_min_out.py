#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import os
import csv

def search_string(folder, base_dir):
    """
    Busca el último valor de ENERGY en archivos .out y extrae la información deseada.
    """
    print(f"Searching in: {folder}")
    os.chdir(folder)
    
    # Obtener todos los archivos .out en el directorio actual
    out_files = [f for f in os.listdir() if f.endswith(".out")]
    
    results = []
    if not out_files:
        print(f"    {folder} no contiene archivos .out")
    else:
        for out_file in out_files:
            found_value = None
            try:
                with open(out_file, "r") as out_file_handle:
                    lines = out_file_handle.readlines()
                    lines = list(reversed(lines)) # Invertir para buscar desde el final
                    
                    # Buscar la línea de encabezado de la tabla desde el final
                    for i, line in enumerate(lines):
                        line_lower = line.lower().strip()
                        
                        # Comprobar si la línea es la línea de encabezado de la tabla
                        if "nstep" in line_lower and "energy" in line_lower and "rms" in line_lower:
                            print(f"Línea de encabezado encontrada: {line.strip()}")
                            
                            # Comprobar si hay una línea siguiente
                            if i > 0: # Ahora i > 0 porque estamos iterando en la lista invertida
                                next_line = lines[i - 1].strip() # i - 1 porque estamos en la lista invertida
                                
                                # Separar la línea en valores
                                values = next_line.split()
                                
                                # Mantener solo las posiciones 0 y 2
                                if len(values) > 2:
                                    found_value = f"{values[1]}"
                                else:
                                    found_value = "Dato incompleto"
                                
                                print(f"Línea filtrada: {found_value}")

                            else:
                                print("No hay línea siguiente.")
                                found_value = "No hay línea siguiente"
                            break  # Salir del bucle si se encuentra
            except UnicodeDecodeError:
                print(f"Error al decodificar el archivo {out_file}. Saltando.")
                continue
            
            # Calcular la ruta relativa
            relative_path = os.path.relpath(os.path.join(folder, out_file), base_dir)
            results.append((relative_path, found_value))

    # No cambiar el directorio aquí, se hace en la función explore_directory
    return results

def explore_directory(base_folder, current_depth, max_depth, base_dir):
    """
    Recursivamente explora directorios hasta una profundidad especificada.
    """
    if current_depth > max_depth:
        return
    
    for folder in sorted(os.listdir(base_folder)):
        folder_path = os.path.join(base_folder, folder)
        
        if os.path.isdir(folder_path):
            print(f"Exploring: {folder_path}")
            results = search_string(folder_path, base_dir)
            
            # Escribir resultados directamente al archivo
            with open(os.path.join(base_dir, "Search_Results.csv"), "a", newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                for out_file, found_value in results:
                    csv_writer.writerow([out_file, found_value])
            
            explore_directory(folder_path, current_depth + 1, max_depth, base_dir)

# Settings
base_dir = os.getcwd()
depth_degree = 1 # Profundidad de búsqueda fija en 1

# Delete the file if it exists
file_path = os.path.join(base_dir, "Search_Results.csv")
try:
    os.remove(file_path)
except FileNotFoundError:
    pass

# Encabezado del archivo
with open(os.path.join(base_dir, "Search_Results.csv"), "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Archivo", "Valor ENERGY"])

# Start the exploration from the current working directory
print("Exploring directories...")
explore_directory(base_dir, 0, depth_degree, base_dir)

print("Results have been written to Search_Results.csv in the base directory.")
