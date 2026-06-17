#!/usr/bin/env python3
"""
Intersector Counter

Utility to read multiple CSV files containing frame-by-frame
residue/atom information, validate their structure and consistency, and compute the
intersection of residues present across all files for each frame.
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pandas as pd

# Attempt to import readline for input tab completion
try:
    import readline
except ImportError:
    readline = None


def setup_readline() -> None:
    """Configures readline to support tab completion for file inputs."""
    if readline is not None:
        readline.parse_and_bind("tab: complete")


def prompt_for_csv_files() -> List[Path]:
    """
    Prompts the user to input CSV file paths iteratively.
    
    Returns:
        List[Path]: A list of validated Path objects.
    """
    csv_files: List[Path] = []
    print("Enter the CSV files to process (one per line).")
    print("Press Enter on an empty line or type 'done' to finish.")
    print("-" * 50)
    
    while True:
        prompt = f"CSV file #{len(csv_files) + 1}: "
        user_input = input(prompt).strip()
        
        if not user_input or user_input.lower() == "done":
            if not csv_files:
                print("Error: You must specify at least one CSV file.")
                continue
            break
            
        file_path = Path(user_input)
        if not file_path.exists():
            print(f"Error: File '{user_input}' does not exist. Please try again.")
            continue
        if not file_path.is_file():
            print(f"Error: '{user_input}' is not a file. Please try again.")
            continue
            
        csv_files.append(file_path)
        
    return csv_files


def obtain_different_residues(csv_file: Path) -> List[str]:
    """
    Extracts suffixes of columns starting with 'Residues_'.
    
    Args:
        csv_file: Path to the CSV file.
        
    Returns:
        List[str]: List of suffixes found.
    """
    try:
        df = pd.read_csv(csv_file, nrows=1)
    except Exception as e:
        print(f"Error reading header of '{csv_file}': {e}")
        sys.exit(1)
        
    different_residues = []
    for header in df.columns:
        if "Residues_" in header:
            # Split by the first occurrence of Residues_
            parts = header.split("Residues_", 1)
            if len(parts) > 1:
                different_residues.append(parts[1])
    return different_residues


def validate_residue_headers(csv_files: List[Path]) -> List[str]:
    """
    Validates that all CSV files have matching Residues_* headers.
    
    Args:
        csv_files: List of CSV file paths to check.
    """
    if not csv_files:
        return
        
    base_residues = obtain_different_residues(csv_files[0])
    print(f"\nResidues found in {csv_files[0].name}: {base_residues}")
    
    for csv_file in csv_files[1:]:
        current_residues = obtain_different_residues(csv_file)
        print(f"Residues found in {csv_file.name}: {current_residues}")
        if base_residues != current_residues:
            print(f"\nError: Residues column mismatch in '{csv_file.name}' compared to '{csv_files[0].name}'.")
            print("Please check the CSV files.")
            sys.exit(1)
            
    print("\nResidues match across all files, nice!")
    return base_residues


def extract_appearances(csv_file: Path) -> Dict[int, List[str]]:
    """
    Parses a CSV file to map each Frame to a list of residues.
    
    Args:
        csv_file: Path to the CSV file.
        
    Returns:
        Dict[int, List[str]]: Map of frame number to list of residues.
    """
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading '{csv_file}': {e}")
        sys.exit(1)
        
    residues_col = [col for col in df.columns if col.startswith("Residues_")]
    if not residues_col:
        print(f"Error: No column starting with 'Residues_' found in '{csv_file.name}'.")
        sys.exit(1)
        
    target_col = residues_col[0]
    data: Dict[int, List[str]] = defaultdict(list)
    
    for _, row in df.iterrows():
        frame = int(row["Frame"])
        residue_cell = row[target_col]
        if pd.notna(residue_cell):
            # Split and clean whitespace
            residues = [r.strip() for r in str(residue_cell).split(",") if r.strip()]
            data[frame].extend(residues)
        else:
            data[frame] = []
            
    return dict(data)


def compute_intersection(all_data: List[Dict[int, List[str]]]) -> Dict[int, Tuple[List[str], int]]:
    """
    Computes the intersection of residues present across all files for each frame.
    
    Args:
        all_data: List of dictionaries mapping frame to residues.
        
    Returns:
        Dict[int, Tuple[List[str], int]]: Map of frame to (intersection list, count).
    """
    if not all_data:
        return {}
        
    first_dict = all_data[0]
    other_dicts_sets: List[Dict[int, Set[str]]] = [
        {frame: set(residues) for frame, residues in d.items()}
        for d in all_data[1:]
    ]
    
    # Verify consistent frames across all datasets
    first_frames = set(first_dict.keys())
    for idx, d in enumerate(all_data[1:], start=2):
        if set(d.keys()) != first_frames:
            print(f"Error: Frame mismatch between file 1 and file {idx}.")
            print("Please ensure all input CSV files contain the exact same set of frames.")
            sys.exit(1)
            
    results: Dict[int, Tuple[List[str], int]] = {}
    
    for frame, residues in first_dict.items():
        intersected_residues = []
        for residue in residues:
            # Check presence in all other files
            in_all = True
            for other_dict_set in other_dicts_sets:
                if residue not in other_dict_set.get(frame, set()):
                    in_all = False
                    break
            if in_all:
                intersected_residues.append(residue)
                
        results[frame] = (intersected_residues, len(intersected_residues))
        
    return results


def save_results(results: Dict[int, Tuple[List[str], int]], base_residues: List[str], output_path: str = "intersector_counter_results.csv") -> None:
    """
    Formats and writes the final intersection results to a CSV file.
    
    Args:
        results: Dictionary containing the frame results.
        output_path: Path where the output CSV will be saved.
    """
    list_results = []
    for frame, (residues, counter) in sorted(results.items()):
        list_results.append([frame, residues, counter])
        
    df = pd.DataFrame(list_results, columns=["Frame", f"Residues_{base_residues[0]}", "Counter"])
    try:
        df.to_csv(output_path, index=False)
        print(f"\nResults successfully written to '{output_path}'")
    except Exception as e:
        print(f"Error writing to '{output_path}': {e}")
        sys.exit(1)


def main() -> None:
    """Main execution pipeline."""
    setup_readline()
    
    # 1. Prompt for files
    csv_files = prompt_for_csv_files()
    
    # 2. Validate residue columns match
    base_residues = validate_residue_headers(csv_files)
    
    # 3. Extract appearances
    all_data = [extract_appearances(f) for f in csv_files]
    
    # 4. Compute intersection
    results = compute_intersection(all_data)
    
    # 5. Save results
    save_results(results, base_residues)


if __name__ == "__main__":
    main()
