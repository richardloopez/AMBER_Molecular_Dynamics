#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile
import readlines

# Request the user for the parameter files and other options
parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file
residues_range = input("Enter the residue range for watershell (e.g., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")  # Residue range for watershell

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {parm_file}
trajin {traj_file}
watershell :{residues_range} out watershell.out.dat
run
quit
""")

# Execute cpptraj with the temporary command file
subprocess.run(["cpptraj", "-i", tmpfile_name])

# Remove the temporary file after execution
os.remove(tmpfile_name)

print("Watershell analysis completed. Results saved in 'watershell.out.dat'.")

