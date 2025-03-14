#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

#######At the end of the document is placed the name of the document required!!   (mmpbgsa_results.csv)  #######

import csv
from collections import defaultdict

# Specify the energy column (starting from 1, not from 0)
ENERGY_COLUMN = 2 

def analyze_mmpbsa_results(input_csv, output_csv, output_txt):
    to_data = defaultdict(list)
    
    # Read the input CSV file
    with open(input_csv, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row if present
        for row in csv_reader:
            if len(row) >= ENERGY_COLUMN:
                folder_to = row[0]
                parts = folder_to.split('_')
                to = '_'.join(parts[1:parts.index('FROM')])
                from_index = parts.index('FROM')
                from_part = '_'.join(parts[from_index+1:-2])
                start = int(parts[-2])
                end = int(parts[-1])
                energy = float(row[ENERGY_COLUMN - 1])  # Substract 1 because Python index begin in 0
                to_data[to].append((from_part, start, end, energy))

    # Prepare output files
    with open(output_csv, 'w', newline='') as csv_file, open(output_txt, 'w') as txt_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['TO', 'FROM', 'Start', 'End', 'Frames', 'Energy', 'Contribution'])

        for to, data in to_data.items():
            txt_file.write(f"\nAnalysis for {to}:\n")
            total_contribution = 0
            total_frames = 0
            
            for from_part, start, end, energy in data:
                frames = end - start
                contribution = frames * energy
                total_contribution += contribution
                total_frames += frames
                
                txt_file.write(f"  From frame {start} to {end} of {from_part}:\n")
                txt_file.write(f"    Total frames: {frames}\n")
                txt_file.write(f"    Energy: {energy:.4f}\n")
                txt_file.write(f"    Contribution: {contribution:.4f}\n")

                csv_writer.writerow([to, from_part, start, end, frames, f"{energy:.4f}", f"{contribution:.4f}"])
            
            weighted_value = total_contribution / total_frames if total_frames > 0 else 0
            
            txt_file.write(f"\nResults for {to}:\n")
            txt_file.write(f"  Total sum of frames: {total_frames}\n")
            txt_file.write(f"  Weighted value: {weighted_value:.4f}\n")

            csv_writer.writerow(['', '', '', '', total_frames, '', f"{weighted_value:.4f}"])

# Use the function
analyze_mmpbsa_results('mmpbgsa_results.csv', 'analysis_results.csv', 'analysis_results.txt') 

