#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile
import readline

# Request the user for the parameter files and other options
parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file
residues_range = input("Enter the residue range for hydrogen bond contacts (e.g., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")  # Residue range for hydrogen bonds
include_intramol = input("Do you want to include intramolecular hydrogen bonds? (y/n): ").lower() == 'y'  # Ask if user wants intramol included

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    intramol_option = "" if include_intramol else " nointramol"
    tmpfile.write(f"""parm {parm_file}
trajin {traj_file}
hbond contacts :{residues_range} avgout avg_hbond.dat{intramol_option}
run
quit
""")

# Execute cpptraj with the temporary command file
subprocess.run(["cpptraj", "-i", tmpfile_name])

# Remove the temporary file after execution
os.remove(tmpfile_name)

print("Hydrogen bond analysis completed. Results saved in 'avg_hbond.dat'.")

