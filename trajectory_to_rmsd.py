#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import tempfile
import readline

# Request the user for the initial and final residue numbers
topology_file = input("Enter the topology file (*.prmtop): ")
trajectory_file = input("Enter the trajectory file (*.mdcrd or *.dcd): ")
residues = input("Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")

# Request the user for the base name of the output file
output_base_name = input("Enter the base name for the output file (without extension): ")

# Create a temporary file for the cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {topology_file}
trajin {trajectory_file}
rms ToFirst :{residues}&!@H= first out {output_base_name}_rmsd.agr mass
run
quit
""")

# Run cpptraj with the temporary command file
print("Running cpptraj to calculate RMSD...")
os.system(f"cpptraj -i {tmpfile_name}")

# Delete the temporary file after execution
os.remove(tmpfile_name)

# Inform the user that the task is complete
print(f"RMSD calculation completed. The output file '{output_base_name}_rmsd.agr' has been generated.")

