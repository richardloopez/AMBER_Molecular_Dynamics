#!/usr/bin/env python3

import csv
import re
import readline  # For interactive autocompletion
from pathlib import Path

def get_validated_input(prompt, input_type=None):
    """Function for validating inputs with retries."""
    while True:
        try:
            value = input(prompt).strip()
            if input_type == int:
                return int(value)
            elif input_type == float:
                return float(value)
            elif input_type is None:
                return value
        except ValueError:
            print(f"Invalid input. Please enter a valid value.")

# Enable autocompletion
readline.parse_and_bind("tab: complete")

# Interactive configuration
input_csv_file = get_validated_input("CSV file to search in (e.g., distances_summary.csv): ")

# List to store molecule codes
molecule_codes = []

# Input loop for molecule codes
while True:
    molecule_code = get_validated_input("Molecule code to search for (e.g., WAT): ")
    molecule_codes.append(molecule_code)
    
    add_another = input("Search for another molecule? (yes/no): ").strip().lower()
    if add_another != 'yes':
        break

# Generate output CSV file name with all molecule codes
output_csv_file = Path(input_csv_file).stem + f"_{'_'.join(molecule_codes)}_counts.csv"

# Validate input CSV file existence
try:
    Path(input_csv_file).resolve(strict=True)
except FileNotFoundError:
    print(f"Error: The file {input_csv_file} does not exist.")
    exit(1)

# Read the input CSV file
with open(input_csv_file, 'r') as file:
    reader = csv.reader(file)
    data = list(reader)

# Prepare the output data
header_row = ["Frame"]
for code in molecule_codes:
    header_row.extend([code, f"Residues_{code}", f"Number_{code}"])

output_data = [header_row]

# Process each row (frame)
for row in data[1:]:
    frame = row[0]
    residues = row[1].split(',')  # Split residues by comma
    
    output_row = [frame]
    for code in molecule_codes:
        # Count occurrences of the molecule code
        molecule_matches = [res for res in residues if res.startswith(code + '_')]
        molecule_count = len(molecule_matches)
        
        # Prepare output row
        output_row.extend([code, ','.join(molecule_matches), molecule_count])
    
    output_data.append(output_row)

# Write the output CSV file
with open(output_csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(output_data)

print(f"Completed! Results in: {output_csv_file}")
