#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess

# Request parameters from the user
parm_file = input("Enter the parameter file name (*.prmtop): ")  # Your parameter file
traj_file = input("Enter the trajectory file name (*.dcd or *.mdcrd): ")  # Your trajectory file
num_frames = int(input("Enter the total number of frames: "))  # Total number of frames (adjust as per your file)
residue1 = int(input("Enter the number of the first residue to study: "))  # Number of the first residue to consider
residue2 = int(input("Enter the number of the last residue to study: "))  # Number of the last residue to consider
include_intramol = input("Do you want to include intramolecular hydrogen bonds? (y/n): ").lower() == 'y'  # Ask if user wants to include intramol interactions
output_dir = "hbond_results"  # Directory to save results

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize results table
results = []
interactions_per_frame = []  # List to store number of interactions per frame and the interactions

# Loop through each frame of the trajectory
for frame in range(1, num_frames + 1):
    # Create cpptraj input file for this frame
    input_file = f"cpptraj_input_{frame}.in"
    with open(input_file, "w") as f:
        f.write(f"parm {parm_file}\n")
        f.write(f"trajin {traj_file} {frame} {frame}\n")
        # Add or exclude intramolecular option based on user input
        intramol_option = "" if include_intramol else " nointramol"
        f.write(f"hbond contacts :{residue1}-{residue2} avgout avg_hbond.dat{intramol_option}\n")

    # Run cpptraj for this frame
    subprocess.run(["cpptraj", "-i", input_file])

    # Read the output file and extract the interactions
    output_file = "avg_hbond.dat"
    with open(output_file, "r") as f:
        lines = f.readlines()

    # Extract hydrogen bond interactions and store them
    interactions = []
    for line in lines:
        if not line.startswith("#Acceptor"):  # Add lines that don't start with "#Acceptor"
            interactions.append(line.strip())

    # Count the interactions and store them in the results
    num_interactions = len(interactions)
    results.append((frame, num_interactions, interactions))
    interactions_per_frame.append((frame, num_interactions, interactions))  # Store interactions per frame

    # Clean up temporary files
    os.remove(input_file)
    os.remove(output_file)

# Write results to a CSV file with column headers
with open(os.path.join(output_dir, "hbond_summary.csv"), "w") as f:
    # Write column headers
    f.write("Frame,Num_Interactions,Acceptor,DonorH,Donor,Donor_Num,Acc_Num,Distance,Angle\n")
    for frame, num_interactions, interactions in results:
        for interaction in interactions:
            interaction_data = interaction.split()
            f.write(f"{frame},{num_interactions},{','.join(interaction_data)}\n")

# Sort interactions by the number of interactions in descending order
interactions_per_frame_sorted = sorted(interactions_per_frame, key=lambda x: x[1], reverse=True)

# Write a summary with the number of interactions per frame in descending order, and the interactions
with open(os.path.join(output_dir, "interactions_per_frame.csv"), "w") as f:
    # Write column headers
    f.write("Frame,Num_Interactions,Interactions\n")
    for frame, num_interactions, interactions in interactions_per_frame_sorted:
        # Convert interactions to a string for writing, separating by commas
        interactions_str = " | ".join([",".join(interaction.split()) for interaction in interactions])
        f.write(f"{frame},{num_interactions},{interactions_str}\n")

print("Analysis complete. Results saved in 'hbond_summary.csv' and 'interactions_per_frame.csv'.")

