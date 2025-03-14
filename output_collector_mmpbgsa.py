#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import re
import csv

# Define the name of the output file
results_file = 'mmpbsa_results.csv'
comma_separator = ","

def search_results_folders():
    results = []
    # Search for folders matching the pattern TO_*_FROM_*_NUM_NUM
    for to_folder in os.listdir('.'):
        if to_folder.startswith('TO_') and re.match(r'TO_.*_FROM_.*_\d+_\d+', to_folder):
            to_folder_path = os.path.join('.', to_folder)
            if os.path.isdir(to_folder_path):
                # Search for MMPBSA_* subfolders within the TO_* folder
                for mmpbsa_folder in os.listdir(to_folder_path):
                    if mmpbsa_folder.startswith('MMPBSA'):
                        mmpbsa_folder_path = os.path.join(to_folder_path, mmpbsa_folder)
                        if os.path.isdir(mmpbsa_folder_path):
                            dat_file = os.path.join(mmpbsa_folder_path, 'FINAL_RESULTS_MMPBSA.dat')
                            if os.path.exists(dat_file):
                                results.append({
                                    'to_folder': to_folder,  # Use the name of the TO_* folder
                                    'dat_file': dat_file
                                })
    return results

def extract_totals(file_path):
    totals = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Search for all lines starting with TOTAL and capture everything that follows
            matches = re.findall(r'TOTAL\s+(.*)', content)
            totals = [match.strip() for match in matches]
    except IOError:
        print(f"Error opening file: {file_path}")
    return totals

def process_mmpbsa_folders(folders):
    results = []
    for folder in folders:
        totals = extract_totals(folder['dat_file'])
        results.append({
            'to_folder': folder['to_folder'],  # Use the name of the TO_* folder
            'totals': totals
        })
    return results

def write_results_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['TO_Folder'])

        for result in results:
            to_folder = result['to_folder']  # Use the name of the TO_* folder
            row = [to_folder] + result['totals']
            writer.writerow(row)

def replace_commas_with_spaces(file):
    with open(file, 'r') as file:
        content = file.read()

    modified_content = content.replace(',', ' ')

    with open(file, 'w') as file:
        file.write(modified_content)

# Execute the process
results_folders = search_results_folders()
final_results = process_mmpbsa_folders(results_folders)

# Write the results to the CSV file
write_results_csv(final_results, results_file)

# Replace commas with spaces in the file
replace_commas_with_spaces(results_file)

print(f"Process completed. Results saved in {results_file} with spaces instead of commas.")
print("Remember that the .csv should be separated by spaces and the first value is not detected by Excel (it needs to be separated manually)")

