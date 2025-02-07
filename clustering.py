#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import tempfile
import readline

# Request input files and parameters from the user
topology = input("Enter the topology file (*.prmtop): ")
trajectory = input("Enter the trajectory file (*.dcd or *.mdcrd): ")
initial_snapshot = input("Enter the number of the first snapshot to consider: ")
final_snapshot = input("Enter the number of the last snapshot to consider: ")
residue_range = input("Enter the residue range to analyze (e.g., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")
num_clusters = input("Enter the number of clusters (e.g., 10): ")
sieve_value = input("Enter the sieve value (e.g., 10): ")
maxit_value = input("Enter the max iterations for k-means (e.g., 500): ")
consider_hydrogens = input("Do you want to consider hydrogens? (y/n): ").lower()

# Check if hydrogens should be considered in the RMSD calculation
if consider_hydrogens == 'y':
    rmsd_atoms = f":{residue_range}"
else:
    rmsd_atoms = f":{residue_range}&!@H="  # Exclude hydrogens

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {topology}
trajin {trajectory} {initial_snapshot} {final_snapshot}
cluster c1 \\
 kmeans clusters {num_clusters} randompoint maxit {maxit_value} \\
 rms {rmsd_atoms} \\
 sieve {sieve_value} random \\
 out cnumvtime.dat \\
 summary summary.dat \\
 info info.dat \\
 cpopvtime cpopvtime.agr normframe \\
 repout rep repfmt pdb \\
 singlerepout singlerep.nc singlerepfmt netcdf \\
 avgout avg avgfmt pdb
run
quit
""")

# Run cpptraj with the temporary command file
print("Running cpptraj for clustering...")
os.system(f"cpptraj -i {tmpfile_name}")

# Delete the temporary file after execution
os.remove(tmpfile_name)

# Inform the user that clustering is complete
print("Clustering completed. The following output files were generated:")
print("  - cnumvtime.dat: Cluster assignment for each frame.")
print("  - summary.dat: Clustering summary.")
print("  - info.dat: Detailed information.")
print("  - rep/avg: Representative/average structures in PDB format.")

