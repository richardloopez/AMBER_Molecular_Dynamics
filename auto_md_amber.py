#!/usr/bin/env python3

import os
import subprocess
import time

# Definitions for the maximun number of restrains and productions (sequential)  
restraints = [50, 10, 0]  # Restraints for NPT, in desired order
num_md = 2                 # Number of production (md) runs

# Function for executing the common step between min, heat, npt and md   
def run_step(step_name, previous_step, input_files, in_content, sh_modification):
    """
    Executes one step of the simulations in a modular way.

    Args:
        step_name (str): Name of the current step (i.e. 'min', 'heat', 'npt', 'md').
        previous_step (str): Name of the previous step (i.e. 'parmed' para 'min', 'min' para 'heat').
        input_files (list of str): Archivos de entrada a copiar desde el paso anterior.
        in_content (str): .in file content for current step.
        sh_modification (str): Specific modification of the .sh file for current step.
    """
    # Create current step folder and move to it
    os.makedirs(step_name, exist_ok=True)
    os.chdir(step_name)

    # Copy neccesary files form the previous folder
    for file in input_files:
        subprocess.run(['cp', f'../{previous_step}/{file}', '.'])

    # Create .in file for current step 
    with open(f'{step_name}.in', 'w') as f:
        f.write(in_content)

    # Generate .sh file using pmemd.cuda
    subprocess.run(['launch_pmemd.cuda', '0', step_name])

    # Modify .sh to include additional refferences if neccesary 
    with open(f'{step_name}.sh', 'r+') as f:
        content = f.read()
        content = content.replace(
            "$AMBERHOME/bin/pmemd.cuda -O -i", sh_modification
        )
        f.seek(0)
        f.write(content)
        f.truncate()

    # Launch job
    subprocess.run(['sbatch', f'{step_name}.sh'])

    # Wait until .rst of this step generates
    rst_file = f'{step_name}.rst'
    while not os.path.isfile(rst_file):
        print(f"Esperando a que termine el trabajo {step_name}.sh y se genere {rst_file}...")
        time.sleep(1)  #Wait 1 seconds
    print(f"Trabajo {step_name}.sh ha terminado y se generó {rst_file}.")

    # Return to main folder
    os.chdir('..')


# Execution of the modular process for each step
def main():
    # Parmed
    os.makedirs('parmed', exist_ok=True)
    os.chdir('parmed')
    subprocess.run(['cp', '../bases/system.prmtop', '.'])
    subprocess.run(['cp', '../bases/system.inpcrd', '.'])

    # Execute parmed block with module purge.
    parmed_commands = """
module purge
parmed -p system.prmtop << EOF
hmassrepartition
outparm system_hmass.prmtop
quit
EOF
"""
    # Execute parmed commands in an isolated thread
    subprocess.run(parmed_commands, shell=True, executable='/bin/bash')

    # Return to main folder
    os.chdir('..')

    # Run min and heat steps only once
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
maxcyc=15000,
ncyc=2000,
ntpr=25,
ntwx=100,
cut=8.0, ntr=1, restraintmask = ':1', restraint_wt = {restraints[0]}.,
/
""",
            "sh_modification": "$AMBERHOME/bin/pmemd.cuda -O -i min.in -o min.out -p system_hmass.prmtop -c system.inpcrd -r min.rst -x min.mdcrd -ref system.inpcrd"
        },
        {
            "name": "heat",
            "previous": "min",
            "input_files": ["system_hmass.prmtop", "min.rst"],
            "in_content": f"""\
&cntrl
imin = 0, nstlim = 1000000, dt = 0.001,
irest = 0, ntx = 1, ig = -1,
tempi = 100.0, temp0 = 298.0,
ntc = 2, ntf = 2, tol = 0.00001,
ntwx = 10000, ntwr = 5000, ntpr = 1000,
cut = 8.0, iwrap = 0,
ntt = 3, gamma_ln=1., ntb = 1, ntp = 0,
nscm = 0, ntr=1, restraintmask = ':1', restraint_wt = {restraints[0]}.,
/
""",
            "sh_modification": "$AMBERHOME/bin/pmemd.cuda -O -i heat.in -o heat.out -p system_hmass.prmtop -c min.rst -r heat.rst -x heat.mdcrd -ref min.rst"
        }
    ]

    # Execute min and heat
    for step in steps:
        run_step(
            step_name=step["name"],
            previous_step=step["previous"],
            input_files=step["input_files"],
            in_content=step["in_content"],
            sh_modification=step["sh_modification"]
        )

    # Define configurations for each NPT step with specific restraints
    for i, restraint in enumerate(restraints):
        step_name = f"npt{restraint}"
        previous_step = 'heat' if i == 0 else f"npt{restraints[i-1]}"
        input_files = ["system_hmass.prmtop", f"{previous_step}.rst"]
        in_content = f"""\
&cntrl
imin = 0, nstlim = 1000000, dt = 0.001,
irest = 1, ntx = 5, ig = -1,
temp0 = 298.0,
ntc = 2, ntf = 2, tol = 0.00001,
ntwx = 10000, ntwr = 1000, ntpr = 1000,
cut = 8.0, iwrap = 0,
ntt = 3, gamma_ln=1, ntb = 2, ntp = 1, barostat=2, ntr=1, restraintmask = ':1', restraint_wt = {restraint},
/
"""
        sh_modification = f"$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p system_hmass.prmtop -c {previous_step}.rst -r {step_name}.rst -x {step_name}.mdcrd -ref {previous_step}.rst"
        
        # Execute each NPT step
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content,
            sh_modification=sh_modification
        )

    # Define settings for each additional MD simulation
    for i in range(1, num_md + 1):
        step_name = f"md{i}"
        previous_step = 'npt0' if i == 1 else f"md{i-1}"
        input_files = ["system_hmass.prmtop", f"{previous_step}.rst"]
        in_content = """\
&cntrl
imin = 0, nstlim = 50000000, dt = 0.004,
irest = 1, ntx = 5, ig = -1,
temp0 = 298.0,
ntb = 2, ntc = 2, ntf=2, tol = 0.00001,
ntwx = 50000, ntwv= -1, ntwr = 50000, ntpr = 10000,
cut = 8.0, iwrap = 0,
ntt = 3, gamma_ln=5., ntp = 1, barostat=2,
/
"""

        sh_modification = f"$AMBERHOME/bin/pmemd.cuda -O -i {step_name}.in -o {step_name}.out -p system_hmass.prmtop -c {previous_step}.rst -r {step_name}.rst -x {step_name}.mdcrd -ref {previous_step}.rst"
        
        # Execute each md step
        run_step(
            step_name=step_name,
            previous_step=previous_step,
            input_files=input_files,
            in_content=in_content,
            sh_modification=sh_modification
        )

if __name__ == '__main__':
    main()

