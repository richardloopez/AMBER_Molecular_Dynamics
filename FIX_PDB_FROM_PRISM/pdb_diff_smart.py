#!/usr/bin/env python3
import sys

# --- CONFIGURATION ---
# Synonym dictionary to normalize AMBER residue names back to standard PDB names.
# This prevents the script from flagging HIS->HIE as a "deleted" residue.
RESIDUE_SYNONYMS = {
    "HIE": "HIS", "HID": "HIS", "HIP": "HIS", 
    "ASH": "ASP", "GLH": "GLU", "LYN": "LYS",
    "CYX": "CYS", "CYM": "CYS",
    "WAT": "HOH", "K+": "K", "Cl-": "CL", "CL-": "CL", "NA+": "NA"
}

# Atomic masses (Da) for mass balance. 
# Now includes Ions as requested.
ATOMIC_MASSES = {
    'H': 1.008, 'C': 12.01, 'N': 14.01, 'O': 15.999, 
    'S': 32.06, 'P': 30.97, 
    'K': 39.10, 'CL': 35.45, 'NA': 22.99, 'MG': 24.30, 'ZN': 65.38
}

def get_element(atom_name):
    """Guess element symbol from atom name."""
    name = atom_name.strip().upper()
    if name.startswith("CL"): return "CL"
    if name.startswith("MG"): return "MG"
    if name.startswith("ZN"): return "ZN"
    if name.startswith("K"):  return "K"
    if name.startswith("P"):  return "P"
    if name.startswith("NA"): return "NA"
    
    first_char = name[0]
    if first_char.isdigit() and len(name) > 1:
        return name[1] 
    return first_char

def read_atoms(filename):
    """
    Returns two structures:
      1. A set of normalized atom identifiers: (ResNum, NormalizedResName, AtomName)
      2. A dictionary mapping (ResNum) -> OriginalResName (to track renaming)
    """
    atoms = set()
    residue_names = {}
    print(f"Reading {filename}...")
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith(("ATOM", "HETATM")):
                    try:
                        atom_name = line[12:16].strip()
                        res_name = line[17:20].strip()
                        res_seq = int(line[22:26])
                        
                        # Store original name for tracking
                        if res_seq not in residue_names:
                            residue_names[res_seq] = res_name

                        # NORMALIZE NAME
                        norm_name = RESIDUE_SYNONYMS.get(res_name, res_name)
                            
                        # Normalize K+ atom name
                        if atom_name == "K+" or atom_name == "K":
                            atom_name = "K" 
                        
                        identifier = (res_seq, norm_name, atom_name)
                        atoms.add(identifier)
                    except ValueError:
                        pass
    except FileNotFoundError:
        print(f"ERROR: File not found: {filename}")
        sys.exit(1)
    return atoms, residue_names

def calculate_weight_diff(atom_list):
    weight = 0.0
    for (res_num, res_name, atom_name) in atom_list:
        elem = get_element(atom_name)
        weight += ATOMIC_MASSES.get(elem, 0.0)
    return weight

# --- MAIN ---

if len(sys.argv) < 3:
    print("Usage: python pdb_diff_smart.py original.pdb final.pdb")
    sys.exit(1)

file_1 = sys.argv[1] 
file_2 = sys.argv[2] 

set1, names1 = read_atoms(file_1)
set2, names2 = read_atoms(file_2)

# Calculate pure atomic differences
lost_atoms = set1 - set2 
gained_atoms = set2 - set1  

# Initialize variables to avoid NameError if sets are empty
mass_lost = 0.0
mass_gained = 0.0

print("\n" + "="*70)
print(f"SMART COMPARISON REPORT (Normalized Names)")
print("="*70)

# 0. RENAMED RESIDUES REPORT
print(f"\n🔄 RENAMED RESIDUES")
renamed_count = 0
# Check residues that exist in both files but have different original names
common_res_nums = set(names1.keys()).intersection(set(names2.keys()))
for res_num in sorted(common_res_nums):
    n1 = names1[res_num]
    n2 = names2[res_num]
    if n1 != n2:
        print(f"   Residue {res_num}: {n1} -> {n2}")
        renamed_count += 1

if renamed_count == 0:
    print("   (No residues were renamed)")


# 1. LOST ATOMS REPORT
print(f"\n🔴 TRULY LOST ATOMS ({len(lost_atoms)})")
if len(lost_atoms) == 0:
    print("   None! All atoms from the original file are present in the final file.")
else:
    mass_lost = calculate_weight_diff(lost_atoms)
    affected_residues = {}
    for (rnum, rname, aname) in lost_atoms:
        key = f"{rname} {rnum}"
        if key not in affected_residues: affected_residues[key] = []
        affected_residues[key].append(aname)

    for key, atoms in sorted(affected_residues.items(), key=lambda x: int(x[0].split()[1])):
        if len(atoms) > 4:
            print(f"   {key}: Missing full side chain or residue ({len(atoms)} atoms)")
        else:
            print(f"   {key}: {', '.join(atoms)}")
    
    print(f"   > Total Mass Lost: -{mass_lost/1000:.3f} kDa")


# 2. GAINED ATOMS REPORT
print(f"\n🟢 NEW/GAINED ATOMS ({len(gained_atoms)})")
mass_gained = calculate_weight_diff(gained_atoms)

h_gained = 0
heavy_gained = 0

for (rnum, rname, aname) in gained_atoms:
    elem = get_element(aname)
    if elem == 'H': h_gained += 1
    else: heavy_gained += 1

print(f"   > New Hydrogens: {h_gained}")
print(f"   > New Heavy Atoms (Reconstruction/Ions): {heavy_gained}")

# Detail heavy atoms
if heavy_gained > 0:
    print("\n   [Detail of new heavy structures]")
    reconstructed = {}
    for (rnum, rname, aname) in gained_atoms:
        elem = get_element(aname)
        if elem != 'H':
            key = f"{rname} {rnum}"
            if key not in reconstructed: reconstructed[key] = []
            reconstructed[key].append(aname)
    
    for key, atoms in sorted(reconstructed.items(), key=lambda x: int(x[0].split()[1])):
         print(f"     {key}: + {', '.join(atoms)}")

print(f"\n   > Total Mass Gained: +{mass_gained/1000:.3f} kDa")

# 3. FINAL BALANCE
print("\n" + "="*70)
print("FINAL MASS BALANCE")
print(f"Net Mass Difference: { (mass_gained - mass_lost)/1000 :.3f} kDa")
print("="*70)
