#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Amber Simulation Quality Assurance (QA) Analyzer
================================================

This script parses Amber MD output files (.out) and trajectory files (.mdcrd/.nc)
to generate a comprehensive report on simulation stability and performance.

It includes:
1. Automated parsing of thermodynamic logs.
2. Structural analysis (RMSD/RoG) using cpptraj.
3. Generation of a single PDB snapshot (final frame) for each step.
4. Global plotting with cumulative time axis.

"""

import os
import re
import sys
import time
import glob
import subprocess
import pandas as pd
import numpy as np
import matplotlib

# Headless mode for cluster execution
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# --- 1. GLOBAL CONFIGURATION VARIABLES ---
# ==========================================

# Topology file used for cpptraj analysis
TOPOLOGY_FILE = "system_hmass.prmtop"

# ----------------------------------------
# MASKS FOR ANALYSIS (RMSD / RoG)
# ----------------------------------------
RMSD_MASK = ":1-1036"          # Residues to calculate RMSD on
ROG_MASK  = ":1-1036"          # Residues to calculate Radius of Gyration on

# ----------------------------------------
# MASKS FOR PDB GENERATION (Centering)
# ----------------------------------------
RESIDUES_FOR_CENTERING = ":1-1036" 

# ----------------------------------------
# DIRECTORIES & STEPS
# ----------------------------------------
REPORT_DIR = "QA_REPORT"
PLOTS_DIR = os.path.join(REPORT_DIR, "Plots")
PDB_DIR = os.path.join(REPORT_DIR, "PDB_Snapshots")

# Steps Order: The script uses this to stitch together the Global Plot correctly.
STEPS_ORDER = [
    "min_1_solvent", "min_2_8RT", "min_3_5RT", "min_4_2RT", "min_5_full",
    "heat_5RT",
    "npt_1_2RT", "npt_2_05RT", "npt_3_full",
    "md1", "md2", "md3", "md4", "md5", "md6", "md7", "md8", "md9", "md10"
]

# ==========================================
# --- END CONFIGURATION ---
# ==========================================


class AmberLogParser:
    """Parses Amber .out files for thermodynamic and performance data."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.is_min = 'min' in self.filename.lower()
        self.data = None
        self.performance = {
            'ns_per_day': 0.0,
            'time_elapsed': 0.0,
            'finished_normally': False
        }

    def parse(self):
        """Main parsing logic dispatcher."""
        if not os.path.exists(self.filepath):
            return None
        
        try:
            if self.is_min:
                self._parse_minimization()
            else:
                self._parse_dynamics()
            
            self._check_completion()
        except Exception as e:
            print(f"Error parsing {self.filename}: {e}")
            return None

        return self.data

    def _parse_minimization(self):
        """Parses minimization steps."""
        data_list = []
        # Regex handles scientific notation (e.g., 1.0E+02)
        re_min = re.compile(r"^\s*(\d+|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)")
        
        with open(self.filepath, 'r') as f:
            for line in f:
                if "Final Results" in line or "A V E R A G E S" in line:
                    break
                if "NSTEP" in line or "---" in line:
                    continue
                match = re_min.search(line)
                if match:
                    try:
                        data_list.append({
                            'Step': int(float(match.group(1))),
                            'Energy': float(match.group(2)),
                            'RMS_Force': float(match.group(3))
                        })
                    except ValueError:
                        continue
        self.data = pd.DataFrame(data_list)

    def _parse_dynamics(self):
        """Parses MD steps robustly."""
        data_list = []
        current_frame = {}
        float_re = r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"
        
        re_nstep = re.compile(rf"NSTEP\s*=\s*(\d+|{float_re})")
        re_time  = re.compile(rf"TIME\(PS\)\s*=\s*({float_re})")
        re_temp  = re.compile(rf"TEMP\(K\)\s*=\s*({float_re})")
        re_press = re.compile(rf"PRESS\s*=\s*({float_re})")
        re_etot  = re.compile(rf"Etot\s*=\s*({float_re})")
        re_eptot = re.compile(rf"EPtot\s*=\s*({float_re})")
        re_dens  = re.compile(rf"Density\s*=\s*({float_re})")
        re_perf  = re.compile(rf"ns/day\s*=\s*({float_re})")
        re_wall  = re.compile(rf"elapsed time\s*=\s*({float_re})")

        with open(self.filepath, 'r') as f:
            for line in f:
                # Stop if summary reached
                if "A V E R A G E S" in line or "RMS fluctuations" in line or "Final Results" in line or "Final Performance Info" in line:
                    break

                # New Block Detection
                if "NSTEP" in line:
                    if current_frame:
                        data_list.append(current_frame)
                    current_frame = {}
                    m_step = re_nstep.search(line)
                    m_time = re_time.search(line)
                    m_temp = re_temp.search(line)
                    if m_step: current_frame['Step'] = int(float(m_step.group(1)))
                    if m_time: current_frame['Time_ps'] = float(m_time.group(1))
                    if m_temp: current_frame['Temp'] = float(m_temp.group(1))
                
                # Parse data within block
                if current_frame or ("NSTEP" in line and current_frame):
                    m_press = re_press.search(line)
                    if m_press: current_frame['Press'] = float(m_press.group(1))
                    m_etot = re_etot.search(line)
                    if m_etot: current_frame['Etot'] = float(m_etot.group(1))
                    m_eptot = re_eptot.search(line)
                    if m_eptot: current_frame['EPtot'] = float(m_eptot.group(1))
                    m_dens = re_dens.search(line)
                    if m_dens: current_frame['Density'] = float(m_dens.group(1))

                # Performance info
                m_perf = re_perf.search(line)
                if m_perf: self.performance['ns_per_day'] = float(m_perf.group(1))
                m_wall = re_wall.search(line)
                if m_wall: self.performance['time_elapsed'] = float(m_wall.group(1))

            # Add last frame
            if current_frame and 'Step' in current_frame:
                data_list.append(current_frame)

        self.data = pd.DataFrame(data_list)

    def _check_completion(self):
        success_markers = ["Final Performance Info", "Job finished", "Run time", "Maximum number of minimization cycles reached", "Final Energy"]
        try:
            with open(self.filepath, 'rb') as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(size - 8192, 0))
                tail = f.read().decode('utf-8', errors='ignore')
                for marker in success_markers:
                    if marker in tail:
                        self.performance['finished_normally'] = True
                        break
        except (OSError, IOError):
            pass

class StructureAnalyzer:
    """Uses cpptraj to calculate RMSD, Radius of Gyration, and generate PDBs."""
    
    def __init__(self, step_name, topology_file, out_file_path):
        self.step_name = step_name
        self.prmtop = topology_file
        
        # Locate trajectory
        base_dir = os.path.dirname(out_file_path)
        possible_traj = [
            os.path.join(base_dir, f"{step_name}.mdcrd"),
            os.path.join(base_dir, f"{step_name}.nc"),
            os.path.join(base_dir, "mdcrd"),
            os.path.join(base_dir, "prod.nc")
        ]
        self.trajectory = None
        for p in possible_traj:
            if os.path.exists(p):
                self.trajectory = p
                break
        
        self.stats_file = os.path.join(base_dir, "cpptraj_stats.dat")
        self.pdb_file = os.path.join(PDB_DIR, f"{step_name}_final.pdb")

    def _read_cpptraj_dat(self, filepath, value_col_name):
        """Robustly reads a cpptraj data file with unknown column count."""
        try:
            # Read ignoring headers, assuming whitespace separation
            df = pd.read_csv(filepath, sep='\s+', header=None, comment='#')
            
            # Logic to identify columns
            # Standard "rms ... time 1.0 noheader" output: Frame | Time | RMSD
            # Standard "radgyr ... time 1.0 noheader" output: Frame | Time | RoG
            
            if df.shape[1] == 3:
                df.columns = ['Frame', 'Time_ps', value_col_name]
            elif df.shape[1] == 2:
                # If time was somehow missing
                df.columns = ['Frame', value_col_name]
                print(f"    [Warn] {value_col_name} file has only 2 cols (Missing time?).")
            else:
                return None
            return df
        except Exception:
            return None

    def run_analysis(self):
        """Generates RMSD/RoG data."""
        if not self.trajectory or not os.path.exists(self.prmtop):
            return None

        rms_file = self.stats_file.replace(".dat", "_rms.dat")
        rog_file = self.stats_file.replace(".dat", "_rog.dat")

        # REQUEST TIME for BOTH to ensure both have valid Time_ps columns
        cpptraj_in = f"""
parm {self.prmtop}
trajin {self.trajectory}
rms ToFirst {RMSD_MASK} first out {rms_file} time 1.0 noheader
radgyr RoG {ROG_MASK} out {rog_file} time 1.0 noheader nomax
run
"""
        script_name = f"temp_analysis_{self.step_name}.in"
        
        try:
            with open(script_name, 'w') as f:
                f.write(cpptraj_in)

            subprocess.run(['cpptraj', '-i', script_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, check=True)
            
            df_rms = None
            df_rog = None

            # 1. Read RMSD
            if os.path.exists(rms_file):
                df_rms = self._read_cpptraj_dat(rms_file, 'ToFirst')
                os.remove(rms_file)

            # 2. Read RoG
            if os.path.exists(rog_file):
                df_rog = self._read_cpptraj_dat(rog_file, 'RoG')
                os.remove(rog_file)

            # MERGE LOGIC
            df_final = None
            if df_rms is not None and df_rog is not None:
                # Merge on Frame and Time (if present)
                df_final = pd.merge(df_rms, df_rog[['Frame', 'RoG']], on='Frame', how='inner')
            elif df_rms is not None:
                df_final = df_rms
            elif df_rog is not None:
                df_final = df_rog

            # Clean up input script
            if os.path.exists(script_name): os.remove(script_name)
            
            return df_final

        except Exception as e:
            if os.path.exists(script_name): os.remove(script_name)
            return None

    def generate_pdb_snapshot(self):
        """Generates a centered PDB of the LAST frame."""
        if not self.trajectory or not os.path.exists(self.prmtop):
            return

        if not os.path.exists(PDB_DIR):
            os.makedirs(PDB_DIR)

        cpptraj_in = f"""
parm {self.prmtop}
trajin {self.trajectory} lastframe
autoimage anchor {RESIDUES_FOR_CENTERING}
trajout {self.pdb_file} pdb include_ep
run
"""
        script_name = f"temp_pdb_{self.step_name}.in"
        try:
            with open(script_name, 'w') as f:
                f.write(cpptraj_in)

            subprocess.run(['cpptraj', '-i', script_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            if os.path.exists(script_name): os.remove(script_name)
            
            if os.path.exists(self.pdb_file):
                return True
        except Exception:
            pass
        return False

class ReportGenerator:
    """Generates Plots and Text Reports."""
    
    def __init__(self):
        if not os.path.exists(PLOTS_DIR):
            os.makedirs(PLOTS_DIR)
        self.summary_lines = []
        self.summary_lines.append("| Step | Type | Status | NSTEP (Last) | Time (ps) | ns/day | Final Val |")
        self.summary_lines.append("|---|---|---|---|---|---|---|")

    def plot_minimization(self, df, step_name):
        if df is None or len(df) < 2: return
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        
        ax[0].plot(df['Step'], df['Energy'], color='blue', linewidth=1.5)
        ax[0].set_title(f'{step_name}: Potential Energy')
        ax[0].set_ylabel('Energy (kcal/mol)')
        ax[0].grid(True, alpha=0.3)

        ax[1].plot(df['Step'], df['RMS_Force'], color='red', linewidth=1.5)
        ax[1].set_title(f'{step_name}: RMS Force')
        ax[1].set_ylabel('Force (kcal/mol/Å)')
        ax[1].set_yscale('log')
        ax[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{step_name}_min.png"), dpi=100)
        plt.close()

    def plot_equilibration(self, df, step_name):
        if df is None or len(df) < 2: return
        
        has_density = 'Density' in df.columns
        has_press = 'Press' in df.columns
        
        rows = 2 
        if has_density: rows += 1
        if has_press: rows += 1
        
        fig, ax = plt.subplots(rows, 1, figsize=(8, 3.5*rows))
        if rows == 1: ax = [ax]
        
        # Temp
        ax[0].plot(df['Step'], df['Temp'], color='orange', label='Temp')
        ax[0].set_title(f'{step_name}: Temperature')
        ax[0].set_ylabel('T (K)')
        ax[0].grid(True, linestyle='--', alpha=0.6)
        
        # Energy
        if 'EPtot' in df.columns:
            ax[1].plot(df['Step'], df['EPtot'], color='blue', label='Pot. Energy')
            ax[1].set_title('Potential Energy')
            ax[1].set_ylabel('kcal/mol')
            ax[1].grid(True, linestyle='--', alpha=0.6)
        else:
            ax[1].text(0.5, 0.5, 'No EPtot Data', ha='center')

        idx = 2
        # Density
        if has_density:
            ax[idx].plot(df['Step'], df['Density'], color='green')
            ax[idx].set_title('Density')
            ax[idx].set_ylabel('g/cm³')
            ax[idx].grid(True, linestyle='--', alpha=0.6)
            idx += 1
        # Pressure
        if has_press:
            ax[idx].plot(df['Step'], df['Press'], color='purple', alpha=0.7)
            ax[idx].set_title('Pressure')
            ax[idx].set_ylabel('Bar')
            ax[idx].set_xlabel('Step (NSTEP)') 
            ax[idx].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{step_name}_thermo.png"), dpi=100)
        plt.close()

    def plot_production_global(self, full_df):
        if full_df.empty: return
        
        # Use Cumulative Time (Calculated in main) for X axis
        if 'Cum_Time_ns' in full_df.columns:
            x_data = full_df['Cum_Time_ns']
            x_label = 'Cumulative Time (ns)'
        else:
            x_data = full_df['Time_ps'] / 1000.0
            x_label = 'Time (ns) [Discontinuous]'

        fig, ax = plt.subplots(5, 1, figsize=(12, 18))
        
        # 1. RMSD
        if 'ToFirst' in full_df.columns:
            ax[0].plot(x_data, full_df['ToFirst'], 'k-', lw=1)
            ax[0].set_title('Global RMSD (vs Start)')
            ax[0].set_ylabel('RMSD (Å)')
            ax[0].grid(True)
        else:
            ax[0].text(0.5, 0.5, 'No RMSD Data Available', ha='center')
        
        # 2. RoG
        if 'RoG' in full_df.columns:
            ax[1].plot(x_data, full_df['RoG'], 'm-', lw=1)
            ax[1].set_title('Radius of Gyration')
            ax[1].set_ylabel('RoG (Å)')
            ax[1].grid(True)
        else:
            ax[1].text(0.5, 0.5, 'No RoG Data Available', ha='center')
        
        # 3. Potential Energy
        if 'EPtot' in full_df.columns:
            ax[2].plot(x_data, full_df['EPtot'], color='navy', lw=1)
            ax[2].set_title('Global Potential Energy')
            ax[2].set_ylabel('kcal/mol')
            ax[2].grid(True)

        # 4. Density
        if 'Density' in full_df.columns:
            ax[3].plot(x_data, full_df['Density'], 'g-', lw=1)
            ax[3].set_title('Density')
            ax[3].set_ylabel('g/cm³')
            ax[3].grid(True)

        # 5. Temperature
        if 'Temp' in full_df.columns:
            ax[4].plot(x_data, full_df['Temp'], color='orange', lw=0.5)
            ax[4].set_title('Temperature')
            ax[4].set_ylabel('K')
            ax[4].set_xlabel(x_label)
            ax[4].grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "GLOBAL_PRODUCTION_METRICS.png"), dpi=100)
        plt.close()

    def add_summary(self, text):
        self.summary_lines.append(text)

    def save_report(self):
        with open(os.path.join(REPORT_DIR, "Simulation_QA_Report.md"), "w") as f:
            f.write("# Molecular Dynamics QA Report\n\n")
            f.write(f"**Date:** {pd.Timestamp.now()}\n\n")
            f.write("## Execution Summary\n")
            f.write("\n".join(self.summary_lines))
        print(f"Report saved to {os.path.join(REPORT_DIR, 'Simulation_QA_Report.md')}")


# --- MAIN ---

def find_files_to_process():
    files_map = []
    
    for step in STEPS_ORDER:
        path = os.path.join(step, f"{step}.out")
        if os.path.exists(path):
            files_map.append((step, path))
            continue
        if os.path.exists(f"{step}.out"):
            files_map.append((step, f"{step}.out"))
            
    return files_map

def main():
    print("--- Starting Amber QA Analysis (Final Version) ---")
    
    report = ReportGenerator()
    global_md_thermo = []
    
    has_topology = os.path.exists(TOPOLOGY_FILE)
    if not has_topology:
        print(f"Warning: Topology '{TOPOLOGY_FILE}' not found. Skipping RMSD/RoG and PDBs.")

    files_to_process = find_files_to_process()
    if not files_to_process:
        print("ERROR: No suitable .out files found.")
        return

    print(f"Found {len(files_to_process)} files to process.")

    for step_name, out_file in files_to_process:
        print(f"Analyzing: {step_name} -> {out_file}")
        
        parser = AmberLogParser(out_file)
        df_thermo = parser.parse()
        
        if df_thermo is None or df_thermo.empty:
            report.add_summary(f"| {step_name} | - | NO DATA | - | - | - | - |")
            continue

        # Status Logic
        if parser.performance['finished_normally']:
            status = "COMPLETED"
        else:
            try:
                if time.time() - os.path.getmtime(out_file) < 3600:
                    status = "RUNNING"
                else:
                    status = "FAILED"
            except:
                status = "FAILED"

        rows = len(df_thermo)
        last_time = 0
        last_step = 0
        
        if not parser.is_min and 'Time_ps' in df_thermo.columns:
            last_time = df_thermo.iloc[-1]['Time_ps']
            last_step = df_thermo.iloc[-1]['Step']
            print(f"  -> Parsed {rows} frames. Sim Time: {last_time} ps. Status: {status}")
        else:
            if 'Step' in df_thermo.columns: last_step = df_thermo.iloc[-1]['Step']
            print(f"  -> Parsed {rows} frames. Status: {status}")

        df_struct = None
        if not parser.is_min and has_topology:
            struct_tool = StructureAnalyzer(step_name, TOPOLOGY_FILE, out_file)
            
            # PDB Generation
            pdb_ok = struct_tool.generate_pdb_snapshot()
            pdb_msg = "PDB Saved" if pdb_ok else "PDB Failed"
            
            # Struct Analysis
            df_struct = struct_tool.run_analysis()
            
            # Debug Output
            rms_count = len(df_struct) if df_struct is not None and 'ToFirst' in df_struct.columns else 0
            rog_count = len(df_struct) if df_struct is not None and 'RoG' in df_struct.columns else 0
            print(f"  -> Struct Stats: RMSD ({rms_count} frames), RoG ({rog_count} frames). {pdb_msg}")

        # Reporting
        if parser.is_min:
            report.plot_minimization(df_thermo, step_name)
            final_val = f"{df_thermo.iloc[-1]['Energy']:.1f}"
            report.add_summary(f"| {step_name} | MIN | {status} | {int(last_step)} | - | - | {final_val} kcal |")
        
        else:
            report.plot_equilibration(df_thermo, step_name)
            dens_val = f"{df_thermo.iloc[-1]['Density']:.4f}" if 'Density' in df_thermo.columns else "N/A"
            perf = f"{parser.performance['ns_per_day']:.1f}"
            report.add_summary(f"| {step_name} | MD | {status} | {int(last_step)} | {last_time:.1f} ps | {perf} | {dens_val} g/cm³ |")

            # Combine for Global Plot
            if df_struct is not None and 'Time_ps' in df_struct.columns:
                combined_step = pd.merge_asof(df_thermo.sort_values('Time_ps'), 
                                              df_struct.sort_values('Time_ps'), 
                                              on='Time_ps', 
                                              direction='nearest',
                                              tolerance=1.0) 
            else:
                combined_step = df_thermo

            combined_step['_step_name'] = step_name
            global_md_thermo.append(combined_step)

    # Global Plot Logic
    if global_md_thermo:
        print("Generating Global Production Plots...")
        full_df = pd.concat(global_md_thermo, ignore_index=True)
        
        # Cumulative Time Calculation
        cum_time = []
        current_offset = 0.0
        last_t = 0.0
        last_step_name = ""
        
        for index, row in full_df.iterrows():
            t = row['Time_ps']
            step = row['_step_name']
            
            # If step changes and time resets (goes backwards), add offset
            if step != last_step_name:
                if t < last_t:
                    current_offset += last_t
                last_step_name = step
            
            cum_time.append((t + current_offset) / 1000.0) # ns
            last_t = t

        full_df['Cum_Time_ns'] = cum_time
        report.plot_production_global(full_df)

    report.save_report()
    print("\n--- Analysis Complete. Check 'QA_REPORT' folder ---")

if __name__ == "__main__":
    main()