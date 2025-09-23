#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile
import readline
import shutil
import pandas as pd
import glob

#############################################################################################################################################
# Input -> Dihedrals, and parameters for analysis. REVIEEW EACH SECTION CAREFULLY. #
#############################################################################################################################################

################################## DIHEDRALS: DEFINITION ##################################

all_dihedrals = [
    
("dihedral_1R1", [1, 2, 15, 16]),
("dihedral_1R2", [11, 14, 25, 26]),

("dihedral_2R1", [1, 15, 16, 17]),
("dihedral_2R2", [14, 25, 26, 27]),

("dihedral_3R1", [15, 16, 17, 19]),
("dihedral_3R2", [25, 26, 27, 29]),

("dihedral_4R1", [16, 17, 19, 21]),
("dihedral_4R2", [26, 27, 29, 31])

]

################################## DIHEDRAL: GROUPING ##################################

range_grouper_dihedral_1_A = [271, 90];        classification_grouper_dihedral_1_A = "A"
range_grouper_dihedral_1_B = [91, 270];      classification_grouper_dihedral_1_B = "B"

range_grouper_dihedral_2_K = [271, 90];        classification_grouper_dihedral_2_K = "K"
range_grouper_dihedral_2_L = [91, 270];      classification_grouper_dihedral_2_L = "L"   

range_grouper_dihedral_3_Q = [271, 90];        classification_grouper_dihedral_3_Q = "Q"      
range_grouper_dihedral_3_R = [91, 270];      classification_grouper_dihedral_3_R = "R"

range_grouper_dihedral_4_Y = [271, 90];        classification_grouper_dihedral_4_Y = "Y"
range_grouper_dihedral_4_Z = [91, 270];      classification_grouper_dihedral_4_Z = "Z"


# Function to create lists of atom identifiers for each dihedral (needed for cpptraj input)


    
def put_atom_in_dihedrals():
    for name, dihedral in all_dihedrals:
        globals()[f"{name}_at"] = []
        for atom in dihedral:
            globals()[f"{name}_at"].append(f"@{atom}")

put_atom_in_dihedrals()



################################## DIHEDRAL: MAKE SURE EACH COMBINATION IS CORRECT ##################################


all_dihedrals_ranges = [
    ("dihedral_1R1", dihedral_1R1_at, range_grouper_dihedral_1_A, classification_grouper_dihedral_1_A, range_grouper_dihedral_1_B, classification_grouper_dihedral_1_B),
    ("dihedral_1R2", dihedral_1R2_at, range_grouper_dihedral_1_A, classification_grouper_dihedral_1_A, range_grouper_dihedral_1_B, classification_grouper_dihedral_1_B),
    ("dihedral_2R1", dihedral_2R1_at, range_grouper_dihedral_2_K, classification_grouper_dihedral_2_K, range_grouper_dihedral_2_L, classification_grouper_dihedral_2_L),
    ("dihedral_2R2", dihedral_2R2_at, range_grouper_dihedral_2_K, classification_grouper_dihedral_2_K, range_grouper_dihedral_2_L, classification_grouper_dihedral_2_L),
    ("dihedral_3R1", dihedral_3R1_at, range_grouper_dihedral_3_Q, classification_grouper_dihedral_3_Q, range_grouper_dihedral_3_R, classification_grouper_dihedral_3_R),
    ("dihedral_3R2", dihedral_3R2_at, range_grouper_dihedral_3_Q, classification_grouper_dihedral_3_Q, range_grouper_dihedral_3_R, classification_grouper_dihedral_3_R),
    ("dihedral_4R1", dihedral_4R1_at, range_grouper_dihedral_4_Y, classification_grouper_dihedral_4_Y, range_grouper_dihedral_4_Z, classification_grouper_dihedral_4_Z),
    ("dihedral_4R2", dihedral_4R2_at, range_grouper_dihedral_4_Y, classification_grouper_dihedral_4_Y, range_grouper_dihedral_4_Z, classification_grouper_dihedral_4_Z)
]

################################## CPPTRAJ INPUT ##################################

parm_file = "system_hmass.prmtop"
traj_file = "md1.dcd"

destination_folder_name = "Dihedral_analysis_results"
this_script_name = "Multi_dihedral_analyzer.py" # Only needed if you want to copy this script to the results folder (trazability purposes)

#############################################################################################################################################
# END OF INPUT #
#############################################################################################################################################


#############################################################################################################################################
# Dihedral calculation
#############################################################################################################################################

# Move to a new directory

dataset_name = destination_folder_name  
new_dir = (f"{dataset_name}")
os.mkdir(new_dir)
os.chdir(new_dir)

original_parm = os.path.join(os.pardir, parm_file)
destination_parm = os.path.join(os.getcwd(), parm_file)
shutil.copy(original_parm, destination_parm)


original_traj = os.path.join(os.pardir, traj_file)
destination_traj = os.path.join(os.getcwd(), traj_file)
shutil.copy(original_traj, destination_traj)

original_this_script = os.path.join(os.pardir, this_script_name)
destination_this_script = os.path.join(os.getcwd(), this_script_name)
shutil.copy(original_this_script, destination_this_script)


#################################################################################################
# Input preparation for cpptraj

with open("dihedrals_input.txt", "w") as f:
    f.write(f"""# Dihedral calculations
parm {parm_file}
trajin {traj_file}
""")    
    for name, dihedral, range1, class1, range2, class2 in all_dihedrals_ranges:
        f.write(f"dihedral {name} {dihedral[0]} {dihedral[1]} {dihedral[2]} {dihedral[3]} out {name}.dat range360\n")
    f.write(f"""run 
quit
            """)
        
        
# Execute cpptraj
subprocess.run(["cpptraj", "-i", "dihedrals_input.txt"])

##############################################################################################
##############################################################################################

#############################################################################################################################################
# CSV Generation (cpptraj dihedrals output)
#############################################################################################################################################


####################################################### Summary CSV #########################################################################

dat_files = glob.glob("*.dat")

dataframes = []

for file in dat_files:
    # Dihedral name is extracted from the header (position 1) of each .dat file
    with open(file) as f:
        header = f.readline()
        dihedral_name = header.split()[1]
    # Read the data, ignoring the first row (header) and using whitespace as delimiter
    df = pd.read_csv(file, delim_whitespace=True, skiprows=1, names=["Frame", dihedral_name])
    dataframes.append(df.set_index("Frame"))

# Une todos los dataframes por el índice Frame
result = pd.concat(dataframes, axis=1)

# Guarda el resultado en un CSV
result.to_csv("dihedrals_summary.csv")



####################################################### Summary with classification CSV #########################################################################

summary_csv_df = pd.read_csv("dihedrals_summary.csv")

# Function to check if a value is inside a circular angular range (degrees from 0 to 360)
def in_circular_range(val, low, high):
    if low <= high:
        return low <= val < high
    else:
        # Circular range case: (e.g., 271, 90) means [271,360) U [0,90)
        return val >= low or val < high

# Add a blank column for classification
summary_csv_df["classification"] = ""

# Assign classification for each frame and dihedral using circular ranges
for idx, row in summary_csv_df.iterrows():
    frame_classifications = []
    for name in all_dihedrals_ranges:
        col = name[0]
        if col in summary_csv_df.columns:
            val = row[col]
            # Use in_circular_range instead of basic if condition
            if in_circular_range(val, name[2][0], name[2][1]):
                frame_classifications.append(name[3])
            elif in_circular_range(val, name[4][0], name[4][1]):
                frame_classifications.append(name[5])
            else:
                frame_classifications.append("X")  # "X" for out-of-range
    # Join all classifications for this frame
    summary_csv_df.at[idx, "classification"] = "".join(frame_classifications)

# Save the updated DataFrame to CSV
summary_csv_df.to_csv("dihedrals_summary_with_classification.csv", index=False)



####################################################### classification grouped by conformation CSV #########################################################################


# Group frames by unique set of classification characters (order-dependent, keep repeats)
# Here, we treat the classification string as a unique conformation label

# Create a new DataFrame grouping by the full classification string
grouped = summary_csv_df.groupby("classification")

# Prepare a summary DataFrame: classification, number of frames, frame indices
group_summary = pd.DataFrame({
    "classification": grouped.groups.keys(),
    "num_frames": [len(grouped.groups[key]) for key in grouped.groups.keys()],
    "frame_indices": [list(grouped.groups[key]) for key in grouped.groups.keys()]
})

# Save the summary DataFrame to CSV
group_summary.to_csv("dihedrals_grouped_by_conformation.csv", index=False)






