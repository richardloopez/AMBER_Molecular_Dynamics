#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import csv
import os
import subprocess

#############################################################################################################################################
# Input -> dihedrals_grouped_by_conformation.csv | REVIEW EACH SECTION CAREFULLY. #
#############################################################################################################################################



parm_file = "system_hmass.prmtop"
traj_file = "md1.dcd"

dihedrals_grouped_by_conformation_csv = "/home/richard/pruebas/md1/Dihedral_analysis_results/dihedrals_grouped_by_conformation.csv" #Output from Multi_dihedral_analyzer.py

destination_folder_name = "dcd_conformation_splitter_results"
this_script_name = "dcd_conformation_splitter.py" # Only needed if you want to copy this script to the results folder (trazability purposes)

            # The csv file should have the following format:
#########################################################################
####          classification,num_frames,frame_indices                ####
####          AAKLRRYY,6,"[352, 355, 357, 358, 1102, 1143]"          ####
####                                                                 ####
####                                                                 ####
##########################################################################


#############################################################################################################################################
# END OF INPUT #
#############################################################################################################################################




#############################################################################################################################################
# SPLITTING #
#############################################################################################################################################



# Extract the conformations from the csv file

if os.path.isfile(dihedrals_grouped_by_conformation_csv) == False:
    raise Exception(f"The file {dihedrals_grouped_by_conformation_csv} does not exist. Please, check the path.")

with open(dihedrals_grouped_by_conformation_csv, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    all_conformations = []
    for row in reader:
        classification = row[0]
        num_frames = int(row[1])
        frame_indices = eval(row[2])  # Convert string representation of list to actual list
        all_conformations.append((classification, num_frames, frame_indices))


# Move to the destination folder and copy necessary files

os.makedirs(destination_folder_name, exist_ok=True)
os.chdir(destination_folder_name)

subprocess.run(["cp", os.path.join("..", this_script_name), "."])
subprocess.run(["cp", os.path.join("..", parm_file), "."])
subprocess.run(["cp", os.path.join("..", traj_file), "."])  
subprocess.run(["cp", os.path.join("..", dihedrals_grouped_by_conformation_csv), "."])


# Generate the function to create the cpptraj input files and execute cpptraj

for conf in all_conformations:
    trajin_lines = "\n".join([f"trajin {traj_file} {item} {item}" for item in conf[2]])
    input_filename = f"dcd_splitter_input_{conf[0]}_{conf[1]}frames.in"
    with open(f"{input_filename}", "w") as f:
        f.write(f"""### Splitting conformation {conf[0]} with {conf[1]} frames ###
parm {parm_file}
{trajin_lines}
trajout {conf[0]}_{conf[1]}frames.dcd dcd
run
quit""")
    
    # Execute cpptraj
    subprocess.run(["cpptraj", "-i", f"{input_filename}"])


#############################################################################################################################################
# JUST FOR FUN: TO MAKE SURE #
#############################################################################################################################################

# Let's see if the files were created
print("""############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
      # Checking if everything went fine...                                   
      # This may take a while, take a marinera and relax
      # If you see any error message below, please, check the folder and your files
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################""")
file_count = len([f for f in os.listdir() if os.path.isfile(f)])
file_expected = len(all_conformations)*2 + 4  # Each conformation generates 2 files (input and output dcd) + 4 other files (script, parm, traj, csv)

all_ok = True

if file_count == file_expected:
    print(f"All done! {file_count} files were created in the folder {destination_folder_name}. Now give me a moment to check if everything is correct...")
else:
    print(f"Warning: {file_count} files were created, but {file_expected} were expected. Please, check the folder {destination_folder_name}.")
    all_ok = False

prefix_cpptraj_input = "dcd_splitter_input_"
suffix_cpptraj_input = ".in"
suffix_dcd = ".dcd"

for conf in all_conformations:
    input_file = f"{prefix_cpptraj_input}{conf[0]}_{conf[1]}frames{suffix_cpptraj_input}"
    dcd_file = f"{conf[0]}_{conf[1]}frames{suffix_dcd}"
    if not os.path.isfile(input_file):
        print(f"Error: Expected cpptraj input file {input_file} not found.")
        all_ok = False
    if not os.path.isfile(dcd_file):
        print(f"Error: Expected output DCD file {dcd_file} not found.")
        all_ok = False
    if os.path.isfile(input_file) and os.path.isfile(dcd_file):
        print(f"Successfully checked: Input file '{input_file}' matches output file '{dcd_file}'.")
print("""############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
      # Crucial message below, please read carefully...
############################################################################################################################################################
############################################################################################################################################################

#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓""")

if all_ok:
    print("All files were created successfully. The process finished correctly. Have a nice day AND eat marineras!")
else:
    print("One or more errors occurred during file creation. Please review the messages above and check your results.")

print("""#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
      
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################""")

 
