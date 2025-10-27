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

    # Modificar el archivo .sh para incluir referencias adicionales y excluir nodo11
    with open(f'{step_name}.sh', 'r+') as f:
        lines = f.readlines()
        # Buscar la última línea que empieza por #SBATCH
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("#SBATCH"):
                insert_idx = i + 1
        # Insertar la línea de exclusión justo después de las directivas #SBATCH
        lines.insert(insert_idx, "#SBATCH --exclude=nodo11        # Problematic node\n")
        # Unir el contenido y realizar el reemplazo habitual
        content = ''.join(lines)
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
imin=1,
ntx=1,
maxcyc=20000,
ncyc=2000,
ntpr=25,
ntwx=100,
cut=9.0,
/
""",
            "sh_modification": "$AMBERHOME/bin/pmemd.cuda -O -i min.in -o min.out -p system_hmass.prmtop -c system.inpcrd -r min.rst -x min.mdcrd"
        },
        {
            "name": "heat",
            "previous": "min",
            "input_files": ["system_hmass.prmtop", "min.rst"],
            "in_content": f"""\
&cntrl
imin = 0, nstlim = 2000000, dt = 0.001,
irest = 0, ntx = 1, ig = -1,
tempi = 100.0, temp0 = 298.0,
ntc = 2, ntf = 2, tol = 0.00001,
ntwx = 10000, ntwr = 5000, ntpr = 1000,
cut = 9.0, iwrap = 0,
ntt = 3, gamma_ln=1., ntb = 1, ntp = 0,
nscm = 0,
/
""",
            "sh_modification": "$AMBERHOME/bin/pmemd.cuda -O -i heat.in -o heat.out -p system_hmass.prmtop -c min.rst -r heat.rst -x heat.mdcrd"
        }
    ]

    # Ejecutar min y heat
    for step in steps:
        run_step(
            step_name=step["name"],
            previous_step=step["previous"],
            input_files=step["input_files"],
            in_content=step["in_content"],
            sh_modification=step["sh_modification"]
        )

    # Definir configuraciones para cada paso de NPT con restraints específicos
    for i, restraint in enumerate(restraints):
        step_name = f"npt{restraint}"
        previous_step = 'heat' if i == 0 else f"npt{restraints[i-1]}"
        input_files = ["system_hmass.prmtop", f"{previous_step}.rst"]
        in_content = f"""\
&cntrl
imin = 0, nstlim = 2000000, dt = 0.001,
irest = 1, ntx = 5, ig = -1,
temp0 = 298.0,
ntc = 2, ntf = 2, tol = 0.00001,
ntwx = 10000, ntwr = 1000, ntpr = 1000,
cut = 9.0, iwrap = 0,
ntt = 3, gamma_ln=1, ntb = 2, ntp = 1, barostat=2,
/
"""
        sh_modification = f"$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p system_hmass.prmtop -c {previous_step}.rst -r {step_name}.rst -x {step_name}.mdcrd"
        
        # Ejecutar cada paso npt
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content,
            sh_modification=sh_modification
        )

    # Definir configuraciones para cada simulación MD adicional
    for i in range(1, num_md + 1):
        step_name = f"md{i}"
        previous_step = 'npt0' if i == 1 else f"md{i-1}"
        input_files = ["system_hmass.prmtop", f"{previous_step}.rst"]
        in_content = """\
&cntrl
imin = 0, nstlim = 75000000, dt = 0.004,
irest = 1, ntx = 5, ig = -1,
temp0 = 298.0,
ntb = 2, ntc = 2, ntf=2, tol = 0.00001,
ntwx = 50000, ntwv= -1, ntwr = 50000, ntpr = 10000,
cut = 9.0, iwrap = 0,
ntt = 3, gamma_ln=5., ntp = 1, barostat=2,
/
"""

        sh_modification = f"$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p system_hmass.prmtop -c {previous_step}.rst -r {step_name}.rst -x {step_name}.mdcrd"
        
        # Ejecutar cada paso md
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content,
            sh_modification=sh_modification
        )

if __name__ == '__main__':
    main()

