# AMBER_Molecular_Dynamics
	-This repository is composed by different codes for better treatment of AMBER Molecular Dynamics Data:
	-Most of them use cpptraj tool to generate the output, but implementing a user-friendly interface, without missing parameters
	-In the attached .pdf a guide for each script is provided
	-total_hbond_interactions.py has special interest because it performs hbond between selected residues in each selected frame (told by the user), a functionality not implemented by cpptraj. It offers a .csv archive as output.

 Molecular Analysis Scripts Collec on 

0.	auto_md_amber
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
    





 
2.	select_pose 
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
 
 
 
 
 
 
 
 
 
 
 
2.	clustering 
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
 
 
 
 
3.	trajectory_to_rmsd 
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
 
 
 
 
 
 
 
 
 
 
 
 
 
 
4.	rmsd_columns 
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
 
 
 
 
 
 
 
 
 
 
 
 
 
 
5.	hbond_average 
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
 
 
 
 
 
 
 
 
 
 
 
 
 
6.	total_hbond_interac ons 
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
 
 
 
 
 
 
 
 
 
 
7.	watershell 
This script performs water shell analysis on a molecular dynamics trajectory using cpptraj.Func onality: 
•	Analyzes water molecule interac on within a specified residue range 
Usage: 
1.	Run the script 
2.	Provide the following inputs: 
•	Parameter file (*.prmtop) 
•	Trajectory file (*.dcd or *.mdcrd) 
•	Residue range to analyze 
Output: A file (watershell.out.dat) with water shell analysis results 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
8.	solva on_spheres_average 
This script calculates average solva on shell values based on data from a watershell.out.dat file.Func onality: 
•	Calculates average for first and second solva on shells 
Usage: 
1. Run the script (requires a pre-exis ng watershell.out.dat file) 
Output: A file (solva on_average.txt) with solva on shell averages 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
9.	lie 
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

