#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile

# Request the user for the necessary files and ranges
parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file
ligand_range = input("Enter the ligand residue range (e.g., 1-1): ")  # Residue range for ligand
receptor_range = input("Enter the receptor residue range (e.g., 2-25): ")  # Residue range for receptor

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {parm_file}
trajin {traj_file}
lie out lie.dat :{ligand_range} :{receptor_range}
run
quit
""")

# Execute cpptraj with the temporary command file
subprocess.run(["cpptraj", "-i", tmpfile_name])

# Remove the temporary file after execution
os.remove(tmpfile_name)

print("Lie analysis completed. Results saved in 'lie.dat'.")

