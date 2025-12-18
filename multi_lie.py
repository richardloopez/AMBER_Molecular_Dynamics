#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import csv
import os
import shutil
import subprocess
import tempfile
import readline
import numpy as np
import re

# Inputs from the user 

parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file
ligand_inp = input("Enter the ligand residue range (e.g., 1-1), numbers separated by commas are also accepted (e.g., 1, 50, 75): ") # Residue range for ligand
receptor_inp = input("Enter the receptor residue range (e.g., 2-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): ")  # Residue range for receptor


# Manage the inputs to generate non-ranged data

ligand_definitive = []
receptor_definitive = []

def ranger_expander(inp, definitive):
    for item in inp.split(","):
        if "-" in item:
            beginning, ending = map(int, item.split("-"))
            definitive.extend(range(beginning, ending + 1))
        else:
            definitive.append(int(item))

ranger_expander(ligand_inp, ligand_definitive)
ranger_expander(receptor_inp, receptor_definitive)


# Change to the final dir

base_folder = os.getcwd()

os.makedirs("multi_lie_analysis", exist_ok=True)
os.chdir("multi_lie_analysis")
cwd = os.getcwd()

parm_file_path = os.path.join(base_folder, parm_file)
parm_file_destination = os.path.join(cwd, parm_file)

traj_file_path = os.path.join(base_folder, traj_file)
traj_file_destination = os.path.join(cwd, traj_file)

shutil.copy2(parm_file_path, parm_file_destination)
shutil.copy2(traj_file_path, traj_file_destination)




# Cpptraj lie

for resid_l in ligand_definitive:
    for resid_r in receptor_definitive:


        # Create a temporary file for cpptraj commands
        with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
            tmpfile_name = tmpfile.name
            # Write the cpptraj commands to the temporary file
            tmpfile.write(f"""
parm {parm_file}
trajin {traj_file}
lie out lie_LR{resid_l}_RR{resid_r}.dat :{resid_l} :{resid_r}
run
quit
""")
        # Execute cpptraj with the temporary command file
        subprocess.run(["cpptraj", "-i", tmpfile_name])

        # Remove the temporary file after execution
        os.remove(tmpfile_name)

        print(f"Lie analysis completed. Results saved in 'lie_LR{resid_l}_RR{resid_r}.dat'.")
        
        
# Manage the data from lie.dat



def process_lie_file(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    # Extract numeric data (skip headers or malformed lines)
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3:
            try:
                data.append([float(parts[0]), float(parts[1]), float(parts[2])])
            except ValueError:
                continue  # skip lines that are not numeric

    data = np.array(data)

    if data.shape[0] == 0:
        print(f"Empty or invalid file: {filepath}")
        return

    # Calculate averages and standard deviations
    eelec_avg = np.mean(data[:, 1])
    eelec_std = np.std(data[:, 1])
    evdw_avg = np.mean(data[:, 2])
    evdw_std = np.std(data[:, 2])

    summary_line = (
        f"""
        # EELEC_AV: {eelec_avg:.4f}
        # EELEC_STDDEV: {eelec_std:.4f}
        # EVDW_AV: {evdw_avg:.4f}
        # EVDW_STDDEV: {evdw_std:.4f}
        """
    )

    # Prepend the summary line to the file
    with open(filepath, "w") as file:
        file.write(summary_line)
        file.writelines(lines)

    print(f"Processed: {filepath}")




for filename in os.listdir(cwd):
    if filename.endswith(".dat"):
        filepath = os.path.join(cwd, filename)
        process_lie_file(filepath)


        
        
        
# Take the final data form lie.dat        


def take_data_for_final_csv(filepath):
    data_dict = {}
    filename = os.path.basename(filepath)
    
    with open(filepath, "r") as file:
        lines = file.readlines()

    # Temporary variables to store values for the current file
    EELEC_AV = None
    EELEC_STDDEV = None
    EVDW_AV = None
    EVDW_STDDEV = None

    for line in lines:
        parts = line.split()

        # Look for tags and extract the last element which should be the value
        if "EELEC_AV:" in line:
            EELEC_AV = float(parts[-1])
        elif "EELEC_STDDEV:" in line:
            EELEC_STDDEV = float(parts[-1])
        elif "EVDW_AV:" in line:
            EVDW_AV = float(parts[-1])
        elif "EVDW_STDDEV:" in line:
            EVDW_STDDEV = float(parts[-1])

    # Store the extracted values in a dictionary with filename as key
    data_dict[filename] = {
        "EELEC_AV": EELEC_AV,
        "EELEC_STDDEV": EELEC_STDDEV,
        "EVDW_AV": EVDW_AV,
        "EVDW_STDDEV": EVDW_STDDEV
    }

    return data_dict


# Dictionary to accumulate data from all files
all_data = {}

for filename in os.listdir(cwd):
    if filename.endswith(".dat"):
        filepath = os.path.join(cwd, filename)
        file_data = take_data_for_final_csv(filepath)

        # Update the main dictionary with data from this file
        all_data.update(file_data)
        
        

# Write ultimate csv

def write_data_to_csv(data_dict, output_filename):
    headers = [
        "filename", "R1", "R2", 
        "EELEC_AV", "EELEC_STDDEV", 
        "EVDW_AV", "EVDW_STDDEV",
        "TOTAL_AV", "TOTAL_STDDEV"
    ]

    with open(output_filename, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for filename, values in data_dict.items():
            # Extract R1 and R2 from filename using regex
            match = re.match(r"lie_LR(\d+)_RR(\d+)\.dat", filename)
            if match:
                R1 = int(match.group(1))
                R2 = int(match.group(2))
            else:
                R1 = ""
                R2 = ""

            # Get values, defaulting to inf if missing
            EELEC_AV = values.get("EELEC_AV", "inf")
            EELEC_STDDEV = values.get("EELEC_STDDEV", "inf")
            EVDW_AV = values.get("EVDW_AV", "inf")
            EVDW_STDDEV = values.get("EVDW_STDDEV", "inf")

            # Calculate TOTAL_AV and TOTAL_STDDEV
            TOTAL_AV = EELEC_AV + EVDW_AV
            TOTAL_STDDEV = (EELEC_STDDEV ** 2 + EVDW_STDDEV ** 2) ** 0.5

            row = {
                "filename": filename,
                "R1": R1,
                "R2": R2,
                "EELEC_AV": EELEC_AV,
                "EELEC_STDDEV": EELEC_STDDEV,
                "EVDW_AV": EVDW_AV,
                "EVDW_STDDEV": EVDW_STDDEV,
                "TOTAL_AV": TOTAL_AV,
                "TOTAL_STDDEV": TOTAL_STDDEV
            }
            writer.writerow(row)

write_data_to_csv(all_data, "final_results_with_residues.csv")
print("Data saved to final_results_with_residues.csv")

        
        
        
        
        
