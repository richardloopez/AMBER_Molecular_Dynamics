#!/usr/bin/env python3
"""
Rotate all atomic coordinates in a PDB file around the X, Y and Z axes
by user-specified angles (in degrees), and write a new rotated PDB.

Usage:
    python rotate_pdb.py input.pdb output.pdb angX angY angZ

Where:
    angX, angY, angZ = rotation angles (degrees) around X, Y, Z axes.
"""

import sys
import math


def read_pdb(path):
    """
    Read a PDB file and extract all ATOM/HETATM lines and their coordinates.

    Returns
    -------
    lines : list of str
        All lines in the original PDB file.
    coords : list of (index, x, y, z)
        index : int
            Line index in `lines` where the atom appears.
        x, y, z : float
            Atomic coordinates read from columns 31–54 of the PDB line.
    """
    with open(path, "r") as f:
        lines = f.readlines()

    coords = []
    for i, line in enumerate(lines):
        # Standard PDB atom records start with "ATOM  " or "HETATM"
        if line.startswith(("ATOM  ", "HETATM")) and len(line) >= 54:
            try:
                # PDB coordinate columns (1-based): x: 31–38, y: 39–46, z: 47–54
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                # If parsing fails, skip this line
                continue
            coords.append((i, x, y, z))

    return lines, coords


def write_pdb(path, lines, rotated_coords):
    """
    Write a new PDB file with updated coordinates.

    Parameters
    ----------
    path : str
        Output PDB filename.
    lines : list of str
        Original PDB lines.
    rotated_coords : list of (index, x, y, z)
        New coordinates to write into the corresponding ATOM/HETATM lines.
    """
    out_lines = list(lines)

    for idx, x, y, z in rotated_coords:
        line = out_lines[idx]
        # Overwrite the coordinate fields (columns 31–54) using PDB formatting.
        # Keep everything else (atom name, residue, occupancy, etc.) unchanged.
        new_line = f"{line[:30]}{x:8.3f}{y:8.3f}{z:8.3f}{line[54:]}"
        out_lines[idx] = new_line

    with open(path, "w") as f:
        f.writelines(out_lines)


def rot_x(x, y, z, angle_deg):
    """
    Rotate a 3D point (x, y, z) around the X axis by angle_deg degrees.
    """
    angle = math.radians(angle_deg)
    ca = math.cos(angle)
    sa = math.sin(angle)

    # Rotation matrix around X:
    # [1   0    0]
    # [0  cos -sin]
    # [0  sin  cos]
    y2 = ca * y - sa * z
    z2 = sa * y + ca * z
    return x, y2, z2


def rot_y(x, y, z, angle_deg):
    """
    Rotate a 3D point (x, y, z) around the Y axis by angle_deg degrees.
    """
    angle = math.radians(angle_deg)
    ca = math.cos(angle)
    sa = math.sin(angle)

    # Rotation matrix around Y:
    # [ cos  0  sin]
    # [  0   1   0 ]
    # [-sin  0  cos]
    x2 = ca * x + sa * z
    z2 = -sa * x + ca * z
    return x2, y, z2


def rot_z(x, y, z, angle_deg):
    """
    Rotate a 3D point (x, y, z) around the Z axis by angle_deg degrees.
    """
    angle = math.radians(angle_deg)
    ca = math.cos(angle)
    sa = math.sin(angle)

    # Rotation matrix around Z:
    # [cos -sin  0]
    # [sin  cos  0]
    # [ 0    0   1]
    x2 = ca * x - sa * y
    y2 = sa * x + ca * y
    return x2, y2, z


def rotate_all_coords(coords, ang_x, ang_y, ang_z):
    """
    Apply consecutive rotations around X, then Y, then Z
    to all coordinates.

    Parameters
    ----------
    coords : list of (index, x, y, z)
        Original coordinates.
    ang_x, ang_y, ang_z : float
        Rotation angles in degrees around X, Y, Z.

    Returns
    -------
    rotated : list of (index, x, y, z)
        Rotated coordinates.
    """
    rotated = []
    for idx, x, y, z in coords:
        # Order of rotations: X -> Y -> Z.
        # If you want a different convention, change the order below.
        x1, y1, z1 = rot_x(x, y, z, ang_x)
        x2, y2, z2 = rot_y(x1, y1, z1, ang_y)
        x3, y3, z3 = rot_z(x2, y2, z2, ang_z)
        rotated.append((idx, x3, y3, z3))
    return rotated


def main():
    # Expect exactly 5 arguments: script, input, output, angX, angY, angZ
    if len(sys.argv) != 6:
        print("Usage: python rotate_pdb.py input.pdb output.pdb angX angY angZ")
        print("Angles in degrees, around X, Y, Z axes respectively.")
        sys.exit(1)

    input_pdb = sys.argv[1]
    output_pdb = sys.argv[2]
    ang_x = float(sys.argv[3])
    ang_y = float(sys.argv[4])
    ang_z = float(sys.argv[5])

    lines, coords = read_pdb(input_pdb)
    rotated_coords = rotate_all_coords(coords, ang_x, ang_y, ang_z)
    write_pdb(output_pdb, lines, rotated_coords)

    print(f"Rotated PDB written to {output_pdb}")


if __name__ == "__main__":
    main()

