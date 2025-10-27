#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil

#subprocess.run(["module", "load", "amber/22"])



script_dinamica_unitaria = "dinamica.py"


    

############################## GENERAR BASES #################################################


carpetas_disponibles = os.listdir()

if "archivos_dinamica" in carpetas_disponibles:
    print("carpeta archivos_dinamica encontrada")
    shutil.copytree("archivos_dinamica", "bases")
    
else:
    raise FileNotFoundError("No se encontró la carpeta 'archivos_dinamica'")

os.chdir("bases")

pbs_que_no_me_interesan = [] # Voy a dejar sólo los .pbs que tienen + en el nombre (R+L)

for archivo in os.listdir(): 
    if archivo.endswith(".pbs"):
        if "+" not in archivo:
            pbs_que_no_me_interesan.append(archivo)
            
             
print(f"Archivos .pbs que no me interesan y voy a eliminar: {pbs_que_no_me_interesan}")

for archivo in pbs_que_no_me_interesan:
    os.remove(archivo)

primigenio_estaba = False

if "primigenio_leap.in" in os.listdir():
    primigenio_estaba = True
    os.remove("primigenio_leap.in")
    
else:
    print("No se encontró el archivo 'primigenio_leap.in' para eliminar.")

print("Archivos eliminados en bases:")

if primigenio_estaba:
    print("primigenio_leap.in")

for archivo in os.listdir():
    print(archivo)


#########################################################################################################

############################## HACER TLEAP #################################################


subprocess.run(["tleap", "-f", "tleap.in"])


if "system.pdb" in os.listdir():
    print("tleap se ejecutó y se generó 'system.pdb'")
    
else:
    raise FileNotFoundError("No se encontró el archivo 'system.pdb'")

#########################################################################################################
############################## LANZAR DINAMIA #################################################

os.chdir("..")

try:
    subprocess.run([f"./{script_dinamica_unitaria}"], timeout=5)
except subprocess.TimeoutExpired:
    print("El proceso se detuvo después de 5 segundos.")

parmed_dir = "parmed"
parmed_file = os.path.join(parmed_dir, "system_hmass.prmtop")

if os.path.isdir(parmed_dir) and os.path.exists(parmed_file):
    print("Se ha creado correctamente la carpeta 'parmed' y el archivo 'system_hmass.prmtop'.")
else:
    print("No se encontró la carpeta 'parmed' o el archivo 'system_hmass.prmtop'.")

for carpeta in ["min", "heat"]:
    if os.path.exists(carpeta):
        shutil.rmtree(carpeta)
        print(f"Se ha eliminado la carpeta {carpeta}.")






