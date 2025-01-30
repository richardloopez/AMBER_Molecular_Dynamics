#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import tempfile

# Request the user for the pose number, parm file, and center residue range
pose = input("Enter the number of the pose you want to select: ")
parm_file = input("Enter the path to the parm file (*.prmtop): ")
trajectory_file = input("Enter the trajectory file (*.mdcrd or *.dcd): ")
center_residues = input("Enter the range of residues for 'center' (e.g., :1-25): ")

# Create a temporary file for the cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:  # Opening the file in write mode
    tmpfile_name = tmpfile.name

    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {parm_file}
trajin {trajectory_file} {pose} {pose} 1 ##########
center :{center_residues} ##########
image familiar
trajout {pose}.pdb ##############
run
quit
""")

# Execute cpptraj with the temporary command file
os.system(f"cpptraj -i {tmpfile_name}")

# Remove the temporary file after execution
os.remove(tmpfile_name)

