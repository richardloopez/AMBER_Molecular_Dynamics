#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile
import readline
import shutil



# Request the user for the parameter files and other options
parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file


p1 = input("Enter the number of the FIRST ATOM to study in residue 1: ")
p2 = input("Enter the number of the SECOND ATOM to study in residue 1: ")
p3 = input("Enter the number of the THIRD ATOM to study in residue 1: ")

pa = input("Enter the number of the FIRST ATOM to study in residue 2: ")
pb = input("Enter the number of the SECOND ATOM to study in residue 2: ")
pc = input("Enter the number of the THIRD ATOM to study in residue 2: ")



dataset_name = (f"atoms_R1_{p1}_{p2}_{p3}_R2_{pa}_{pb}_{pc}")






# Move to a new directory

new_dir = (f"angle_{dataset_name}")
os.mkdir(new_dir)
os.chdir(new_dir)

original_parm = os.path.join(os.pardir, parm_file)
destination_parm = os.path.join(os.getcwd(), parm_file)
shutil.copy(original_parm, destination_parm)


original_traj = os.path.join(os.pardir, traj_file)
destination_traj = os.path.join(os.getcwd(), traj_file)
shutil.copy(original_traj, destination_traj)





##############################################################################################

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name

    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {parm_file}
trajin {traj_file}
vector v1 out v1_{p1}_{p2}.dat @{p1} @{p2}
vector v2 out v2_{p2}_{p3}.dat @{p2} @{p3}
vectormath vec1 v1 vec2 v2 crossproduct out plane_alpha_{p1}_{p2}_{p2}_{p3}.dat name plane_alpha
vector va out va_{pa}_{pb}.dat @{pa} @{pb}
vector vb out vb_{pb}_{pc}.dat @{pb} @{pc}
vectormath vec1 va vec2 vb crossproduct out plane_beta_{pa}_{pb}_{pb}_{pc}.dat name plane_beta
vectormath vec1 plane_alpha vec2 plane_beta dotangle out angle_{dataset_name}.dat name final_angle
run
quit
""")

# Execute cpptraj with the temporary command file
subprocess.run(["cpptraj", "-i", tmpfile_name])

# Remove the temporary file after execution
os.remove(tmpfile_name)

##############################################################################################





print(f"""###########################################################################


OPERATION CONCLUDED. DATA USED:
-----------------------------

p1: {p1} p2: {p2} p3: {p3}
v1: {p1} and {p2}
v2: {p2} and {p3}
plane_alpha: v1 and v2

-------------------------------

pa: {pa} pb: {pb} pc: {pc}
va: {pa} and {pb}
vb: {pb} and {pc}
plane_beta: va and vb

-------------------------------
angle_{dataset_name}: plane_alpha and plane_beta

###########################################################################

      """)










