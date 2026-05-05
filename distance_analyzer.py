#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R

import subprocess
from pathlib import Path
import csv
import readline
import sys
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Enable autocompletion
readline.parse_and_bind("tab: complete")

try:
    topology_file = input("Topology file (*.prmtop): ")
    trajectory_file = input("Trajectory file (*.mdcrd or *.dcd): ")
    computing_mode = int(
        input(
            """
    Select Computing Mode:
    1. residue - residue 
    2. atom - residue 
    3. atom - atom

    > """
        ).strip()
    )

    target = int(input("Target residue or atom (i) (e.g., 55): "))
    min_distance = float(input("Minimum distance range (Å) (e.g., 0.0): "))
    max_distance = float(input("Maximum distance range (Å) (e.g., 5.0): "))
    output_folder_name = input("Output folder name: ")
except ValueError:
    logger.error("Error: Please enter valid numbers for mode, target, and distances.")
    sys.exit(1)

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
    logger.error(f"Error: {e}. Make sure the files exist.")
    sys.exit(1)

# Generate temporary PDB file of the first frame
cpptraj_pdb_script = f"""
parm {topology_file}
trajin {trajectory_file} 1 1 1
trajout temp_first_frame.pdb include_ep
run
quit
"""

with open("cpptraj_pdb.in", "w") as f:
    f.write(cpptraj_pdb_script)

# Execute cpptraj to generate the temporary PDB file
subprocess.run(["cpptraj", "-i", "cpptraj_pdb.in"], check=True)

# Read and adjust residue/atom numbers from PDB
residue_names = {}
atom_names = {}
prev_pdb_res_id = None
amber_residue_index = 0
amber_atom_index = 0

with open("temp_first_frame.pdb", "r") as pdb:
    for line in pdb:
        if line.startswith(("ATOM", "HETATM")):
            amber_atom_index += 1
            atom_key = str(amber_atom_index)

            raw_res = line[22:27]  # includes insertion code
            raw_chain = line[21]
            residue_name = line[17:20].strip()

            current_pdb_res_id = (raw_res, raw_chain, residue_name)

            # Adjust on Amber numeration (strictly sequential)
            if current_pdb_res_id != prev_pdb_res_id:
                amber_residue_index += 1
                prev_pdb_res_id = current_pdb_res_id

            adjusted_residue_key = str(amber_residue_index)
            atom_name = line[12:16].strip()

            if adjusted_residue_key not in residue_names:
                residue_names[adjusted_residue_key] = residue_name
            if atom_key not in atom_names:
                atom_names[atom_key] = (atom_name, residue_name, adjusted_residue_key)

total_residues = len(residue_names)
logger.info(f"Total residues detected: {total_residues}")
total_atoms = len(atom_names)
logger.info(f"Total atoms detected: {total_atoms}")

if computing_mode == 1:
    target_atom = None
    target_residue = str(target)
    items_to_process = [
        str(i) for i in range(1, total_residues + 1) if i != target_residue
    ]

elif computing_mode == 2:
    target_atom = target
    target_residue = None
    items_to_process = [str(i) for i in range(1, total_residues + 1)]

elif computing_mode == 3:
    target_atom = str(target)
    target_residue = None
    items_to_process = [
        str(i) for i in range(1, total_atoms + 1) if str(i) != target_atom
    ]

# Generate cpptraj script to calculate distances
cpptraj_script = [f"parm {topology_file}", f"trajin {trajectory_file}"]

if computing_mode == 1:
    cpptraj_script.extend(
        [
            f"distance :{target_residue} :{res} out temp_{res}.dat"
            for res in items_to_process
        ]
    )
elif computing_mode == 2:
    cpptraj_script.extend(
        [
            f"distance @{target_atom} :{res} out temp_{res}.dat"
            for res in items_to_process
        ]
    )
elif computing_mode == 3:
    cpptraj_script.extend(
        [
            f"distance @{target_atom} @{atom} out temp_{atom}.dat"
            for atom in items_to_process
        ]
    )

cpptraj_script.append("run")

with open("cpptraj.in", "w") as f:
    f.write("\n".join(cpptraj_script))

# Execute cpptraj to calculate distances
try:
    result = subprocess.run(
        ["cpptraj", "-i", "cpptraj.in"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    logger.info("cpptraj finished calculating distances.")
except subprocess.CalledProcessError as e:
    logger.error(f"Error executing cpptraj: {e}")
    logger.error(e.stderr)
    sys.exit(1)

# Process distance data dynamically
distances_data = {}
for item in items_to_process:
    temp_file = Path(f"temp_{item}.dat")
    try:
        with open(temp_file) as f:
            distances = [line.split()[1] for line in f.readlines()[1:]]
        distances_data[item] = distances
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if not distances_data:
    logger.error("Error: No distance data was collected. Check your cpptraj setup.")
    sys.exit(1)

# Prepare data for complete distances file
num_frames = len(next(iter(distances_data.values())))
transposed_data = [[""] * (len(items_to_process) + 1) for _ in range(num_frames + 1)]

transposed_data[0][0] = "Frame"

# Set correct headers based on mode
for i, item in enumerate(items_to_process):
    if computing_mode in [1, 2]:
        res_name = residue_names.get(item, "UNK")
        header_name = f"{res_name}_{item}"
    else:
        atom_info = atom_names.get(item, ("Atom", "UNK", "UNK"))
        atom_name = atom_info[0]
        residue_name = atom_info[1]
        adjusted_res_key = atom_info[2]
        header_name = f"{atom_name}@{residue_name}_{adjusted_res_key}_atom_{item}"

    transposed_data[0][i + 1] = header_name

for i in range(num_frames):
    transposed_data[i + 1][0] = i + 1
    for j, item in enumerate(items_to_process):
        # Prevent index errors if a file had fewer frames
        if i < len(distances_data[item]):
            transposed_data[i + 1][j + 1] = distances_data[item][i]
        else:
            transposed_data[i + 1][j + 1] = ""

# Write complete distances to CSV file
with open(complete_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(transposed_data)

# Prepare data for filtered and summary outputs
filtered_data = [transposed_data[0]]
summary_data = [["Frame", "Items_in_range"]]

for row in transposed_data[1:]:
    frame = row[0]
    filtered_row = [frame]
    items_in_range = []

    for i, distance in enumerate(row[1:]):
        try:
            distance_float = float(distance) if distance.strip() else None
            if (
                distance_float is not None
                and min_distance <= distance_float <= max_distance
            ):
                filtered_row.append(distance)
                item_full_name = transposed_data[0][i + 1]
                items_in_range.append(item_full_name)
            else:
                filtered_row.append("")
        except ValueError:
            filtered_row.append("")

    filtered_data.append(filtered_row)
    summary_data.append([frame, ",".join(items_in_range)])

# Write filtered data to CSV
with open(filtered_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(filtered_data)

# Write summary data to CSV
with open(summary_distances_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(summary_data)

logger.info(f"\nAnalysis completed! Results in: {output_folder_name}")

# Cleanup temporary files
for item in items_to_process:
    temp_file = Path(f"temp_{item}.dat")
    if temp_file.exists():
        temp_file.unlink()

for f in ["cpptraj.in", "cpptraj_pdb.in", "temp_first_frame.pdb"]:
    if Path(f).exists():
        Path(f).unlink()
