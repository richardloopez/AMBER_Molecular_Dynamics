#!/usr/bin/env python3
import sys

# List of residues extracted from leap.log that caused "bond distance" errors.
# These side chains will be stripped so TLeap can reconstruct them with correct geometry.
bad_residues = [
    64, 67, 71, 72, 75, 81, 84, 170, 192, 501, 
    535, 537, 540, 541, 542, 607, 687, 688, 776, 
    842, 857, 866, 922, 926, 927, 972, 975
]

# Backbone atoms that must ALWAYS be kept.
# Everything else in the 'bad_residues' will be deleted.
backbone_atoms = ["N", "CA", "C", "O", "CB", "OXT"]

input_pdb = "5VHE-PRISM-1.pdb"        # Original file
output_pdb = "5VHE-PRISM-1_fixed.pdb"   # Cleaned output file

print(f"Processing {input_pdb}...")

with open(input_pdb, 'r') as f_in, open(output_pdb, 'w') as f_out:
    for line in f_in:
        # Only process lines starting with ATOM (Protein).
        # HETATM lines (like DNA or Ions) are ignored by this check 
        # and written directly to the output, preserving them.
        if line.startswith("ATOM"):
            try:
                # Extract residue number (columns 22-26 in standard PDB format)
                res_num = int(line[22:26].strip())
                atom_name = line[12:16].strip()
                
                # If the residue is in the bad_residues list...
                if res_num in bad_residues:
                    # ...and it is NOT a backbone atom -> SKIP IT (Delete)
                    if atom_name not in backbone_atoms:
                        continue
            except ValueError:
                pass # Ignore malformed lines
        
        # Write the line (if it wasn't skipped)
        f_out.write(line)

print(f"Done! File saved as: {output_pdb}")
print("Now use this new PDB in your TLeap script.")
