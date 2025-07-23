# AMBER_Molecular_Dynamics
	-This repository is composed by different codes for better treatment of AMBER Molecular Dynamics Data:
	-Most of them use cpptraj tool to generate the output, but implementing a user-friendly interface, without missing parameters


 **Molecular Analysis Scripts Collec on**

**0.	auto_md_amber**
This Python script automates a series of molecular dynamics (MD) simulations, including steps such as minimization (min), heating (heat), pressure equilibration (npt), and multiple MD stages (md), using Amber and pmemd.cuda. It is designed to work in a modular fashion, where each simulation step is executed sequentially in its own folder. The script handles file copying, .in file generation, .sh script generation, and submission to a cluster via sbatch.

Features
Parmed Preprocessing: Prepares the necessary input files and performs system parameter modifications.
Sequential Steps: Executes the steps of minimization, heating, pressure equilibration, and molecular dynamics.
Custom Restraints: Allows for flexible configuration of restraints in the NPT steps.
Modular Execution: Each step is executed in its own subdirectory, ensuring clean and manageable simulation workflows.
Cluster Integration: Submits jobs to a cluster using sbatch, allowing for long-running simulations.
How to Use
Preparation:

Ensure that you have Amber and pmemd.cuda installed and accessible in your environment.
Set up the directory structure with necessary files, including system.prmtop, system.inpcrd, and any other files required for the simulations.
Running the Script:

Clone the repository or download the script.
Modify the script to fit your system, including the number of MD steps and specific restraints for the NPT simulation.
Run the script using Python:
python3 <script_name>.py
Configuration:

The script will ask for restraint values for the NPT steps (e.g., 50, 10, 0) and will execute MD simulations with these values.
The job submission is handled through sbatch, ensuring jobs are run on a cluster.
Results:

The results of each simulation step (e.g., .rst, .mdcrd, .out) are saved in the respective step directories.
The script automatically waits for the completion of each step before proceeding to the next.
    





 
**1.	select_pose**
This script automates the extrac on of a specific pose from a molecular dynamics trajectory using cpptraj.Func onality: 
•	Allows user to select a specific pose 
•	Centers the pose based on a specified residue range 
•	Saves the pose as a PDB file 
Usage: 
1.	Run the script 
2.	Provide the following inputs when prompted: 
•	Pose number to extract 
•	Parm file (*.prmtop) 
•	Trajectory file (*.mdcrd or *.dcd) 
•	Residue range for centering 
Output: A PDB file with the pose number as filename (e.g., 1.pdb for pose 1) 
 
 
 
 
 
 
 
 
 
 
 
**2.	clustering** 
This script automates the clustering of molecular dynamics snapshots using cpptraj.Func onality: 
•	Performs k-means clustering on molecular trajectories 
•	Allows specifica on of parameters such as number of clusters and sieve value 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Topology file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Snapshot range to analyze 
•	Residue range for RMSD calcula ons 
•	Number of clusters 
•	Sieve value for clustering 
•	Maximum itera ons for k-means algorithm 
•	Inclusion of hydrogens in RMSD calcula on 
Output: 
•	cnumv me.dat: Cluster assignment for each frame 
•	summary.dat: Clustering process summary 
•	info.dat: Detailed clustering informa on 
•	rep/avg.pdb: Representa ve and average structures in PDB format 
•	singlerep.nc: Representa ve structures in NetCDF format 
 
 
 
 
**3.	trajectory_to_rmsd** 
This script automates the calcula on of Root Mean Square Devia on (RMSD) for a specific range of residues in a molecular dynamics trajectory.Func onality: 
•	Calculates RMSD of specified residues rela ve to the first frame of the trajectory 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Topology file (*.prmtop) 
•	Trajectory file (*.mdcrd or *.dcd) 
•	Residue range to analyze 
•	Base name for output file 
Output: An RMSD plot file (*.agr) containing RMSD data 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
**4.	rmsd_columns** 
This script processes mul ple RMSD data files (*.agr format), extracts the data, and combines them into a single CSV file.Func onality: 
•	Combines RMSD data for receptor, ligand, and ligand-receptor system 
•	Aligns datasets and fills with empty cells where data is missing 
Usage: 
1.	Run the script 
2.	Provide names of three RMSD files: 
•	Receptor RMSD file 
•	Ligand RMSD file 
•	Ligand+receptor RMSD file 
Output: A CSV file (rmsd_columns.csv) with combined RMSD data 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
**5.	hbond_average** 
This script performs hydrogen bond analysis on a molecular dynamics trajectory using cpptraj.Func onality: 
•	Calculates hydrogen bond contacts within a specified residue range 
•	Op on to include intramolecular hydrogen bonds 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Parameter file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Residue range to analyze 
•	Inclusion of intramolecular hydrogen bonds 
Output: A file (avg_hbond.dat) with average hydrogen bond contact data 
 
 
 
 
 
 
 
 
 
 
 
 
 
**6.	total_hbond_interactions** 
This script performs detailed hydrogen bond analysis on a molecular dynamics trajectory for a specified residue range.Func onality: 
•	Calculates number of hydrogen bond interac ons for each frame 
•	Generates CSV files with detailed data and summaries 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Parameter file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Number of frames in trajectory 
•	Residue range to analyze 
•	Inclusion of intramolecular hydrogen bonds 
Output: 
•	hbond_summary.csv: Summary of hydrogen bond interac ons 
•	interac ons_per_frame.csv: Number of interac ons per frame 
 
 
 
 
 
 
 
 
 
 
**7.	watershell**
This script performs water shell analysis on a molecular dynamics trajectory using cpptraj.Func onality: 
•	Analyzes water molecule interac on within a specified residue range 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Parameter file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Residue range to analyze 
Output: A file (watershell.out.dat) with water shell analysis results 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
**8.	solva on_spheres_average** 
This script calculates average solva on shell values based on data from a watershell.out.dat file.Func onality: 
•	Calculates average for first and second solva on shells 
Usage: 
1. Run the script (requires a pre-exis ng watershell.out.dat file) 
Output: A file (solva on_average.txt) with solva on shell averages 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
**9.	lie** 
This script automates Linear Interac on Energy (LIE) analysis using cpptraj.Func onality: 
•	Calculates interac on energy between a ligand and receptor for each frame of a trajectory 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Parameter file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Ligand residue range 
•	Receptor residue range 
Output: A file (lie.dat) with LIE analysis results





**10. distance_analyzer.py**

Description
This script automates the analysis of residue distances within molecular dynamics trajectories using cpptraj. It calculates distances between a specified target residue and all other residues, filters these distances based on a user-defined range, and generates comprehensive output files. Additionally, it resolves issues with PDB files containing more than 9999 residues by correctly adjusting residue numbering.

Functionality
Calculates distances between a target residue and all other residues in the trajectory using cpptraj.

Filters calculated distances based on a user-defined minimum and maximum range.

Handles PDB files with more than 9999 residues by:

Detecting and adjusting residue numbers that restart at 0 due to AMBER's limitations.

Correctly assigning unique numbers to residues by adding offsets for each cycle of 9999 residues.

Generates three CSV files:

A file containing all calculated distances.

A file containing only the distances that fall within the specified range.

A summary file that lists, for each frame, the residues within the specified distance range of the target residue.

Automatically creates an output folder to store all generated CSV files for organized access.

Cleans up all temporary files generated during the analysis.

Usage
Run the script:

python distance_analyzer.py
Provide the following inputs when prompted:

Topology file (e.g., *.prmtop)

Trajectory file (e.g., *.mdcrd or *.dcd)

Target residue number

Minimum distance for filtering (in Å)

Maximum distance for filtering (in Å)

Name of the output folder

Output
The script generates the following output files within the specified output folder:

{output_folder_name}_complete.csv: Contains all calculated distances between the target residue and every other residue for each frame.

{output_folder_name}_filtered.csv: Contains distances that fall within the specified range.

{output_folder_name}_summary.csv: Lists the residues within the specified distance range of the target residue for each frame.

New Feature: Handling PDB Files with >9999 Residues
Automatically adjusts residue numbering in PDB files where AMBER restarts numbering at 0 after reaching 9999 residues.

Ensures unique numbering by adding offsets of +10000 for each cycle of 9999 residues:

Example: Residue 0 becomes 10000, 1 becomes 10001, etc., in subsequent cycles.

This adjustment guarantees compatibility with large systems without errors in residue identification.



**11.5 molecule_counter.py**

Description:
This script automates the analysis of molecular dynamics data by counting occurrences of specified molecule codes in a CSV file containing residue information. It processes each frame of the input data and generates a summary CSV file with detailed counts and residue lists for the selected molecule codes.

Functionality:

Allows users to specify multiple molecule codes for analysis.

Validates user inputs interactively, including file names and molecule codes.

Reads residue data from an input CSV file and processes each frame.

Counts occurrences of specified molecule codes and extracts related residue details.

Generates an output CSV file with the following columns:

Frame number.

Molecule code.

Residues associated with the molecule code.

Count of occurrences for each molecule code.

Usage:

Run the script: python molecule_counter.py.

Provide the following inputs when prompted:

Input CSV file containing residue data (e.g., distances_summary.csv).

Molecule codes to analyze (e.g., WAT, ION).

The script will generate an output CSV file named {input_file_name}_{molecule_codes}_counts.csv.

Output:
The script generates a CSV file summarizing the analysis with detailed counts and residue lists for each selected molecule code.

Let me know if you need further adjustments!




**##MMPBGSA AUTOMATED CALCULATIONS**

Documentation for Automated MMPBSA Analysis Workflow
Introduction
This document describes an automated workflow for performing Molecular Mechanics Poisson-Boltzmann Surface Area (MMPBSA) analysis using a series of Python scripts. The goal is to facilitate performing MMPBSA calculations on multiple systems and processing the obtained results.

Workflow Overview
The general workflow consists of the following steps:

Preparation of the input CSV file.

Execution of the auto_multi_mmpbgsa.py script.

Collecting results with output_collector_mmpbgsa.py and converting to CSV format.

Calculation of weighted energies using mmpbgsa_weighted_energies_calculations.py.

Visualization and analysis of the results.

**1. Input CSV File (input_auto_multi_mmpbgsa.csv)**

This file is essential for the auto_multi_mmpbgsa.py script. It must have the following format, with a header line:

TO,FROM,START,END
i03_A+H2O,i01_C+H2O,0000,0500
i03_A+H2O,i03_A+H2O,0000,0600
i03_A+H2O,i07_A+H2O,0300,0800
i03_A+H2O,i09_A+H2O,0000,0400
i03_A+H2O,i11_A+H2O,0150,0900
i03_D+H2O,i01_A+H2O,0200,1500

TO: Destination folder where calculations will be performed.

FROM: Source folder of the necessary files for the calculation.

START: Initial frame for the MMPBSA calculation.

END: Final frame for the MMPBSA calculation.

Important: The script skips the first line of the CSV file, assuming it's a header.

**2. Script auto_multi_mmpbgsa.py**

This script automates the creation of folders, copying of files, and launching of MMPBSA calculations.

Main Functions:
crear_carpetas_y_copiar(csv_file, mmpbsa_script):

Reads the specified CSV file.

Creates a folder for each line in the CSV, named TO_{to_folder}_FROM_{from_folder}_{start_frame}_{end_frame}.

Copies the contents of the FROM folder to the new folder.

Copies the Each_Folder_General_Automated_MMPBSA_calculations.py script to the new folder.

Modifies the Each_Folder_General_Automated_MMPBSA_calculations.py script in the new folder to adjust the startframe and endframe parameters in the &general section of the MMPBSA input file.

Launches the Each_Folder_General_Automated_MMPBSA_calculations.py script using sbatch.

Usage:
Ensure that the Each_Folder_General_Automated_MMPBSA_calculations.py script and the CSV file are in the same directory.

Execute the script: python3 auto_multi_mmpbgsa.py.

Considerations:
Ensure that the MMPBSA_SCRIPT variable in the auto_multi_mmpbgsa.py script matches the name of the MMPBSA script to be executed.

This script uses sbatch to launch calculations, so it must be executed in an environment that supports this command (e.g., an HPC cluster).

The script assumes that the FROM folders are in the same directory where the script is executed.

**3. Script output_collector_mmpbgsa.py**

This script collects the results of the MMPBSA calculations from the folders generated by auto_multi_mmpbgsa.py.

Main Functions:
search_results_folders():

Searches for folders matching the pattern TO_*_FROM_*_NUM_NUM.

Within each folder, searches for MMPBSA_* subfolders.

Collects data from the FINAL_RESULTS_MMPBSA.dat file in each subfolder.

extract_energies(file_path):

Extracts the relevant energies from the FINAL_RESULTS_MMPBSA.dat file.

write_csv_header(results_file):

Writes the header of the output CSV file.

write_results(results_file, folder_name, energies):

Writes the results to the CSV file.

Usage:
Ensure that the output_collector_mmpbgsa.py script is in the same directory as the folders generated by auto_multi_mmpbgsa.py.

Execute the script: python3 output_collector_mmpbgsa.py.

Output Format:
The script generates a file named mmpbsa_results.csv. Important: This file is separated by spaces, not commas. Therefore, it's necessary to open it in Excel, separate the columns, and then save it as a true CSV file (comma-separated) using VIM, Force, or any other text editing tool.

**4. Script mmpbgsa_weighted_energies_calculations.py**

This script calculates the weighted energies from the mmpbsa_results.csv file generated in the previous step.

Main Functions:
calculate_weighted_energies(input_file):

Reads the mmpbsa_results.csv file.

Calculates the weighted energies (how they are weighted depends on the logic implemented in the script).

Writes the results to a file named analysis_results.csv or analysis_results.txt.

Usage:
Ensure that the mmpbgsa_weighted_energies_calculations.py script is in the same directory as the mmpbsa_results.csv file.

Execute the script: python3 mmpbgsa_weighted_energies_calculations.py.

Output Format:
The script generates a file named analysis_results.csv or analysis_results.txt containing the calculated weighted energies.

**5. Script each_folder_general_automated_mmpbgsa_calculations.py**

This script automates the MMPBSA process for a specific folder.

Important Variables:
complex_tleap_in_info: Defines the tleap script to prepare the complex.

receptor_tleap_in_info: Defines the tleap script to prepare the receptor.

ligand_tleap_in_info: Defines the tleap script to prepare the ligand.

mmpbsa_in_info: Defines the input script for MMPBSA.

Main Functions:
run_cpptraj(commands): Executes cpptraj with the provided commands.

process_folder(grandfather_folder): Processes the main folder, identifying ligand and receptor, creating subfolders, and executing cpptraj and MMPBSA.

process_subfolder(parent_folder, subfolder_name, pdb_file, tleap_info): Creates and processes subfolders for the complex, ligand, and receptor, executing tleap.

Usage:
Place the script in the folder containing the "bases" and "md1" folders.

Make sure to have the necessary .mol2, .frcmod, and .pdb files in the "bases" folder.

Execute the script: python3 each_folder_general_automated_mmpbgsa_calculations.py.

General Notes:
File extensions: Be aware of the file extensions, as the code might be dependent on them (.pdb, .frcmod...).

Absolute Paths: The Each_Folder_General_Automated_MMPBSA_calculations.py script uses absolute paths to execute MMPBSA.py and tleap. Make sure these paths are correct for your system. Specifically, check this line:


run_mmpbsa = "python3 /usr/local/amber/22/amber22/bin/MMPBSA.py -O -i mmpbsa.in -o FINAL_RESULTS_MMPBSA.dat -sp system_solvated.prmtop -cp kstripped_system_dry.prmtop -rp kstripped_receptor_dry.prmtop -lp ligand_dry.prmtop -y *.mdcrd"

Dependencies: Make sure you have all the necessary dependencies installed, such as AmberTools, cpptraj, and the Python modules os, shutil, subprocess, and csv.

Errors: Carefully review error messages to troubleshoot issues. Common errors are usually related to incorrect paths or missing files.

Cobramm profile: Every script is sourcing the cobramm profile. Make sure the path is correct.

Conclusion
This automated workflow simplifies performing MMPBSA analysis on multiple systems. By following these steps and paying attention to the additional considerations, you can obtain accurate results and efficiently analyze the interaction energies between ligands and receptors.








**##RE-PARAMETRIZATION SCRIPTS**




**1. reparametrizador_organizador.py**

This Python 3 script automates the workflow of force field parametrization and short molecular dynamics (MD) runs in AMBER for multiple ligand conformations stored as PDB files in the current directory. It organizes files, modifies input scripts dynamically, runs tleap and a follow-up MD script, and structures all outputs neatly per conformation.

Usage
Run the script in the directory containing your .pdb conformations:

python3 reparametrizador_organizador.py
Input requirements
PDB files: One or more .pdb files in the working directory, each representing a ligand conformation.

Parameter and topology files:

QCyMeBT3.frcmod (force field modifications file)

QCyMeBT3.mol2 (molecular topology)
These must be present in the parent directory (one level up from where the script runs).

tleap input file:
A base tleap input file at the path defined by ruta_reparametleap (e.g., /home/richard/Dinamica/scripts_dinamica/reparametleap.in). This template will be copied and modified to load each specific PDB.

Dynamics script:
A Python script with MD instructions located at the path defined by ruta_script_dinamica (e.g., /home/richard/Dinamica/scripts_dinamica/reparametrizacion_parmed_min_dinamica.py).

How it works
For each .pdb file in the working directory:

Directory setup:
Creates a separate folder named after the PDB filename (without extension).

File organization:
Moves the .pdb into its folder. Copies the .frcmod and .mol2 parameter files from the parent directory into that folder.

tleap input modification:
Copies the tleap input template (reparametleap.in) into the folder and edits the line containing "system= loadPDB" to load the current PDB filename.

Running tleap:
Executes the AMBER program tleap with the customized input, generating LEaP outputs (.prmtop, .inpcrd, etc.).

File sorting:
Moves the generated topology files (system.prmtop, system.inpcrd, system.pdb) to a bases/ subfolder. Moves other output or log files (except some key scripts and folders) to an otros_documentos/ subfolder.

Run MD script:
Copies the dynamics Python script into the folder and runs it to perform minimization or short MD runs on the system.

Returns to parent folder and continues with the next PDB.

Outputs
For each PDB conformation folder, you get:

A bases/ folder containing finalized AMBER files (.prmtop, .inpcrd, .pdb) ready for simulation.

An otros_documentos/ folder with logs, output files, and auxiliary documents.

Results of the MD run initiated by the dynamics Python script.

Organized structure facilitating batch parametrization and simulation.

Requirements
Python 3

AMBER 22 environment correctly set and accessible via modules (module load amber/22)

Availability of required input files in specified paths (.frcmod, .mol2, tleap input, dynamics script)

Unix/Linux system with bash shell

Notes
You must modify the paths inside the script (ruta_script_dinamica, ruta_reparametleap) to your file locations before running.

The script aborts if expected input files are missing.

The command source /etc/profile && module load amber/22 is used to load AMBER environment; adjust if your system differs.

The script assumes tleap is in your PATH once the module is loaded.

The Python dynamics script called inside (reparametrizacion_parmed_min_dinamica.py) should be set up for your minimization/dynamics protocol.




**2. reparametrizacion_parmed_min_dinamica.py**

Description:
This Python script automates a focused, minimal workflow tailored specifically for force field reparametrization protocols in AMBER. Its goal is to prepare the system via heavy-atom mass repartitioning (using Parmed), followed by a single energy minimization step through pmemd.cuda and SLURM job submission, with file organization and output conversion integrated.

This script is NOT intended for extended MD simulations like heating, NPT equilibration, or production runs, but strictly for the reparametrization preparatory process.

Input Requirements
system.prmtop and system.inpcrd files pre-generated in the ../bases/ directory.

AMBER environment properly configured with:

parmed

pmemd.cuda and associated utility scripts (launch_pmemd.cuda, mdcrd_to_dcd, rst_to_pdb).

SLURM job scheduler accessible (sbatch command).

Python 3 interpreter.

Workflow Summary
Heavy-atom mass repartitioning (parmed step):

Creates parmed/ directory.

Copies topology and coordinate files into parmed/.

Runs parmed commands to generate a modified topology file with redistributed hydrogen masses (system_hmass.prmtop).

Energy minimization (min/ step):

Creates min/ directory.

Copies system_hmass.prmtop and system.inpcrd from the parmed/ directory.

Writes a basic minimization input file with specified parameters targeting implicit solvent (igb=6) and zero steps (maxcyc=0) — you can edit this file for your specific needs.

Uses the external launch_pmemd.cuda tool to generate a SLURM submission script .sh.

Modifies the submission script to use the correct parameters for minimization.

Submits the minimization job to SLURM and waits until the .rst restart file is produced.

Converts .mdcrd trajectory to .dcd and restart to .pdb using auxiliary scripts for easy visualization and analysis.

Outputs Organized per Step
parmed/ → Contains output of the heavy-mass repartitioning step (system_hmass.prmtop).

min/ → Contains minimization input/output, restart files, MD trajectories in .dcd, and structure snapshot .pdb.

Notes
The minimization input is minimal and may need customization (e.g., number of cycles, cutoffs) depending on your system and goals.

This script assumes a controlled environment tailored for rapid parametrization cycles without full equilibration or production dynamics.

To extend beyond this minimal workflow, other scripts or adaptations (like your auto_md_amber.py) can be used, but they are outside the scope of this script.

Paths to auxiliary tools (launch_pmemd.cuda, mdcrd_to_dcd, rst_to_pdb) need to be in your PATH or adjusted accordingly.

SLURM is used for job control; ensure access and commands are appropriate for your cluster environment.







**3. Print_Information_min_out.py**


Description:
This script performs a shallow recursive search (depth = 1) from the base directory to find all .out files (typical Gaussian or similar output files) containing standard tables with headers including "NStep", "Energy", and "RMS". For each .out file, it locates the last occurrence of this table (by searching from the end of the file) and extracts the energy value from the line immediately following the header. It collects these energy values together with the relative path of the .out files and writes them into a CSV file named Search_Results.csv located in the base directory.

Input
Base directory where the script is executed (current working directory).

Folder structure up to depth 1 (only the immediate subdirectories of the base).

.out files inside those subdirectories.

The .out files must contain output tables with headers that include the keywords: NStep, Energy, and RMS.

How It Works
The script starts in the current directory (base_dir) and creates or overwrites the CSV file Search_Results.csv with the header: ["Archivo", "Valor ENERGY"] (File, Energy Value).

It recursively explores directories up to depth 1.

In each directory, it finds all files ending with .out.

For each .out file, it reads lines in reverse order searching for the table header containing "nstep", "energy", and "rms".

Upon finding the last such table, it extracts the energy value from the line following the header (second column).

It records in Search_Results.csv both the relative path of the .out file and the extracted energy.

In case of decoding errors or incomplete data, it marks an appropriate notice in the CSV and continues processing.

Output
A CSV file named Search_Results.csv generated in the base directory with two columns:

Archivo: relative path to the .out file

Valor ENERGY: extracted energy value from the last table found in the file

Usage
Run the script from the base directory:

python3 search_out_energy.py
The Search_Results.csv file will be created or updated automatically.

Notes
Only explores folder trees up to depth 1 (adjustable by modifying the depth_degree parameter in the script).

Expects .out files with output table headers typical of Gaussian energy or minimization steps.

Handles file encoding errors gracefully without stopping the overall search.

Very helpful for quickly extracting energy data from large sets of Gaussian or similar output files.
