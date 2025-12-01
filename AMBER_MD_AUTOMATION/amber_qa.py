#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Amber Simulation Quality Assurance (QA) Analyzer - v5
=====================================================

Professional QA tool for Amber MD simulations.

Updates in v5:
- Explicit separation of Complex, Receptor, and Ligand analysis.
- Robust warnings if Ligand/Receptor masks are invalid or empty.
- Improved global plotting with distinct colors for each component.

"""

import os
import re
import sys
import time
import shutil
import subprocess
import pandas as pd
import numpy as np
import matplotlib

# Headless mode for cluster execution
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# --- CONFIGURATION SECTION (EDIT THIS) ---
# ==========================================

# 1. FILES
TOPOLOGY_FILE = "system_hmass.prmtop"

# 2. ANALYSIS MASKS (CRITICAL: UPDATE THESE FOR YOUR SYSTEM!)
# These masks determine what is analyzed.
# Example: ":1-300" (Residues 1 to 300), ":LIG" (Residue name LIG)
COMPLEX_MASK  = ":1-1036"   # The whole system (Protein + Ligand)
RECEPTOR_MASK = ":1-1010"   # Protein only
LIGAND_MASK   = ":1011-1036"     # Ligand only (CHANGE THIS IF YOUR LIGAND IS DIFFERENT)

# Mask used for DCD generation (centering and imaging)
DCD_ANCHOR_MASK = COMPLEX_MASK     
RESIDUES_FOR_CENTERING = COMPLEX_MASK   

# 3. DIRECTORIES
REPORT_DIR = "QA_REPORT"
PLOTS_DIR = os.path.join(REPORT_DIR, "Plots")
PDB_DIR = os.path.join(REPORT_DIR, "PDB_Snapshots")
PROD_DCD_DIR = "PROD_DCD"

# 4. SIMULATION STEPS ORDER
STEPS_ORDER = [
    "STEP_01_MIN_RESTRAINT_25KCAL",
    "STEP_02_MIN_RESTRAINT_8KCAL",
    "STEP_03_MIN_RESTRAINT_5KCAL",
    "STEP_04_MIN_RESTRAINT_2KCAL",
    "STEP_05_MIN_UNRESTRAINED",
    "STEP_06_NVT_RESTRAINT_5KCAL",
    "STEP_07_NPT_RESTRAINT_2KCAL",
    "STEP_08_NPT_RESTRAINT_05KCAL",
    "STEP_09_NPT_UNRESTRAINED",
    "STEP_10_PROD",
    "STEP_11_PROD",
    "STEP_12_PROD",
    "STEP_13_PROD",
    "STEP_14_PROD",
    "STEP_15_PROD",
    "STEP_16_PROD",
    "STEP_17_PROD",
    "STEP_18_PROD",
    "STEP_19_PROD"
]

def is_prod_step(step_name):
    """Determines if a step is a production step based on naming convention."""
    return "PROD" in step_name

# ==========================================
# --- END CONFIGURATION ---
# ==========================================


class AmberLogParser:
    """Parses Amber .out files for thermodynamic data and timing info."""
    
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
        if not os.path.exists(self.filepath):
            return None
        
        try:
            if self.is_min:
                self._parse_minimization()
            else:
                self._parse_dynamics()
            self._check_completion()
        except Exception:
            return None

        return self.data

    def _parse_minimization(self):
        data_list = []
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
                            'Step': float(match.group(1)),
                            'Energy': float(match.group(2)),
                            'RMS_Force': float(match.group(3))
                        })
                    except ValueError:
                        continue
        
        self.data = pd.DataFrame(data_list)
        if not self.data.empty and 'Step' in self.data.columns:
            # Cast step to int if safe
            if (self.data['Step'] % 1 == 0).all():
                 self.data['Step'] = self.data['Step'].astype(int)

    def _parse_dynamics(self):
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

        perf_found = False

        with open(self.filepath, 'r') as f:
            for line in f:
                m_perf = re_perf.search(line)
                if m_perf: 
                    self.performance['ns_per_day'] = float(m_perf.group(1))
                    perf_found = True
                m_wall = re_wall.search(line)
                if m_wall: self.performance['time_elapsed'] = float(m_wall.group(1))

                if "A V E R A G E S" in line or "RMS fluctuations" in line or "Final Results" in line or ("Final Performance Info" in line and perf_found):
                    break

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
                
                if current_frame or ("NSTEP" in line and current_frame):
                    m_press = re_press.search(line)
                    if m_press: current_frame['Press'] = float(m_press.group(1))
                    m_etot = re_etot.search(line)
                    if m_etot: current_frame['Etot'] = float(m_etot.group(1))
                    m_eptot = re_eptot.search(line)
                    if m_eptot: current_frame['EPtot'] = float(m_eptot.group(1))
                    m_dens = re_dens.search(line)
                    if m_dens: current_frame['Density'] = float(m_dens.group(1))

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
    """Handles cpptraj analysis for RMSD, RoG, DCD generation, and PDB snapshots."""
    
    def __init__(self, step_name, topology_file, out_file_path):
        self.step_name = step_name
        self.prmtop = topology_file
        
        # Smart trajectory finder
        base_dir = os.path.dirname(out_file_path)
        possible_traj = [
            os.path.join(base_dir, f"{step_name}.mdcrd"),
            os.path.join(base_dir, f"{step_name}.nc"),
            os.path.join(base_dir, "mdcrd"), 
            os.path.join(base_dir, "prod.nc"),
            f"{step_name}.mdcrd", 
            f"{step_name}.nc"
        ]
        self.trajectory = None
        for p in possible_traj:
            if os.path.exists(p):
                self.trajectory = p
                break
        
        self.pdb_file = os.path.join(PDB_DIR, f"{step_name}_final.pdb")

    def _read_cpptraj_dat(self, filepath, col_names):
        try:
            df = pd.read_csv(filepath, sep='\s+', header=None, comment='#', skipinitialspace=True)
            # Handle cases where Time column might be missing
            if df.shape[1] == len(col_names) + 1:
                df.columns = ['Frame'] + col_names
            elif df.shape[1] == len(col_names) + 2:
                df.columns = ['Frame', 'Time_Cpptraj'] + col_names
            else:
                return None
            return df
        except Exception:
            return None

    def run_analysis(self):
        """Calculates RMSD and RoG for Complex, Receptor, and Ligand."""
        if not self.trajectory or not os.path.exists(self.prmtop):
            return None

        # Output filenames
        f_rms_complex = os.path.join(REPORT_DIR, f"{self.step_name}_rms_complex.dat")
        f_rms_rec     = os.path.join(REPORT_DIR, f"{self.step_name}_rms_rec.dat")
        f_rms_lig     = os.path.join(REPORT_DIR, f"{self.step_name}_rms_lig.dat")
        
        f_rog_complex = os.path.join(REPORT_DIR, f"{self.step_name}_rog_complex.dat")
        f_rog_rec     = os.path.join(REPORT_DIR, f"{self.step_name}_rog_rec.dat")
        f_rog_lig     = os.path.join(REPORT_DIR, f"{self.step_name}_rog_lig.dat")

        # Cpptraj script
        cpptraj_in = f"""
parm {self.prmtop}
trajin {self.trajectory}
rms RmsdComplex {COMPLEX_MASK} first out {f_rms_complex} time 1.0 noheader
rms RmsdRec {RECEPTOR_MASK} first out {f_rms_rec} time 1.0 noheader
rms RmsdLig {LIGAND_MASK} first out {f_rms_lig} time 1.0 noheader

radgyr RogComplex {COMPLEX_MASK} out {f_rog_complex} time 1.0 noheader nomax
radgyr RogRec {RECEPTOR_MASK} out {f_rog_rec} time 1.0 noheader nomax
radgyr RogLig {LIGAND_MASK} out {f_rog_lig} time 1.0 noheader nomax
run
"""
        script_name = f"temp_analysis_{self.step_name}.in"
        
        try:
            with open(script_name, 'w') as f:
                f.write(cpptraj_in)

            subprocess.run(['cpptraj', '-i', script_name], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Read and merge data
            df_main = None
            
            # Helper to read and merge
            def load_and_merge(fname, col_name, main_df):
                if not os.path.exists(fname): 
                    # Warning if file missing for expected outputs
                    print(f"    [Warn] Missing output: {os.path.basename(fname)} (Check Masks)")
                    return main_df
                    
                temp_df = self._read_cpptraj_dat(fname, [col_name])
                os.remove(fname)
                if temp_df is None or temp_df.empty: 
                    return main_df
                
                if main_df is None:
                    return temp_df
                else:
                    return pd.merge(main_df, temp_df[['Frame', col_name]], on='Frame', how='inner')

            df_main = load_and_merge(f_rms_complex, 'RMSD_Complex', df_main)
            df_main = load_and_merge(f_rms_rec, 'RMSD_Rec', df_main)
            df_main = load_and_merge(f_rms_lig, 'RMSD_Lig', df_main)
            df_main = load_and_merge(f_rog_complex, 'RoG_Complex', df_main)
            df_main = load_and_merge(f_rog_rec, 'RoG_Rec', df_main)
            df_main = load_and_merge(f_rog_lig, 'RoG_Lig', df_main)

            if os.path.exists(script_name): os.remove(script_name)
            return df_main

        except Exception:
            # Cleanup on fail
            for f in [script_name, f_rms_complex, f_rms_rec, f_rms_lig, 
                      f_rog_complex, f_rog_rec, f_rog_lig]:
                if os.path.exists(f): os.remove(f)
            return None

    def generate_pdb_snapshot(self):
        if not self.trajectory or not os.path.exists(self.prmtop):
            return False

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
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            if os.path.exists(script_name): os.remove(script_name)
            return os.path.exists(self.pdb_file)
        except Exception:
            if os.path.exists(script_name): os.remove(script_name)
            return False

    def generate_dcd(self):
        if not self.trajectory or not os.path.exists(self.prmtop):
            return None
        
        base_name = os.path.splitext(os.path.basename(self.trajectory))[0]
        out_dcd_path = os.path.join(os.path.dirname(self.trajectory), f"{base_name}.dcd")

        cpptraj_in = f"""
parm {self.prmtop}
trajin {self.trajectory}
autoimage anchor {DCD_ANCHOR_MASK}
trajout {out_dcd_path} dcd
run
quit
"""
        script_name = f"temp_dcd_{self.step_name}.in"
        
        try:
            with open(script_name, 'w') as f:
                f.write(cpptraj_in)

            print(f"    ... Generating DCD: {os.path.basename(out_dcd_path)}")
            subprocess.run(['cpptraj', '-i', script_name], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            if os.path.exists(script_name): os.remove(script_name)
            return out_dcd_path if os.path.exists(out_dcd_path) else None
        except Exception:
            if os.path.exists(script_name): os.remove(script_name)
            return None


class ReportGenerator:
    """Generates visualization and markdown reports."""
    
    def __init__(self):
        if not os.path.exists(PLOTS_DIR): os.makedirs(PLOTS_DIR)
        if not os.path.exists(REPORT_DIR): os.makedirs(REPORT_DIR)
        self.summary_lines = []
        self.summary_lines.append("| Step | Type | Status | Frames (Log) | Duration (ps) | ns/day | Final Val |")
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
        rows = 2 + (1 if has_density else 0) + (1 if has_press else 0)
        
        fig, ax = plt.subplots(rows, 1, figsize=(8, 3.5*rows))
        if rows == 1: ax = [ax]
        
        ax[0].plot(df['Step'], df['Temp'], color='orange')
        ax[0].set_title(f'{step_name}: Temperature')
        ax[0].set_ylabel('T (K)')
        ax[0].grid(True, linestyle='--', alpha=0.6)
        
        ax[1].plot(df['Step'], df['EPtot'], color='blue')
        ax[1].set_title('Potential Energy')
        ax[1].set_ylabel('kcal/mol')
        ax[1].grid(True, linestyle='--', alpha=0.6)

        idx = 2
        if has_density:
            ax[idx].plot(df['Step'], df['Density'], color='green')
            ax[idx].set_title('Density')
            ax[idx].set_ylabel('g/cm³')
            ax[idx].grid(True, linestyle='--', alpha=0.6)
            idx += 1
        if has_press:
            ax[idx].plot(df['Step'], df['Press'], color='purple')
            ax[idx].set_title('Pressure')
            ax[idx].set_ylabel('Bar')
            ax[idx].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{step_name}_thermo.png"), dpi=100)
        plt.close()

    def plot_production_global(self, df_thermo, df_struct):
        """
        Plots global metrics.
        Crucially, it plots Thermo and Struct data on independent axes/timeframes
        to prevent 'cutting' caused by frequency mismatches.
        """
        if df_thermo.empty: return
        
        # Determine X axis for Thermo
        x_thermo = df_thermo['Cum_Time_ns']
        
        # Prepare Plot
        fig, ax = plt.subplots(5, 1, figsize=(14, 20))
        
        # 1. RMSD (Complex, Receptor, Ligand)
        if not df_struct.empty and 'Cum_Time_ns' in df_struct.columns:
            x_struct = df_struct['Cum_Time_ns']
            if 'RMSD_Complex' in df_struct.columns:
                ax[0].plot(x_struct, df_struct['RMSD_Complex'], 'k-', lw=0.8, label='Complex')
            if 'RMSD_Rec' in df_struct.columns:
                ax[0].plot(x_struct, df_struct['RMSD_Rec'], 'b-', lw=0.8, alpha=0.7, label='Receptor')
            if 'RMSD_Lig' in df_struct.columns:
                ax[0].plot(x_struct, df_struct['RMSD_Lig'], 'r-', lw=0.8, alpha=0.7, label='Ligand')
            else:
                print("    [Warn] 'RMSD_Lig' not found in data. Skipping Ligand plot.")
            
            ax[0].set_ylabel('RMSD (Å)')
            ax[0].legend(loc='upper left')
        else:
            ax[0].text(0.5, 0.5, 'No Structural Data', ha='center')
        ax[0].set_title('Global RMSD')
        ax[0].grid(True)
        
        # 2. RoG (Complex, Receptor, Ligand)
        if not df_struct.empty and 'Cum_Time_ns' in df_struct.columns:
            x_struct = df_struct['Cum_Time_ns']
            if 'RoG_Complex' in df_struct.columns:
                ax[1].plot(x_struct, df_struct['RoG_Complex'], 'm-', lw=0.8, label='Complex')
            if 'RoG_Rec' in df_struct.columns:
                ax[1].plot(x_struct, df_struct['RoG_Rec'], 'b--', lw=0.8, alpha=0.6, label='Receptor')
            if 'RoG_Lig' in df_struct.columns:
                ax[1].plot(x_struct, df_struct['RoG_Lig'], 'r--', lw=0.8, alpha=0.6, label='Ligand')
            
            ax[1].set_ylabel('RoG (Å)')
            ax[1].legend(loc='upper left')
        else:
            ax[1].text(0.5, 0.5, 'No RoG Data', ha='center')
        ax[1].set_title('Radius of Gyration')
        ax[1].grid(True)
        
        # 3. Potential Energy
        if 'EPtot' in df_thermo.columns:
            ax[2].plot(x_thermo, df_thermo['EPtot'], color='navy', lw=1)
            ax[2].set_ylabel('kcal/mol')
        ax[2].set_title('Global Potential Energy')
        ax[2].grid(True)

        # 4. Density
        if 'Density' in df_thermo.columns:
            ax[3].plot(x_thermo, df_thermo['Density'], 'g-', lw=1)
            ax[3].set_ylabel('g/cm³')
        ax[3].set_title('Density')
        ax[3].grid(True)

        # 5. Temperature
        if 'Temp' in df_thermo.columns:
            ax[4].plot(x_thermo, df_thermo['Temp'], color='orange', lw=0.5)
            ax[4].set_ylabel('K')
            ax[4].set_xlabel('Cumulative Time (ns)')
        ax[4].set_title('Temperature')
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

def merge_dcd_files(dcd_list):
    """Merges collected DCD files into a single trajectory."""
    if not dcd_list: return
    
    if not os.path.exists(PROD_DCD_DIR):
        os.makedirs(PROD_DCD_DIR)

    output_merged = os.path.join(PROD_DCD_DIR, "merged_production.dcd")
    print(f"\n--- Merging {len(dcd_list)} DCD files into {output_merged} ---")

    script_lines = [f"parm {TOPOLOGY_FILE}"]
    for dcd in dcd_list:
        script_lines.append(f"trajin {dcd}")
    
    script_lines.append(f"trajout {output_merged} dcd")
    script_lines.append("run")
    script_lines.append("quit")
    
    script_name = "temp_merge_dcd.in"
    try:
        with open(script_name, 'w') as f:
            f.write("\n".join(script_lines))
        
        subprocess.run(['cpptraj', '-i', script_name], check=True)
        print("    -> Merge successful.")
        if os.path.exists(script_name): os.remove(script_name)
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] Merging failed: {e}")

# --- MAIN EXECUTION ---

def find_files_to_process():
    files_map = []
    for step in STEPS_ORDER:
        path = os.path.join(step, f"{step}.out")
        if os.path.exists(path):
            files_map.append((step, path))
            continue
        if os.path.exists(f"{step}.out"):
            files_map.append((step, f"{step}.out"))
            continue
        if os.path.exists(f"{step}.log"):
            files_map.append((step, f"{step}.log"))
            continue
    return files_map

def main():
    print("--- Starting Amber QA Analysis (Professional Edition v5) ---")
    
    report = ReportGenerator()
    
    # Collections for Global Plot
    global_thermo_list = []
    global_struct_list = []
    
    # Tracking cumulative time offset
    cumulative_offset_thermo = 0.0
    cumulative_offset_struct = 0.0 # Track structure time separately
    
    generated_dcd_paths = []
    
    has_topology = os.path.exists(TOPOLOGY_FILE)
    if not has_topology:
        print(f"Warning: Topology '{TOPOLOGY_FILE}' not found. Skipping structural analysis.")

    files_to_process = find_files_to_process()
    if not files_to_process:
        print("ERROR: No suitable .out files found.")
        return

    print(f"Found {len(files_to_process)} files to process.")

    for step_name, out_file in files_to_process:
        print(f"Analyzing: {step_name}")
        
        # 1. Parse Thermo Data
        parser = AmberLogParser(out_file)
        df_thermo = parser.parse()
        
        if df_thermo is None or df_thermo.empty:
            report.add_summary(f"| {step_name} | - | NO DATA | - | - | - | - |")
            continue

        # Check status
        if parser.performance['finished_normally']:
            status = "COMPLETED"
        elif time.time() - os.path.getmtime(out_file) < 600:
            status = "RUNNING"
        else:
            status = "FAILED/STOPPED"

        # Thermo Stats
        rows = len(df_thermo)
        last_time = 0.0
        if not parser.is_min and 'Time_ps' in df_thermo.columns:
            last_time = df_thermo['Time_ps'].iloc[-1]
            step_duration = df_thermo['Time_ps'].iloc[-1] - df_thermo['Time_ps'].iloc[0]
            if step_duration < 0: step_duration = df_thermo['Time_ps'].iloc[-1]
        else:
             step_duration = 0.0

        # 2. Structural Analysis
        df_struct = None
        if not parser.is_min and has_topology:
            struct_tool = StructureAnalyzer(step_name, TOPOLOGY_FILE, out_file)
            struct_tool.generate_pdb_snapshot()
            df_struct = struct_tool.run_analysis()
            
            # DCD Generation
            if is_prod_step(step_name):
                dcd_path = struct_tool.generate_dcd()
                if dcd_path: generated_dcd_paths.append(dcd_path)

        # 3. Reporting & Accumulation
        if parser.is_min:
            report.plot_minimization(df_thermo, step_name)
            final_val = f"{df_thermo.iloc[-1]['Energy']:.1f}"
            report.add_summary(f"| {step_name} | MIN | {status} | {rows} | - | - | {final_val} kcal |")
        
        else:
            report.plot_equilibration(df_thermo, step_name)
            dens_val = f"{df_thermo.iloc[-1]['Density']:.4f}" if 'Density' in df_thermo.columns else "N/A"
            perf = f"{parser.performance['ns_per_day']:.1f}"
            
            # --- GLOBAL PLOT PREPARATION ---
            
            # A. Process Thermo Data
            start_t = df_thermo['Time_ps'].iloc[0]
            if start_t < cumulative_offset_thermo:
                 current_offset = cumulative_offset_thermo
            else:
                 current_offset = cumulative_offset_thermo

            step_time_vector = df_thermo['Time_ps'] - df_thermo['Time_ps'].iloc[0]
            df_thermo['Cum_Time_ns'] = (step_time_vector + cumulative_offset_thermo) / 1000.0
            
            actual_duration = step_time_vector.iloc[-1]
            cumulative_offset_thermo += actual_duration

            # Robust column handling (Fill missing with NaN to avoid KeyError)
            required_cols = ['Cum_Time_ns', 'Temp', 'EPtot', 'Density']
            for col in required_cols:
                if col not in df_thermo.columns:
                    df_thermo[col] = np.nan
            
            global_thermo_list.append(df_thermo[required_cols])

            # B. Process Struct Data
            if df_struct is not None:
                n_frames = len(df_struct)
                if n_frames > 0:
                    dt_struct = actual_duration / n_frames
                    struct_time_vector = np.arange(1, n_frames + 1) * dt_struct
                    df_struct['Cum_Time_ns'] = (struct_time_vector + cumulative_offset_struct) / 1000.0
                    
                    global_struct_list.append(df_struct)
                    cumulative_offset_struct += actual_duration

            report.add_summary(f"| {step_name} | MD | {status} | {rows} | {last_time:.1f} ps | {perf} | {dens_val} g/cm³ |")

    # 4. Generate Global Plots
    if global_thermo_list:
        print("Generating Global Production Plots...")
        final_thermo = pd.concat(global_thermo_list, ignore_index=True)
        final_struct = pd.concat(global_struct_list, ignore_index=True) if global_struct_list else pd.DataFrame()
        
        report.plot_production_global(final_thermo, final_struct)

    # 5. DCD Merging
    if generated_dcd_paths:
        print(f"\n--- Processing {len(generated_dcd_paths)} DCD files ---")
        final_dcd_list = []
        if not os.path.exists(PROD_DCD_DIR): os.makedirs(PROD_DCD_DIR)
        
        for src in generated_dcd_paths:
            dst = os.path.join(PROD_DCD_DIR, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                final_dcd_list.append(dst)
            except Exception as e:
                print(f"    [Error] Copying {os.path.basename(src)}: {e}")
        
        merge_dcd_files(final_dcd_list)

    report.save_report()
    print("\n--- QA Analysis Complete ---")

if __name__ == "__main__":
    main()
