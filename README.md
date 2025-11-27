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
 
 
 
 
 
 
 
 **3-4. -JOINED- 	traj_rmsd_csv_columns.py** 
 
 
 This Python script automates the process of calculating Root Mean Square Deviation (RMSD) for molecular dynamics trajectories using cpptraj, and then compiles the resulting .agr files into a single, organized CSV file.

It's designed to calculate the RMSD for three distinct components—Ligand, Receptor, and Ligand + Receptor—in a single run.

🚀 Features
Integrated Workflow: Combines the RMSD calculation (using cpptraj) and the data compilation into a CSV (based on the logic of rmsd_columns.py) into a single, cohesive script.

Multiple RMSD Calculations: Calculates and outputs separate RMSD values for:

Ligand

Receptor

Ligand + Receptor

File Path Autocompletion: Uses the readline and glob libraries to provide Tab-completion for file paths in the terminal, improving user experience.

Traceability: Generates a cpptraj_commands.in file containing the exact commands used, ensuring reproducibility.

CSV Output: Creates a final rmsd_columns.csv file where the RMSD data for the three components is presented in parallel columns for easy plotting and analysis.

Customizable Residues: Allows the user to specify the residue ranges for each component (Ligand, Receptor, Ligand+Receptor) via command-line input.

⚙️ Prerequisites
Python 3

cpptraj: This script relies on the cpptraj program being installed and accessible in your system's PATH.

🖥️ How to Run
Save the script (e.g., as full_rmsd_analysis.py).

Run it from your terminal:

Bash

python3 full_rmsd_analysis.py
Follow the prompts: You will be asked to enter the file paths for your topology and trajectory, and the residue selections for the Ligand, Receptor, and Ligand+Receptor. Use Tab for file path autocompletion!

Example Input Prompts:
Enter the topology file (*.prmtop): complex.prmtop
Enter the trajectory file (*.mdcrd or *.dcd): production.mdcrd
| LIGAND | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): 180-200
| RECEPTOR | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): 1-179
| LIGAND+RECEPTOR | Enter a range of residues (eg., 1-25), numbers separated by commas are also accepted (e.g., 1, 50, 75): 1-200
📄 Output Files
The script generates the following files:

ligand_rmsd.agr: RMSD data for the ligand.

receptor_rmsd.agr: RMSD data for the receptor.

ligandreceptor_rmsd.agr: RMSD data for the complex.

cpptraj_commands.in: A plain text file showing the exact cpptraj commands used.

rmsd_columns.csv: The final output file containing all three sets of RMSD data side-by-side, ready for plotting.
 
 
 
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



**12. multi_dihedral_analyzer.py**

This Python script automates the analysis of multiple dihedral angles from molecular dynamics trajectories using cpptraj. It is designed to be flexible and easily adaptable to molecules with different numbers of dihedrals and structural symmetry.

Key Features
Fully configurable dihedral definitions and classification ranges via the input section.

Supports any number of dihedrals and multiple symmetric "arms" or branches of a molecule by adjusting only the input variables.

Automates creation of cpptraj input files for all defined dihedrals.

Runs cpptraj to extract dihedral angle trajectories from molecular dynamics simulations.

Generates summary CSV files consolidating angles, classifies frames into conformational groups based on user-defined angular ranges, and outputs statistics on grouped conformations.

Modular and loop-based design ensures that only the input section needs to be modified for different systems, making it scalable and user-friendly.

The crucial all_dihedrals_ranges setup links each dihedral selection to its corresponding angular ranges and classification identifiers, which is central to the classification logic.

Usage
To analyze a different molecule with a different number of dihedrals or arms, modify the dihedral definitions and their corresponding range groupings in the input section. The program handles the rest automatically through nested loops and classification logic.



**13. dcd_conformation_splitter.py**

This Python script automates the splitting of molecular dynamics (MD) trajectories based on conformational cluster assignments derived from dihedral angle analysis. Using as input a parameter/topology file, an MD trajectory file (.dcd), and a CSV file detailing conformations classified by frame indices, the script generates and executes customized cpptraj input files to extract sub-trajectories corresponding to each conformation.

Main features
Parses a CSV file containing conformer classifications and their associated frame indices.

Creates a results directory and organizes all relevant files for traceability (script, parameter, trajectory, and CSV).

Generates cpptraj input files tailored for each conformation to extract specified frames from the full trajectory.

Executes cpptraj to produce individual trajectory files (.dcd) per conformation.

Validates the creation of input script files and output .dcd files, logging status messages for each processed conformation.

Provides comprehensive summary messages indicating success or any file creation errors, facilitating easy debugging and verification.

Usage context
The script is designed for researchers working in computational chemistry, structural biology, or molecular dynamics simulation analysis who need to dissect large trajectories into subsets organized by conformational states. This enables detailed structural or dynamical insight into particular molecular conformations.





**14. plane-angle-calc.py **

Plane Angle Calculator for Molecular Dynamics (cpptraj interface)

This Python tool automates the calculation of the angle between planes defined by three atoms each from two different residues in a biomolecular system, using cpptraj from the Amber suite. The user provides parameter and trajectory files (Amber .prmtop/.dcd/.mdcrd formats), specifies atom indices for two residues, and the script prepares a working directory, sets up all necessary cpptraj input commands, and extracts the desired geometric angle with named outputs.

Key Features:

Interactive prompts for parameter and trajectory file names, plus atom indices for two residue triplets.

Automated creation of a dedicated data directory and organized file copying for reproducibility.

Generates cpptraj input scripts dynamically for vector, cross product, and angle calculations.

Executes cpptraj and cleans up temporary files automatically.

Clearly logs the workflow and results for traceability.









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








**##MD PREPARATION SCRIPTS (BETA)**

**A. charges-antechamber-tleap.py**

Pipeline Automática para la Preparación de Dinámica Molecular (Gaussian/Amber)

Este script Python (charges-antechamber-tleap.py) automatiza la secuencia completa de pasos computacionales necesarios para preparar un ligando orgánico para simulaciones de Dinámica Molecular utilizando el software Amber (a través de TLEAP), integrando cálculos de Gaussian para la obtención de cargas RESP.

El flujo de trabajo gestiona automáticamente la copia de archivos entre directorios, la ejecución de programas externos (launch_g16, antechamber, parmchk2) y la modificación de scripts auxiliares mediante sustituciones dinámicas (similares a sed -i).

Flujo de Trabajo (Pipeline)

Preparación de Gaussian: Modifica el script ponedor_coordenadas_pdb_en_com.py para asegurar que el archivo de entrada de Gaussian (S1_II_1_E.com) sea generado correctamente a partir de la plantilla y las coordenadas del PDB.

Cálculo Gaussian: Lanza la simulación en segundo plano y espera la terminación normal del cálculo (S1_II_1_E.log).

Antechamber/Parmchk2: Utiliza el log de Gaussian para ejecutar Antechamber (generando S1_II_1_E.mol2 con cargas RESP) y Parmchk2 (generando S1_II_1_E.frcmod con parámetros faltantes).

Preparación de Dinámica (TLEAP):

Copia los archivos mol2 y frcmod generados a la carpeta archivos_dinamica/.

Modifica el script hacedor_final_pdb.py con las rutas finales.

Ejecuta hacedor_final_pdb.py para construir el PDB del complejo final (S1_II_1_E+HB1.pdb).

Genera el script TLEAP: Procesa la plantilla primigenio_leap.in para crear el archivo final tleap.in, sustituyendo las variables de ligando, archivos de parámetros y el PDB del complejo final.



**A/1 (charges): ponedor_coordenadas_pdb_en_com.py**


Ponedor de Coordenadas PDB en Archivo de Entrada Gaussian (.com)

Este script auxiliar tiene la función de fusionar la cabecera de un archivo de entrada de Gaussian (.com) con las coordenadas atómicas de un archivo PDB.

Funcionalidad clave:

Lee una plantilla de archivo Gaussian (nombre_com_base), buscando la línea de referencia que indica la carga y multiplicidad (ej: "0 1").

Lee un archivo PDB (nombre_pdb).

Filtra y extrae solo las coordenadas de las líneas ATOM o HETATM que pertenecen al residuo llamado "UNL" (unligand, sin nombre).

Escribe un nuevo archivo de entrada de Gaussian, tomando la cabecera de la plantilla e insertando las coordenadas filtradas.

Asegura la inclusión de una línea en blanco obligatoria al final del archivo, requerida para la correcta terminación de los archivos de entrada de Gaussian.



**A/2 (antechamber): Esta carpeta no necesita script, el proceso se hace en charges-antechamber-tleap.py**



**A/3 (archivos_dinamica): hacedor_final_pdb.py**

Combinador y Actualizador de PDBs (PDB Final para TLEAP)

Este script es crucial para la fase de Dinámica Molecular, ya que crea el archivo PDB del complejo final que TLEAP utilizará para la solvatación y el setup de la simulación.

Funcionalidad clave:

Extracción de Coordenadas: Lee el PDB del ligando (PDB_LIG), extrayendo las coordenadas de los átomos que tienen el nombre de residuo "UNL".

Extracción de Atomtypes: Lee el archivo MOL2 (MOL2_FILE), generado por Antechamber, para obtener los atomtypes Amber específicos para cada átomo del ligando.

Sustitución en el Receptor: Lee el PDB de referencia del complejo Receptor-Ligando (PDB_REF).

Reemplazo Inteligente: Busca los residuos de tipo "NOU" (Placeholder) en el PDB de referencia. Reemplaza estos residuos placeholder por los átomos del ligando, realizando simultáneamente tres cambios críticos:

Actualiza el nombre del residuo de "UNL" / "NOU" a la abreviatura final del ligando (ej: "S1X").

Actualiza el campo del Atomtype con los valores extraídos del archivo MOL2.

Asegura que las líneas TER asociadas al placeholder también se actualicen con la abreviatura final del ligando.

Generación de Salida: Escribe el complejo final (OUTPUT_PDB) listo para ser cargado por TLEAP.



--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**##AMBER MD AUTOMATION**
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Amber MD Automation for SLURM Clusters

## Overview

This repository contains a high-throughput, automated Python workflow for executing Molecular Dynamics (MD) simulations using the **Amber** software suite (`pmemd.cuda`) on **SLURM-managed High-Performance Computing (HPC) clusters**.

The script `ultimate_dynamics-CTC.py` orchestrates the entire simulation lifecycle—from minimization and heating to equilibration and production—handling job dependencies, error checking, and file management automatically. It is designed to be robust, ensuring that a simulation step only proceeds once the previous step has successfully completed and converged.

## Key Features

* **Automated Workflow:** Sequentially executes 19+ defined simulation steps without user intervention.
* **SLURM Integration:** Automatically generates submission scripts, submits jobs via `sbatch`, and monitors queue status.
* **Robust Error Handling:** Checks output files for specific termination flags (e.g., "TIMINGS") to ensure runs finished correctly before proceeding.
* **Gentle Equilibration Protocol:** Implements a step-wise release of positional restraints (from 25 kcal/mol·Å² down to unrestrained) to ensure system stability.
* **H-Mass Repartitioning:** Includes functional blocks for `ParmEd` integration to enable Hydrogen Mass Repartitioning (HMR) for larger time steps (requires uncommenting in `main()`).
* **Context:** Specifically configured for GPU nodes (CTC configuration), but easily adaptable to other SLURM partitions.

## Simulation Protocol

The workflow enforces a rigorous physical protocol to prepare the system:

1.  **Minimization (Steps 1-5):**
    * Gradual reduction of restraints on protein/nucleic acids (25 $\to$ 8 $\to$ 5 $\to$ 2 kcal/mol·Å²).
    * Final unrestrained minimization.
2.  **NVT Heating (Step 6):**
    * Linear heating from 0K to 310K with restraints (5 kcal/mol·Å²).
3.  **NPT Equilibration (Steps 7-9):**
    * Pressure equilibration while reducing restraints (2 $\to$ 0.5 $\to$ 0 kcal/mol·Å²).
4.  **Production (Steps 10-19+):**
    * Long-scale sampling in NPT ensemble.

## Prerequisites

* **Python 3.x**
* **AmberTools / Amber** (specifically `pmemd.cuda` for GPU acceleration)
* **SLURM Workload Manager**
* **(Optional) ParmEd** (if using H-mass repartitioning)

## Directory Structure

To run the script, your working directory must be organized as follows:

```text
.
├── ultimate_dynamics-CTC.py   # This script
├── system_hmass.prmtop        # (Optional) If skipping ParmEd step, place topology here
├── parmed_setup/              # Created automatically if HMR is run
└── bases/                     # Input directory
    ├── system.prmtop          # Original topology
    └── system.inpcrd          # Original coordinates
