#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import readline

# Function to process each .agr file and return the data
def process_agr(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Filter lines containing data (those not starting with "@")
    data = [line.strip() for line in lines if not line.startswith("@") and line.strip()]
    # Split columns into separate lists
    columns = [line.split() for line in data]
    return columns

# Request the user for the RMSD files for the receptor and ligand
receptor_file = input("Enter the receptor RMSD file name (e.g., receptor_rmsd.agr): ")
ligand_file = input("Enter the ligand RMSD file name (e.g., ligand_rmsd.agr): ")
ligand_receptor_file = input("Enter the ligand+receptor RMSD file name (e.g., ligand+receptor_rmsd.agr): ")

# List of .agr files and their titles
agr_files = [
    (receptor_file, "Receptor"),
    (ligand_file, "Ligand"),
    (ligand_receptor_file, "Ligand+Receptor")
]
output_file = "rmsd_columns.csv"

# Create a list to store all rows for the CSV file
output_lines = []

# Add headers to the first line of the CSV
headers = []
for _, title in agr_files:
    headers.append(title)
    headers.append("")  # Space for the second column (always empty)
    headers.append("")  # Blank column between blocks
output_lines.append(",".join(headers))

# Process each file
file_data = [process_agr(file) for file, _ in agr_files]

# Get the maximum number of rows across all files
max_rows = max(len(data) for data in file_data)

# Combine the data from the files into columns
for i in range(max_rows):
    row = []
    for data in file_data:
        if i < len(data):
            row.extend(data[i])  # Add the existing row
        else:
            row.extend(["", ""])  # Add empty columns if there's no data
        row.append("")  # Add an empty column between sets
    output_lines.append(",".join(row))

# Write all lines to the CSV file
with open(output_file, "w") as f:
    for line in output_lines:
        f.write(line + "\n")

print(f"CSV file saved as '{output_file}'")

