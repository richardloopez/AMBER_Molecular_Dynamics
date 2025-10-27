#!/usr/bin/env python3
import os
import sys
import subprocess
import time
# PARTE 1 DE LAS VARIABLES DEL LANZADOR
ngpus = 1 # NO TOCAR POR FAVOR
ncpu = 2 # NO TOCAR POR FAVOR
# Definiciones para el número de restraints y dinámicas
restraints = [0]  # Restraints para NPT
num_md = 1        # Número de simulaciones MD
def crear_sh_cpu(step_name, out_name, err_name, partition, mem, ntasks, input_file, output_file, prmtop, cprev, rst_new, mdcrd, inf_file):
    contenido_sh = f"""#!/bin/bash
#SBATCH --job-name={step_name}
#SBATCH --output={out_name}
#SBATCH --error={err_name}
#SBATCH --partition={partition}
#SBATCH --gres=gpu:{ngpus}
#SBATCH -n {ncpu}
#SBATCH -N {ntasks}
#SBATCH --mem={mem}
# Variables de entorno para ajuste de paralelismo híbrido y afinidad
# (En GPU no tengo nada por ahora, pero se podría hacer "export CUDA_VISIBLE_DEVICES=0" si fuera necesario)
pmemd.cuda -O \
 -i {input_file} \
 -o {output_file} \
 -p {prmtop} \
 -c {cprev} \
 -r {rst_new} \
 -x {mdcrd} \
 -inf {inf_file}
"""
    with open(f'{step_name}.sh', 'w') as f:
        f.write(contenido_sh)
def job_finished(job_id):
    """Devuelve True si el job SLURM ya no está en la cola (terminado)."""
    cmd = ['squeue', '-j', str(job_id)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return job_id not in result.stdout
def check_timings_in_output(output_file):
    """Devuelve True si la palabra TIMINGS está en el archivo de salida."""
    try:
        with open(output_file, 'r') as f:
            for line in f:
                if 'TIMINGS' in line:
                    return True
    except FileNotFoundError:
        return False
    return False
# PARTE 2 DE LAS VARIABLES DEL LANZADOR
def run_step(step_name, previous_step, input_files, in_content):
    os.makedirs(step_name, exist_ok=True)
    os.chdir(step_name)
    for file in input_files:
        subprocess.run(['cp', f'../{previous_step}/{file}', '.'])
    with open(f'{step_name}.in', 'w') as f:
        f.write(in_content)
    prmtop = "system_hmass.prmtop"
    rst_in = input_files[-1]
    rst_out = f"{step_name}.rst"
    mdcrd = f"{step_name}.mdcrd"
    info = f"{step_name}.info"
    out_name = f"{step_name}.job.out"
    err_name = f"{step_name}.err"
    partition = "gpusNodes"
    ntasks = "1"
    mem = "40G"
    crear_sh_cpu(step_name, out_name, err_name, partition, mem, ntasks,
                 f"{step_name}.in", f"{step_name}.out", prmtop,
                 rst_in, rst_out, mdcrd, info)
    # Lanzar el trabajo y capturar el job ID
    result = subprocess.run(['sbatch', '--parsable', f'{step_name}.sh'], stdout=subprocess.PIPE, text=True)
    job_id = result.stdout.strip()
    print(f"Trabajo {step_name} enviado con JobID: {job_id}")
    # Esperar hasta que el job termine
    print(f"Esperando finalización del Job {job_id}...")
    while not job_finished(job_id):
        time.sleep(10)  # Espera 10 segundos antes de chequear de nuevo
        
    # Comprobar que apareció la palabra TIMINGS en la salida
    output_file = f"{step_name}.out"
    print(f"Chequeando salida para 'TIMINGS' en {output_file}...")
    while not check_timings_in_output(output_file):
        print(f"'TIMINGS' no encontrado aún, esperando 10 segundos...")
        time.sleep(10)
    print(f"Trabajo {step_name} finalizado y contiene TIMINGS.")
    os.chdir('..')
def main():
    os.makedirs('parmed', exist_ok=True)
    os.chdir('parmed')
    subprocess.run(['cp', '../bases/system.prmtop', '.'])
    subprocess.run(['cp', '../bases/system.inpcrd', '.'])
    parmed_commands = """\
module purge
hmassrepartition
outparm system_hmass.prmtop
quit
"""
    with open ("parmed.in", "w") as f:
        f.write(parmed_commands)
    subprocess.run(['parmed', '-p', 'system.prmtop', '-i', 'parmed.in'])
    if not os.path.isfile("system_hmass.prmtop"):
        print("Error, no se generó system_hmass.prmtop. ¿Has cargado el módulo de Amber antes de lanzar? El script se detiene.")
        sys.exit(1)
    os.chdir('..')
    steps = [
        {
            "name": "min",
            "previous": "parmed",
            "input_files": ["system_hmass.prmtop", "system.inpcrd"],
            "in_content": """\
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
"""
        },
        {
            "name": "heat",
            "previous": "min",
            "input_files": ["system_hmass.prmtop", "min.rst"],
            "in_content": """\
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
"""
        }
    ]
    for step in steps:
        run_step(
            step_name=step["name"],
            previous_step=step["previous"],
            input_files=step["input_files"],
            in_content=step["in_content"]
        )
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
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content
        )
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
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content
        )
if __name__ == '__main__':
    main()
