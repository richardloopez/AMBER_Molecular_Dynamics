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


############################### PLOT #################################

generate_plot = input("\nGenerate publication-grade RMSD plot? (y/n): ").strip().lower()
if generate_plot == "y":
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("ERROR: matplotlib and numpy are required for plotting.")
        print("Install with: python -m pip install matplotlib numpy")
    else:
        try:
            timestep_input = input("Enter timestep (default 0.01 ns between frames): ").strip()
            timestep_ns = float(timestep_input) if timestep_input else 0.01

            plot_title = input("Plot title (press Enter for none): ").strip()
            output_pdf = "rmsd_plot.pdf"
            output_png = "rmsd_plot.png"

            with open(output_file, "r") as f:
                csv_lines = [line.strip() for line in f if line.strip()]
            header = csv_lines[0].split(",")
            ncols = len(header)

            def parse_block(lines, x_col, y_col):
                x_data, y_data = [], []
                for line in lines:
                    cols = line.split(",")
                    if x_col < len(cols) and y_col < len(cols):
                        try:
                            x_data.append(float(cols[x_col]))
                            y_data.append(float(cols[y_col]))
                        except ValueError:
                            continue
                return np.array(x_data), np.array(y_data)

            data_rows = csv_lines[1:]
            time_lig, rmsd_lig = parse_block(data_rows, 3, 4)
            time_rec, rmsd_rec = parse_block(data_rows, 0, 1)
            time_lr,  rmsd_lr  = parse_block(data_rows, 6, 7)

            time_lig = time_lig * timestep_ns
            time_rec = time_rec * timestep_ns
            time_lr  = time_lr  * timestep_ns

            matplotlib.rcParams.update({
                "font.family": "sans-serif",
                "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                "font.size": 14,
                "axes.labelsize": 16,
                "axes.titlesize": 18,
                "xtick.labelsize": 13,
                "ytick.labelsize": 13,
                "legend.fontsize": 13,
                "lines.linewidth": 1.8,
                "axes.linewidth": 1.2,
                "xtick.major.width": 1.2,
                "ytick.major.width": 1.2,
                "xtick.major.size": 6,
                "ytick.major.size": 6,
                "xtick.minor.size": 3,
                "ytick.minor.size": 3,
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "savefig.bbox": "tight",
                "savefig.dpi": 300,
            })

            fig, ax = plt.subplots(figsize=(5.5, 4.0))

            ax.plot(time_rec, rmsd_rec, color="#2166ac", label="Receptor")
            ax.plot(time_lig, rmsd_lig, color="#b2182b", label="Ligand")
            ax.plot(time_lr,  rmsd_lr,  color="#4daf4a", label="Ligand+Receptor")

            if plot_title:
                ax.set_title(plot_title)

            ax.set_xlabel("Time (ns)")
            ax.set_ylabel("RMSD (Å)")

            ax.legend(frameon=True, fancybox=False, edgecolor="black")

            ax.tick_params(direction="in", which="both")
            ax.minorticks_on()

            fig.savefig(output_pdf)
            fig.savefig(output_png, dpi=300)
            plt.close(fig)

            print(f"Publication-grade RMSD plot saved:")
            print(f"  Vector:  {output_pdf}")
            print(f"  Raster:  {output_png} (300 DPI)")

        except Exception as e:
            print(f"ERROR during plotting: {e}")

############################################################################################



