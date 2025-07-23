#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

def run_command(command):
    """ Ejecuta un comando en bash y muestra la salida en tiempo real. """
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"ERROR ejecutando {command}:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout)

def main():
    print("Iniciando script de parametrizacion")

    # Definir rutas de los archivos
    ruta_script_dinamica = "/home/richard/Dinamica/scripts_dinamica/reparametrizacion_parmed_min_dinamica.py_____Xx_Recuerda_asegurarte_de_que_esta_correcto_xX_____"  # Modificar
    ruta_reparametleap = "/home/richard/Dinamica/scripts_dinamica/reparametleap.inpy_____Xx_Recuerda_asegurarte_de_que_esta_correctamente_adaptado_xX_____"  # Modificar

    # Cargar el modulo Amber 22 (fuente del entorno necesario)
    run_command("source /etc/profile && module load amber/22")

    # Identificar archivos .pdb en la carpeta actual
    archivos_pdb = [f for f in os.listdir('.') if f.endswith('.pdb')]
    if not archivos_pdb:
        print("No se encontraron archivos .pdb en el directorio actual.")
        sys.exit(1)

    print(f"Archivos PDB detectados: {archivos_pdb}")

    for pdb in archivos_pdb:
        nombre_base = os.path.splitext(pdb)[0]
        print(f"\nProcesando {pdb} en la carpeta {nombre_base}...")

        os.makedirs(nombre_base, exist_ok=True)

        # Mover archivo .pdb a la nueva carpeta
        destino_pdb = os.path.join(nombre_base, pdb)
        if not os.path.exists(destino_pdb):
            shutil.move(pdb, destino_pdb)

        os.chdir(nombre_base)

        # Copiar archivos necesarios
        for archivo in ["QCyMeBT3.frcmod", "QCyMeBT3.mol2"]:
            origen = os.path.join("..", archivo)
            if os.path.exists(origen):
                shutil.copy(origen, ".")
                print(f"Copiado {archivo} a {nombre_base}")
            else:
                print(f"No se encontro {archivo} en el directorio superior.")
                sys.exit(1)

        # Modificar reparametleap.in
        if os.path.exists(ruta_reparametleap):
            shutil.copy(ruta_reparametleap, "reparametleap.in")
            with open("reparametleap.in", 'r') as file:
                lines = file.readlines()
            with open("reparametleap.in", 'w') as file:
                for line in lines:
                    if "system= loadPDB" in line:
                        file.write(f"system= loadPDB {pdb}\n")
                    else:
                        file.write(line)
            print("Archivo reparametleap.in modificado correctamente")
        else:
            print(f"No se encontro {ruta_reparametleap}. Abortando.")
            sys.exit(1)

        # Ejecutar tleap
        run_command("tleap -f reparametleap.in")

        # Organizar archivos
        os.makedirs("bases", exist_ok=True)
        os.makedirs("otros_documentos", exist_ok=True)

        archivos_bases = ["system.inpcrd", "system.pdb", "system.prmtop"]
        for archivo in archivos_bases:
            if os.path.exists(archivo):
                shutil.move(archivo, "bases/")
        
        for archivo in os.listdir('.'):
            if archivo not in archivos_bases + ["bases", "otros_documentos", "reparametrizacion_parmed_min_dinamica.py"]:
                shutil.move(archivo, "otros_documentos/")

        print("Archivos organizados en carpetas.")

        # Copiar y ejecutar el script de dinamica
        if os.path.exists(ruta_script_dinamica):
            shutil.copy(ruta_script_dinamica, "reparametrizacion_parmed_min_dinamica.py")
            run_command("python3 reparametrizacion_parmed_min_dinamica.py")
        else:
            print(f"No se encontro {ruta_script_dinamica}. Abortando ejecucion de dinamica.")
            sys.exit(1)

        # Volver a la carpeta principal
        os.chdir("..")

    print("\nParametrizacion completada exitosamente.")

if __name__ == "__main__":
    main()
