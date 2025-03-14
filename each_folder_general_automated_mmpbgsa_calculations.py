#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R....
import os
import shutil
import subprocess
import glob
import tempfile
import sys
import time

# Necessary variables
complex_tleap_in_info = """
source leaprc.DNA.OL15
addAtomTypes {
        { "cy"  "C" "sp2" }
        { "ci"  "C" "sp2" }
        { "ch"  "C" "sp2" }
        { "cx"  "C" "sp2" }
        { "cm"  "C" "sp2" }
        { "c1"  "C" "sp2" }
        { "cb"  "C" "sp2" }
        { "c2"  "C" "sp2" }
        { "c3"  "C" "sp2" }
        { "cs"  "C" "sp2" }
        { "cv"  "C" "sp2" }
        { "c"   "C" "sp2" }
        { "o"   "O" "sp2" }
        { "ss"  "S" "sp3" }
        { "na"  "N" "sp2" }
        { "cn"  "C" "sp3" }
        { "ha"  "H" "sp3" }
        { "hn"  "H" "sp3" }
}
BT3= loadmol2 QCyMeBT3.mol2
source leaprc.water.tip3p
loadamberparams frcmod.ionsjc_tip3p
loadAmberparams QCyMeBT3.frcmod
check BT3
saveoff BT3 BT3.lib
system= loadPDB i01_A+6JJ0K.pdb ############change name
set default PBradii mbondi2
charge system
savepdb system system_dry.pdb
saveamberparm system system_dry.prmtop system_dry.inpcrd
solvateOct system TIP3PBOX 12.0
charge system
addions system K+ 0    ## If the system has a + charge: addions system Cl- 0
savepdb system system_solvated.pdb
saveamberparm system system_solvated.prmtop system_solvated.inpcrd
quit
"""

receptor_tleap_in_info = """
source leaprc.DNA.OL15
source leaprc.water.tip3p
loadamberparams frcmod.ionsjc_tip3p
system= loadPDB receptor.pdb ############change name
set default PBradii mbondi2
charge system
savepdb system system_dry.pdb
saveamberparm system receptor_dry.prmtop system_dry.inpcrd
quit
"""

ligand_tleap_in_info = """
addAtomTypes {
        { "cy"  "C" "sp2" }
        { "ci"  "C" "sp2" }
        { "ch"  "C" "sp2" }
        { "cx"  "C" "sp2" }
        { "cm"  "C" "sp2" }
        { "c1"  "C" "sp2" }
        { "cb"  "C" "sp2" }
        { "c2"  "C" "sp2" }
        { "c3"  "C" "sp2" }
        { "cs"  "C" "sp2" }
        { "cv"  "C" "sp2" }
        { "c"   "C" "sp2" }
        { "o"   "O" "sp2" }
        { "ss"  "S" "sp3" }
        { "na"  "N" "sp2" }
        { "cn"  "C" "sp3" }
        { "ha"  "H" "sp3" }
        { "hn"  "H" "sp3" }
}
BT3= loadmol2 QCyMeBT3.mol2
loadAmberparams QCyMeBT3.frcmod
check BT3
saveoff BT3 BT3.lib
system= loadPDB ligand.pdb ############change name
set default PBradii mbondi2
charge system
savepdb system system_dry.pdb
saveamberparm system ligand_dry.prmtop system_dry.inpcrd
quit
"""

mmpbsa_in_info = """
Input file for running PB and GB
&general
   startframe=400, endframe=1400, interval=10, keep_files=2,
/
&gb
  igb=2, saltcon=0.145,
/
&pb
radiopt=0,  istrng=145,
/
"""

# Command to execute MMPBSA
run_mmpbsa = "python3 /usr/local/amber/22/amber22/bin/MMPBSA.py -O -i mmpbsa.in -o FINAL_RESULTS_MMPBSA.dat -sp system_solvated.prmtop -cp kstripped_system_dry.prmtop -rp kstripped_receptor_dry.prmtop -lp ligand_dry.prmtop -y *.mdcrd"

# Function to execute cpptraj
def run_cpptraj(commands):
    print("Current working directory:", os.getcwd())
    
    with tempfile.NamedTemporaryFile('w', delete=False, dir=os.getcwd()) as tmpfile:
        tmpfile.write(commands)
        tmpfile_name = tmpfile.name

    print(f"Executing cpptraj with the following commands:")
    print(commands)

    cpptraj_path = shutil.which('cpptraj')
    if cpptraj_path is None:
        print("Error: cpptraj not found in PATH")
        sys.exit(1)
    print("cpptraj path:", cpptraj_path)

    try:
        # Source the cobramm_profile before running cpptraj
        result = subprocess.run(source_command + f"{cpptraj_path} -i {tmpfile_name}", 
                                shell=True, check=True,
                                capture_output=True, text=True)
        print("cpptraj executed successfully")
        print("cpptraj output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing cpptraj: {e}")
        print("Error output:")
        print(e.stderr)
    finally:
        os.remove(tmpfile_name)

def process_folder(grandfather_folder):
    print(f"Processing folder: {grandfather_folder}")

    bases_folder = os.path.join(grandfather_folder, "bases")
    md1_folder = os.path.join(grandfather_folder, "md1")

    if not (os.path.exists(bases_folder) and os.path.exists(md1_folder)):
        print(f"Folder {grandfather_folder} not valid for analysis")
        return grandfather_folder
        
    # Identify ligand and receptor
    complex_name = None
    for file in os.listdir(bases_folder):
        if file.endswith(".pdb") and "+" in file:
            complex_name = file
            ligand_name, receptor_name = complex_name.split("+")[0], complex_name.split("+")[1].split(".")[0]
            break

    if not complex_name:
        print(f"No complex file found in {bases_folder}")
        return grandfather_folder

    # Process folders
    process_subfolder(bases_folder, "complex", complex_name, complex_tleap_in_info)
    process_subfolder(bases_folder, "ligand", f"{ligand_name}.pdb", ligand_tleap_in_info)
    process_subfolder(bases_folder, "receptor", f"{receptor_name}.pdb", receptor_tleap_in_info)

    # Create MMPBSA folder and process
    mmpbsa_folder = os.path.join(grandfather_folder, f"MMPBSA_{ligand_name}+{receptor_name}")
    os.makedirs(mmpbsa_folder, exist_ok=True)

    # Copy necessary files
    for subfolder in ['complex', 'ligand', 'receptor']:
        source_folder = os.path.join(bases_folder, subfolder)
        for file in glob.glob(os.path.join(source_folder, '*.prmtop')):
            shutil.copy(file, mmpbsa_folder)
            print(f"File copied: {file}")

    for file in glob.glob(os.path.join(md1_folder, '*.mdcrd')):
        shutil.copy(file, mmpbsa_folder)
        print(f"File copied: {file}")

    # Generate mmpbsa.in
    with open(os.path.join(mmpbsa_folder, "mmpbsa.in"), "w") as f:
        f.write(mmpbsa_in_info)

    print(f"Files in {mmpbsa_folder}:")
    print(os.listdir(mmpbsa_folder))
    
    # Execute cpptraj
    original_dir = os.getcwd()
    os.chdir(mmpbsa_folder)
    
    try:
        print("Files in the current folder before executing cpptraj:")
        print(os.listdir())
        # Process receptor_dry.prmtop
        cpptraj_commands = """parm receptor_dry.prmtop
parmstrip :K+
parmwrite out kstripped_receptor_dry.prmtop
quit
"""
        run_cpptraj(cpptraj_commands)
        # Process system_dry.prmtop
        cpptraj_commands = """parm system_dry.prmtop
parmstrip :K+
parmwrite out kstripped_system_dry.prmtop
quit
"""
        run_cpptraj(cpptraj_commands)

        print("Files in the current folder after executing cpptraj:")
        print(os.listdir())
    except Exception as e:
        print(f"Error executing cpptraj: {e}")
    finally:
        os.chdir(original_dir)

    # Launch MMPBSA calculations
    try:
        # Source the cobramm_profile before running MMPBSA
        source_command = "source /home/lorenzo/.cobramm_profile && "  # Added here
        subprocess.run(source_command + run_mmpbsa, shell=True, cwd=mmpbsa_folder, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing MMPBSA: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Command: {e.cmd}")
        print(f"Output: {e.output}")
        print(f"Stderr: {e.stderr}")

    return grandfather_folder

def process_subfolder(parent_folder, subfolder_name, pdb_file, tleap_info):
    subfolder = os.path.join(parent_folder, subfolder_name)
    os.makedirs(subfolder, exist_ok=True)

    # Copy necessary files
    for ext in [".mol2", ".frcmod", ".pdb"]:
        for file in os.listdir(parent_folder):
            if file.endswith(ext):
                shutil.copy(os.path.join(parent_folder, file), subfolder)

    # Generate and modify tleap.in
    tleap_file = f"{subfolder_name}_tleap.in"
    with open(os.path.join(subfolder, tleap_file), "w") as f:
        f.write(tleap_info)

    # Modify the system=loadPDB line
    with open(os.path.join(subfolder, tleap_file), "r") as f:
        lines = f.readlines()

    with open(os.path.join(subfolder, tleap_file), "w") as f:
        for line in lines:
            if line.startswith("system= loadPDB"):
                f.write(f"system= loadPDB {pdb_file}\n")
            else:
                f.write(line)

    # Execute tleap
    try:
        # Source the cobramm_profile before running tleap
        source_command = "source /home/lorenzo/.cobramm_profile && "  # Added here
        subprocess.run(source_command + f"tleap -f {tleap_file}", shell=True, cwd=subfolder, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing tleap in {subfolder}: {e}")

def main():
    # Source the cobramm_profile at the beginning of the script
    source_command = "source /home/lorenzo/.cobramm_profile"
    try:
        subprocess.run(source_command, shell=True, check=True)
        print(".cobramm_profile sourced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error sourcing .cobramm_profile: {e}")

    # Assume the script is executed directly in the "grandfather_folder"
    grandfather_folder = os.getcwd()
    process_folder(grandfather_folder)
    print(f"Processing of {grandfather_folder} completed")

if __name__ == "__main__":
    main()
