#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import time

# --- 1. Global Simulation Settings (de ultimate_dynamics.py) ---
# Define core parameters for the simulation
GLOBAL_SETTINGS = {
    'protein_residues': '1-1010',        # CHANGE THIS IF NEEDED
    'nucleic_residues': '1011-1036',        # CHANGE THIS IF NEEDED
    'base_prmtop': 'system.prmtop',     # Original prmtop from tleap
    'base_inpcrd': 'system.inpcrd',     # Original inpcrd from tleap
    'hmass_prmtop': 'system_hmass.prmtop', # Output prmtop from H-mass repartitioning
    'parmed_dir': 'parmed_setup',
    'base_dir': 'bases'                 # Directory containing original prmtop/inpcrd
}

# --- 2. Site-Specific SLURM Configuration (de dinamica_GPU_CTC.py) ---
CTC_SLURM_SETTINGS = {
    'partition': 'gpusNodes',
    'ngpus': 1,
    'ncpu': 2,
    'ntasks': 1,
    'mem': '40G'
}

# --- 3. Step Input File Definitions (de ultimate_dynamics.py) ---
# Define the Amber input file contents for each step.

STEP_01_MIN_RESTRAINT_25KCAL_IN = f"""
Step 1 -Minimization- solvent minimization (protein and nucleic restrained by 25 kcal/mol*Å²
&cntrl
  imin=1, ntx=1, maxcyc=50000, ntmin=2, ntpr=100,
  cut=9.0, ntr=1, restraint_wt=25.0,
  restraintmask= ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""

STEP_02_MIN_RESTRAINT_8KCAL_IN = f"""
Step 2 -Minimization- protein and nucleic restrained by 8 kcal/mol*Å²
&cntrl
  imin=1, ntx=1, maxcyc=10000, ntmin=2, ntpr=100,
  cut=9.0, ntr=1, restraint_wt=8.0,
  restraintmask= ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""
STEP_03_MIN_RESTRAINT_5KCAL_IN = f"""
Step 3 -Minimization- protein and nucleic restrained by 5 kcal/mol*Å²
&cntrl
  imin=1, ntx=1, maxcyc=10000, ntmin=2, ntpr=100,
  cut=9.0, ntr=1, restraint_wt=5.0,
  restraintmask= ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""
STEP_04_MIN_RESTRAINT_2KCAL_IN = f"""
Step 4 -Minimization- protein and nucleic restrained by 2 kcal/mol*Å²
&cntrl
  imin=1, ntx=1, maxcyc=20000, ntmin=2, ntpr=100,
  cut=9.0, ntr=1, restraint_wt=2.0,
  restraintmask= ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""

STEP_05_MIN_UNRESTRAINED_IN = """
Step 5 -Minimization- full system (unrestrained)
&cntrl
  imin=1, ntx=1, maxcyc=50000, ntmin=2, ntpr=100,
  cut=9.0, ntr=0,
/
"""

STEP_06_NVT_RESTRAINT_5KCAL_IN = f"""
Step 6 -NVT equilibration- Heating the system (protein and nucleic restrained by 5 kcal/mol*Å²)
&cntrl
  imin = 0, nstlim = 200000, dt = 0.001,
  irest = 0, ntx = 1, ig = -1,
  tempi = 0.0, temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 5000, ntpr = 1000,
  cut = 9.0, iwrap = 1,
  ntt = 3, gamma_ln=5, ntb = 1, ntp = 0,
  nscm = 0,
  ntr = 1,
  restraint_wt = 5.0,
  restraintmask = ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
  nmropt = 1,
/
&wt type='TEMP0', istep1=0, istep2=100000, value1=0.0, value2=310.0 /
&wt type='TEMP0', istep1=100001, istep2=200000, value1=310.0, value2=310.0 /
&wt type='END' /
"""

STEP_07_NPT_RESTRAINT_2KCAL_IN = f"""
Step 7 -NPT equilibration- protein and nucleic restrained by 2 kcal/mol*Å²
&cntrl
  imin = 0, nstlim = 1000000, dt = 0.001,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 1000, ntpr = 1000,
  cut = 9.0, iwrap = 1,
  ntt = 3, gamma_ln=5, ntb = 2, ntp = 1, barostat=2,
  ntr = 1,
  restraint_wt = 2.0,
  restraintmask = ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""
STEP_08_NPT_RESTRAINT_05KCAL_IN = f"""
Step 8 -NPT equilibration- protein and nucleic restrained by 0.5 kcal/mol*Å²
&cntrl
  imin = 0, nstlim = 1000000, dt = 0.001,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 1000, ntpr = 1000,
  cut = 9.0, iwrap = 1,
  ntt = 3, gamma_ln=5, ntb = 2, ntp = 1, barostat=2,
  ntr = 1,
  restraint_wt = 0.5,
  restraintmask = ":{GLOBAL_SETTINGS['protein_residues']} | :{GLOBAL_SETTINGS['nucleic_residues']}",
/
"""
STEP_09_NPT_UNRESTRAINED_IN = """
Step 9 -NPT equilibration- full system (unrestrained)
&cntrl
  imin = 0, nstlim = 1000000, dt = 0.001,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 1000, ntpr = 1000,
  cut = 9.0, iwrap = 1,
  ntt = 3, gamma_ln=5, ntb = 2, ntp = 1, barostat=2,
/
"""

STEP_10_PROD_IN = """
Step 10 -Production- MD run
&cntrl
  imin = 0, nstlim = 25000000, dt = 0.004,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntb = 2, ntc = 2, ntf=2, tol = 0.00001,
  ntwx = 1000, ntwv= -1, ntwr = 50000, ntpr = 10000,
  cut = 9.0,
  ntt = 3, gamma_ln=2, ntp = 1, barostat=2, iwrap=1
/
"""

# --- 4. Simulation Workflow (de ultimate_dynamics.py) ---
# This list defines the entire simulation pipeline.
SIMULATION_WORKFLOW = [
    {
        'name': 'STEP_01_MIN_RESTRAINT_25KCAL',
        'in_content': STEP_01_MIN_RESTRAINT_25KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_02_MIN_RESTRAINT_8KCAL',
        'in_content': STEP_02_MIN_RESTRAINT_8KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_03_MIN_RESTRAINT_5KCAL',
        'in_content': STEP_03_MIN_RESTRAINT_5KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_04_MIN_RESTRAINT_2KCAL',
        'in_content': STEP_04_MIN_RESTRAINT_2KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_05_MIN_UNRESTRAINED',
        'in_content': STEP_05_MIN_UNRESTRAINED_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_06_NVT_RESTRAINT_5KCAL',
        'in_content': STEP_06_NVT_RESTRAINT_5KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_07_NPT_RESTRAINT_2KCAL',
        'in_content': STEP_07_NPT_RESTRAINT_2KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_08_NPT_RESTRAINT_05KCAL',
        'in_content': STEP_08_NPT_RESTRAINT_05KCAL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_09_NPT_UNRESTRAINED',
        'in_content': STEP_09_NPT_UNRESTRAINED_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },   
    {
        'name': 'STEP_10_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_11_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_12_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_13_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_14_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_15_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_16_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_17_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_18_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'STEP_19_PROD',
        'in_content': STEP_10_PROD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    },
                    
    # Add more steps here, e.g.:
    # {
    #     'name': 'md2',
    #     'in_content': MD_IN,
    #     'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    # },
]


# --- 5. Helper Functions (Combined) ---

def run_parmed_setup():
    """
    Runs the initial H-mass repartitioning step using parmed.
    """
    print("--- Starting ParmEd H-Mass Repartitioning ---")
    parmed_dir = GLOBAL_SETTINGS['parmed_dir']
    base_dir = GLOBAL_SETTINGS['base_dir']
    prmtop_in = GLOBAL_SETTINGS['base_prmtop']
    inpcrd_in = GLOBAL_SETTINGS['base_inpcrd']
    prmtop_out = GLOBAL_SETTINGS['hmass_prmtop']

    os.makedirs(parmed_dir, exist_ok=True)
    os.chdir(parmed_dir)

    # Copy base files
    subprocess.run(['cp', f'../{base_dir}/{prmtop_in}', '.'], check=True)
    subprocess.run(['cp', f'../{base_dir}/{inpcrd_in}', '.'], check=True)

    # Create and run parmed script
    parmed_commands = f"""
module purge
parmed -p {prmtop_in} << EOF
hmassrepartition
outparm {prmtop_out}
quit
EOF
"""
    # Run in bash shell to correctly handle 'module purge' and EOF block
    subprocess.run(parmed_commands, shell=True, executable='/bin/bash', check=True)
    
    print("ParmEd setup complete.")
    os.chdir('..')

def generate_sh_launcher_ctc(sh_filename, step_name, pmemd_command, slurm_settings):
    """
    Generates the .sh script for SLURM in CTC.
    """
    content_sh = f"""#!/bin/bash
#SBATCH --job-name={step_name}
#SBATCH --output={step_name}.job.out
#SBATCH --error={step_name}.err
#SBATCH --partition={slurm_settings['partition']}
#SBATCH --gres=gpu:{slurm_settings['ngpus']}
#SBATCH -n {slurm_settings['ncpu']}
#SBATCH -N {slurm_settings['ntasks']}
#SBATCH --mem={slurm_settings['mem']}

# Environment variables (if needed)
# Example: export CUDA_VISIBLE_DEVICES=0

# pmemd command (formatted from the workflow)
{pmemd_command}
"""
    with open(sh_filename, 'w') as f:
        f.write(content_sh)

def job_finished(job_id):
    """
    Returns True if the SLURM job is no longer in the queue (finished).
    """
    cmd = ['squeue', '-j', str(job_id)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return job_id not in result.stdout

def check_timings_in_output(output_file):
    """
    Returns True if the word TIMINGS is in the output file.
    """
    try:
        with open(output_file, 'r') as f:
            for line in f:
                if 'TIMINGS' in line:
                    return True
    except FileNotFoundError:
        return False
    return False

# --- 6. Main Execution ---

def main():
    """
    Main function to orchestrate the simulation workflow.
    """
    
    # 1. Run initial parmed setup
    # run_parmed_setup()

    # 2. Initialize loop variables
    parmed_dir = GLOBAL_SETTINGS['parmed_dir']
    prmtop_file = GLOBAL_SETTINGS['hmass_prmtop']
    
    # The first step uses the inpcrd from the parmed dir
    previous_step_dir = parmed_dir
    coords_file = GLOBAL_SETTINGS['base_inpcrd'] 

    # 3. Iterate through the simulation workflow
    for step_config in SIMULATION_WORKFLOW:
        
        step_name = step_config['name']
        current_dir = step_name
        print(f"--- Starting Step: {step_name} ---")

        os.makedirs(current_dir, exist_ok=True)
        os.chdir(current_dir)

        # 2. Copy required files from previous step
        # The prmtop is always the same, copied from the parmed dir
        subprocess.run(['cp', f'../{parmed_dir}/{prmtop_file}', '.'], check=True)
        # The restart/coord file comes from the *immediate* previous step
        subprocess.run(['cp', f'../{previous_step_dir}/{coords_file}', '.'], check=True)

        # 3. Generate the .in file for this step
        with open(f"{step_name}.in", 'w') as f:
            f.write(step_config['in_content'])

        # 4. Format the pmemd command from the workflow template
        pmemd_command_template = step_config['sh_template']
        pmemd_command = pmemd_command_template.format(
            step_name=step_name,
            prmtop=prmtop_file,
            coords_in=coords_file  # This is the key! Uses the file from the prev step.
        )
        
        # 5. Generate the .sh file for CTC
        sh_file = f"{step_name}.sh"
        generate_sh_launcher_ctc(sh_file, step_name, pmemd_command, CTC_SLURM_SETTINGS)

        # 6. Submit the job and get Job ID
        result = subprocess.run(['sbatch', '--parsable', sh_file], stdout=subprocess.PIPE, text=True, check=True)
        job_id = result.stdout.strip()
        print(f"Job {step_name} submitted with JobID: {job_id}")

        # 7. Wait for the job to complete (using CTC logic)
        print(f"Waiting for job {job_id} to complete...")
        while not job_finished(job_id):
            time.sleep(10)  # Wait 10 seconds before checking again
        
        # Check that the output file exists and has TIMINGS
        output_file = f"{step_name}.out"
        print(f"Checking for 'TIMINGS' in {output_file}...")
        while not check_timings_in_output(output_file):
            print(f"'TIMINGS' not found yet, waiting 10 seconds...")
            time.sleep(10)
        
        print(f"Job {step_name} completed and contains TIMINGS.")

        # 8. Prepare variables for the next loop iteration
        os.chdir('..')
        previous_step_dir = current_dir
        coords_file = f"{step_name}.rst"  # The output of this step is the input for the next

    print("--- Simulation Workflow Completed ---")

if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred in a subprocess: {e}")
        print("Workflow terminated.")
    except FileNotFoundError as e:
        print(f"Error: A required file or program was not found: {e}")
        print("Workflow terminated.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Workflow terminated.")
