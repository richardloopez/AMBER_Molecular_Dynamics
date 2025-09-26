#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.


###################################### IMPORTS ######################################
import os
import readline
import glob
#######################################################################################




################################ AUTOCOMPLETE FOR FILE PATHS ############################
# Autocomplete function for file paths
def complete_path(text, state):
    if not text:
        completions = os.listdir('.')
    else:
        completions = glob.glob(text + '*')
    try:
        return completions[state]
    except IndexError:
        return None
      
  # Set up readline for autocompletion  
readline.set_completer(complete_path)
readline.parse_and_bind("tab: complete")

############################################################################################




################################# REQUEST USER INPUT ##################################


# Request the user for the initial and final residue numbers
topology_file = input("Enter the topology file (*.prmtop): ")
trajectory_file = input("Enter the trajectory file (*.mdcrd or *.dcd): ")
residues_ligand = input("| LIGAND | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")
residues_receptor = input("| RECEPTOR | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")
residues_ligandreceptor = input("| LIGAND+RECEPTOR | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")

ligand_file = "ligand_rmsd.agr"
receptor_file = "receptor_rmsd.agr"
ligandreceptor_file = "ligandreceptor_rmsd.agr"

#########################################################################################


############################### CPPTRAJ RMSD CALCULARTIONS #################################
# Create a file for the cpptraj commands (for traceability)
cpptraj_cmd_file = "cpptraj_commands.in"

with open(cpptraj_cmd_file, "w") as cmdfile:
    cmdfile.write(f"""parm {topology_file}
trajin {trajectory_file}
rms ligand_rmds :{residues_ligand}&!@H= first out {ligand_file} mass
rms receptor_rmds :{residues_receptor}&!@H= first out {receptor_file} mass
rms ligandreceptror_rmds :{residues_ligandreceptor}&!@H= first out {ligandreceptor_file} mass
run
quit
""")

# Run cpptraj with the command file
print("Running cpptraj to calculate RMSD...")
os.system(f"cpptraj -i {cpptraj_cmd_file}")

# Inform the user that the task is complete
print(f"RMSD calculation completed. Begginning with the CSV-COLUMNS adaptation.")

############################################################################################





############################### CSV-COLUMNS ADAPTATION #################################

# Function to process each .agr file and return the data
def process_agr(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Filter lines containing data (those not starting with "@")
    data = [line.strip() for line in lines if not line.startswith("@") and line.strip()]
    # Split columns into separate lists
    columns = [line.split() for line in data]
    return columns


# List of .agr files and their titles
agr_files = [
    (receptor_file, "Receptor"),
    (ligand_file, "Ligand"),
    (ligandreceptor_file, "LigandReceptor")
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




############################################################################################



