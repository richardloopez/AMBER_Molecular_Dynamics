#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import time

# --- 1. Global Simulation Settings ---
# Define core parameters for the simulation
GLOBAL_SETTINGS = {
    'protein_residues': '1-740', CAMBIA ESTO SI NECESARIO, PENDEJO     # Residue mask for restraints (e.g., "1-376")
    'base_prmtop': 'system.prmtop',  # Original prmtop from tleap
    'base_inpcrd': 'system.inpcrd',  # Original inpcrd from tleap
    'hmass_prmtop': 'system_hmass.prmtop', # Output prmtop from H-mass repartitioning
    'parmed_dir': 'parmed_setup',
    'base_dir': 'bases'              # Directory containing original prmtop/inpcrd
}

# --- 2. Site-Specific SLURM Configuration ---
# Add any extra SBATCH directives or node exclusions here.
# This will be applied to every job submitted.
SLURM_EXTRAS = {

        # e.g., "#SBATCH --partition=gpu",
        # "#SBATCH --account=my_project"
    ]
}

# --- 3. Step Input File Definitions ---
# Define the Amber input file contents for each step.

MIN_1_SOLVENT_IN = f"""
Minimization step 1: solvent with protein restrained
&cntrl
  imin=1, maxcyc=20000, ncyc=2000, ntpr=25,
  cut=9.0, ntr=1, restraint_wt=25.0,
  restraintmask=":{GLOBAL_SETTINGS['protein_residues']}",
/
"""

MIN_2_LESS_RESTRAINT_IN = f"""
Minimization step 2: solvent with protein less restrained
&cntrl
  imin=1, maxcyc=20000, ncyc=2000, ntpr=25,
  cut=9.0, ntr=1, restraint_wt=8.0,
  restraintmask=":{GLOBAL_SETTINGS['protein_residues']}",
/
"""

MIN_3_FULL_IN = """
Minimization step 3: full system
&cntrl
  imin=1, maxcyc=20000, ncyc=2000,
  ntpr=25, cut=9.0, ntr=0,
/
"""

HEAT_IN = """
Heating the system
&cntrl
  imin = 0, nstlim = 2000000, dt = 0.001,
  irest = 0, ntx = 1, ig = -1,
  tempi = 0.0, temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 5000, ntpr = 1000,
  cut = 9.0, iwrap = 0,
  ntt = 3, gamma_ln=1., ntb = 1, ntp = 0,
  nscm = 0,
/
"""

NPT_IN = """
NPT equilibration
&cntrl
  imin = 0, nstlim = 2000000, dt = 0.001,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntc = 2, ntf = 2, tol = 0.00001,
  ntwx = 10000, ntwr = 1000, ntpr = 1000,
  cut = 9.0, iwrap = 0,
  ntt = 3, gamma_ln=1, ntb = 2, ntp = 1, barostat=2,
/
"""

MD_IN = """
Production MD run
&cntrl
  imin = 0, nstlim = 75000000, dt = 0.004,
  irest = 1, ntx = 5, ig = -1,
  temp0 = 310.0,
  ntb = 2, ntc = 2, ntf=2, tol = 0.00001,
  ntwx = 50000, ntwv= -1, ntwr = 50000, ntpr = 10000,
  cut = 9.0, iwrap = 0,
  ntt = 3, gamma_ln=5., ntp = 1, barostat=2,
/
"""

# --- 4. Simulation Workflow ---
# This list defines the entire simulation pipeline.
# Each dictionary is one step. Add/remove/modify dictionaries to change the workflow.
#
# 'name': Directory name for the step.
# 'in_content': The input file content (from section 3).
# 'sh_template': The pmemd command to be inserted into the .sh file.
#   - {step_name}: Will be replaced with the step's 'name'.
#   - {prmtop}: Will be replaced with the H-mass prmtop file.
#   - {coords_in}: Will be replaced with the restart/coord file from the *previous* step.

SIMULATION_WORKFLOW = [
    {
        'name': 'min_1_solvent',
        'in_content': MIN_1_SOLVENT_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'min_2_less_restraint',
        'in_content': MIN_2_LESS_RESTRAINT_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd -ref {coords_in}"
    },
    {
        'name': 'min_3_full',
        'in_content': MIN_3_FULL_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    },
    {
        'name': 'heat',
        'in_content': HEAT_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    },
    {
        'name': 'npt0',
        'in_content': NPT_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    },
    {
        'name': 'md1',
        'in_content': MD_IN,
        'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    },
    # Add more steps here, e.g.:
    # {
    #     'name': 'md2',
    #     'in_content': MD_IN,
    #     'sh_template': "$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p {prmtop} -c {coords_in} -r {step_name}.rst -x {step_name}.mdcrd"
    # },
]


# --- 5. Helper Functions ---

def wait_for_file(file_path, poll_interval=10):
    """
    Waits for a specific file to appear.
    """
    print(f"Waiting for job to finish and create {file_path}...")
    while not os.path.isfile(file_path):
        time.sleep(poll_interval)
    print(f"File {file_path} found. Proceeding.")

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


# --- 6. Main Execution ---

def main():
    """
    Main function to orchestrate the simulation workflow.
    """
    
    # 1. Run initial parmed setup
    #run_parmed_setup()

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

        # 4. Launch the job (this creates the .sh file)
        subprocess.run(['launch_pmemd.cuda', '0', step_name], check=True)

        # 5. Modify the generated .sh file
        sh_file = f"{step_name}.sh"
        
        # 5a. Format the new pmemd command from the template
        # This command will use the *copied* coordinate file name
        new_pmemd_command = step_config['sh_template'].format(
            step_name=step_name,
            prmtop=prmtop_file,
            coords_in=coords_file  # This is the key! Uses the file from the prev step.
        )

        # 5b. Read, modify, and write the .sh file
        with open(sh_file, 'r') as f:
            lines = f.readlines()

        # 5c. Inject SLURM extras
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("#SBATCH"):
                insert_idx = i + 1
        
        # Add node exclusions
        for node in SLURM_EXTRAS.get('exclude_nodes', []):
            lines.insert(insert_idx, f"#SBATCH --exclude={node}        # Excluded via script\n")
        # Add other extra lines
        for line in SLURM_EXTRAS.get('extra_sbatch_lines', []):
            lines.insert(insert_idx, f"{line}\n")
        
        # 5d. Replace the default pmemd command
        content = ''.join(lines)
        # The launch_pmemd.cuda script often uses a generic command as a placeholder
        content = content.replace(
            "$AMBERHOME/bin/pmemd.cuda -O -i", new_pmemd_command, 1
        )

        with open(sh_file, 'w') as f:
            f.write(content)

        # 6. Submit the modified job
        subprocess.run(['sbatch', sh_file], check=True)

        # 7. Wait for the job to complete
        rst_out = f"{step_name}.rst"
        wait_for_file(rst_out)
        print(f"Step {step_name} completed.")

        # 8. Prepare variables for the next loop iteration
        os.chdir('..')
        previous_step_dir = current_dir
        coords_file = rst_out  # The output of this step is the input for the next

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
