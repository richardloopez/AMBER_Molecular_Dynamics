import os
import glob


patron_buscar = "S3_*"

# Lista para guardar los paths de los archivos .com
com_paths = []

# Recorre las carpetas que empiezan por DC3_ en el directorio actual
for folder in glob.glob(f"{patron_buscar}"):                    
    charges_dir = os.path.join(folder, "charges")
    # Si existe la carpeta charges
    if os.path.isdir(charges_dir):
        # Busca el archivo DC3_*.com dentro de la carpeta charges
        for com_file in glob.glob(os.path.join(charges_dir, f"{patron_buscar}.com")):
            com_paths.append(com_file)

# Junta los paths para el comando vimdiff
vimdiff_cmd = "vimdiff " + " ".join(com_paths)

# Muestra el resultado
print("COMANDO FINAL:")
print(vimdiff_cmd)

