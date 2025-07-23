#!/usr/bin/env python3

import os
import subprocess
import time

# Definiciones para el número de restrains y dinámicas
restraints = [0]  # Restraints para NPT, en el orden deseado
num_md = 1                 # Número de simulaciones MD

# Función para ejecutar el paso común entre min, heat, npt y md
def run_step(step_name, previous_step, input_files, in_content, sh_modification):
    """
    Realiza un paso de la simulación de manera modular.

    Args:
        step_name (str): Nombre del paso actual (ej. 'min', 'heat', 'npt', 'md').
        previous_step (str): Nombre del paso anterior (ej. 'parmed' para 'min', 'min' para 'heat').
        input_files (list of str): Archivos de entrada a copiar desde el paso anterior.
        in_content (str): Contenido del archivo .in para el paso.
        sh_modification (str): Modificación específica en el archivo .sh para el paso actual.
    """
    # Crear la carpeta del paso actual y moverse a ella
    os.makedirs(step_name, exist_ok=True)
    os.chdir(step_name)

    # Copiar archivos necesarios desde la carpeta anterior
    for file in input_files:
        subprocess.run(['cp', f'../{previous_step}/{file}', '.'])

    # Crear el archivo .in con el contenido proporcionado
    with open(f'{step_name}.in', 'w') as f:
        f.write(in_content)

    # Generar el archivo .sh mediante pmemd.cuda
    subprocess.run(['launch_pmemd.cuda', '0', step_name])

    # Modificar el archivo .sh para incluir referencias adicionales si es necesario
    with open(f'{step_name}.sh', 'r+') as f:
        content = f.read()
        content = content.replace(
            "$AMBERHOME/bin/pmemd.cuda -O -i", sh_modification
        )
        f.seek(0)
        f.write(content)
        f.truncate()

    # Lanzar el trabajo
    subprocess.run(['sbatch', f'{step_name}.sh'])

    # Esperar hasta que el archivo .rst del paso actual esté generado
    rst_file = f'{step_name}.rst'
    while not os.path.isfile(rst_file):
        print(f"Esperando a que termine el trabajo {step_name}.sh y se genere {rst_file}...")
        time.sleep(1)  # Esperar 1 segundo antes de verificar nuevamente
    print(f"Trabajo {step_name}.sh ha terminado y se generó {rst_file}.")

    # Convertir el archivo .mdcrd a .dcd y renombrarlo
    subprocess.run(['mdcrd_to_dcd'])
    subprocess.run(['mv', 'visual.dcd', f'{step_name}.dcd'])

    # Convertir el archivo .rst a .pdb y renombrarlo
    subprocess.run(['rst_to_pdb'])
    subprocess.run(['mv', 'visual.pdb', f'{step_name}.pdb'])

    # Volver a la carpeta principal
    os.chdir('..')


# Ejecución del proceso modular para cada paso
def main():
    # Parmed
    os.makedirs('parmed', exist_ok=True)
    os.chdir('parmed')
    subprocess.run(['cp', '../bases/system.prmtop', '.'])
    subprocess.run(['cp', '../bases/system.inpcrd', '.'])

    # Ejecutar el bloque de parmed con module purge y parmed
    parmed_commands = """
module purge
parmed -p system.prmtop << EOF
hmassrepartition
outparm system_hmass.prmtop
quit
EOF
"""
    # Ejecutar los comandos de parmed en un subproceso aislado
    subprocess.run(parmed_commands, shell=True, executable='/bin/bash')

    # Volver a la carpeta principal
    os.chdir('..')

    # Ejecutar pasos min y heat una sola vez
    steps = [
        {
            "name": "min",
            "previous": "parmed",
            "input_files": ["system_hmass.prmtop", "system.inpcrd"],
            "in_content": f"""\
minimization run

&cntrl
cut=1000,
imin=1,
maxcyc=0,
ncyc=0,
igb=6,
&end
/
""",
            "sh_modification": "$AMBERHOME/bin/pmemd.cuda -O -i min.in -o min.out -p system_hmass.prmtop -c system.inpcrd -r min.rst -x min.mdcrd -ref system.inpcrd"
        },
        
    ]

    # Ejecutar min
    for step in steps:
        run_step(
            step_name=step["name"],
            previous_step=step["previous"],
            input_files=step["input_files"],
            in_content=step["in_content"],
            sh_modification=step["sh_modification"]
        )


if __name__ == '__main__':
    main()



