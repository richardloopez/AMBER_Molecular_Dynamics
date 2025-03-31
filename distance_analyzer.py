#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R

import subprocess
from pathlib import Path
import csv
import readline
import os

def get_validated_input(prompt, input_type=None, min_value=None, max_value=None):
    """Function for validating inputs with retries."""
    while True:
        try:
            value = input(prompt).strip()
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)

            # Validate ranges
            if min_value is not None and value < min_value:
                raise ValueError(f"Value must be greater than or equal to {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"Value must be less than or equal to {max_value}")

            return value
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

# Enable autocompletion
readline.parse_and_bind("tab: complete")

# Get user input
topology_file = get_validated_input("Topology file (*.prmtop): ")
trajectory_file = get_validated_input("Trajectory file (*.mdcrd or *.dcd): ")
target_residue = get_validated_input("Target residue (e.g., 55): ", int)
min_distance = get_validated_input("Minimum distance range (Å) (e.g., 0.0): ", float, min_value=0.0)
max_distance = get_validated_input("Maximum distance range (Å) (e.g., 5.0): ", float, min_value=min_distance)
output_folder_name = get_validated_input("Output folder name: ")

# Create output folder
output_path = Path(output_folder_name)
output_path.mkdir(parents=True, exist_ok=True)

# Generate output file names
base_name = output_folder_name
complete_distances_file = output_path / f"{base_name}_complete.csv"
filtered_distances_file = output_path / f"{base_name}_filtered.csv"
summary_distances_file = output_path / f"{base_name}_summary.csv"

# Validate input files existence
try:
    Path(topology_file).resolve(strict=True)
    Path(trajectory_file).resolve(strict=True)
except FileNotFoundError as e:
    print(f"Error: {e}. Make sure the files exist.")
    exit(1)

# Generate temporary PDB file of the first frame
cpptraj_pdb_script = f"""
parm {topology_file}
trajin {trajectory_file} 1 1 1
trajout temp_first_frame.pdb
run
quit
"""

with open("cpptraj_pdb.in", "w") as f:
    f.write(cpptraj_pdb_script)

# Execute cpptraj to generate the temporary PDB file
subprocess.run(["cpptraj", "-i", "cpptraj_pdb.in"], check=True)

# Read residue names and total number of residues from the temporary PDB file
residue_names = {}
with open("temp_first_frame.pdb", 'r') as pdb:
    for line in pdb:
        if line.startswith("ATOM"):
            residue_number = line[22:26].strip()
            residue_name = line[17:20].strip()
            if residue_number not in residue_names:
                residue_names[residue_number] = residue_name

total_residues = len(residue_names)
residues = [str(i) for i in range(1, total_residues + 1) if i != target_residue]

# Generate cpptraj script to calculate distances
cpptraj_script = [
    f"parm {topology_file}",
    f"trajin {trajectory_file}",
    *[f"distance :{target_residue} :{res} out temp_{res}.dat" for res in residues],
    "run"
]

with open("cpptraj.in", "w") as f:
    f.write("\n".join(cpptraj_script))

# Execute cpptraj to calculate distances
try:
    result = subprocess.run(
        ["cpptraj", "-i", "cpptraj.in"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error executing cpptraj: {e}")
    print(e.stdout)
    print(e.stderr)
    exit(1)

# Process distance data
distances_data = {}
for res in residues:
    temp_file = Path(f"temp_{res}.dat")
    if temp_file.exists():
        with open(temp_file) as f:
            distances = [line.split()[1] for line in f.readlines()[1:]]
        distances_data[res] = distances

# Prepare data for complete distances file
num_frames = len(next(iter(distances_data.values())))
transposed_data = [[""] * (len(residues) + 1) for _ in range(num_frames + 1)]

transposed_data[0][0] = "Frame"
for i, res in enumerate(residues):
    residue_name = residue_names.get(res, f"R{res}")
    transposed_data[0][i + 1] = f"{residue_name}_{res}"

for i in range(num_frames):
    transposed_data[i + 1][0] = i + 1
    for j, res in enumerate(residues):
        transposed_data[i + 1][j + 1] = distances_data[res][i]

# Write complete distances to CSV file
with open(complete_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(transposed_data)

# Prepare data for filtered and summary outputs
filtered_data = [transposed_data[0]]
summary_data = [["Frame", "Residues_in_range"]]

for row in transposed_data[1:]:
    frame = row[0]
    filtered_row = [frame]
    residues_in_range = []

    for i, distance in enumerate(row[1:]):
        try:
            distance_float = float(distance) if distance.strip() else None
            if distance_float is not None and min_distance <= distance_float <= max_distance:
                filtered_row.append(distance)
                residue_full_name = transposed_data[0][i + 1]
                residues_in_range.append(residue_full_name)
            else:
                filtered_row.append('')
        except ValueError:
            filtered_row.append('')

    filtered_data.append(filtered_row)
    summary_data.append([frame, ",".join(residues_in_range)])

# Write filtered data to CSV
with open(filtered_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(filtered_data)

# Write summary data to CSV
with open(summary_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(summary_data)

print("\nAnalysis completed! Results in:", output_folder_name)

# Cleanup temporary files
for res in residues:
    temp_file = Path(f"temp_{res}.dat")
    if temp_file.exists():
        temp_file.unlink()
Path("cpptraj.in").unlink()
Path("cpptraj_pdb.in").unlink()
Path("temp_first_frame.pdb").unlink()
