import os
import runpy
import sys

# Master list of active python chart-generating scripts
scripts = [
    'Russia_Pivot.py',
    'Russia_Anomaly_Comp.py',
    'Security_Dumbbell.py',
    'Initiative_Consensus.py',
    'Clusters.py',
    'Impact_Dumbbell.py',
    'Digital_Surveillance_Comp.py',
    'Rank_Humanitarian.py',
    'Land_vs_Sea_Comp.py',
    'Initiatives_Comparison.py',
    'Humanitarian_Dumbbell.py',
    'Clusters_Positions_Shapes.py',
    'Initiative_Performance.py',
    'Rank_Invest_and_Rank_Arms.py'
]

def main():
    # Pivot working directory to the directory where run_all.py resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
        
    print("=" * 60)
    print("       CHART GENERATION PIPELINE INITIALIZED")
    print("=" * 60)
    
    try:
        from china_config import LANG, OUTPUT_DIR
        print(f"[*] Target Language:       {LANG}")
        print(f"[*] Destination Directory:  {OUTPUT_DIR}/")
        print(f"[*] Working Directory:      {os.getcwd()}")
    except ImportError:
        print("[!] Warning: china_config.py not loaded properly.")
    print("-" * 60)

    # Gather Python files in current folder for diagnostic purposes
    py_files_in_dir = [f for f in os.listdir('.') if f.endswith('.py') and f != 'run_all.py']

    success_count = 0
    failed_count = 0

    for script in scripts:
        if os.path.exists(script):
            print(f"[PROCESS] Executing: {script}")
            try:
                # Run the script in its standalone local namespace
                runpy.run_path(script, run_name="__main__")
                success_count += 1
            except Exception as e:
                print(f"[ERROR] Failure in {script}: {e}")
                failed_count += 1
        else:
            print(f"[WARNING] File not found: {script}")
            failed_count += 1
        print("-" * 60)

    print("\n" + "=" * 60)
    print("       PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"[+] Successfully generated: {success_count} charts")
    if failed_count > 0:
        print(f"[!] Issues encountered:     {failed_count} files")
        
        # Diagnostic printout if nothing was generated
        if success_count == 0 and py_files_in_dir:
            print("\n[DIAGNOSTIC] No charts were generated.")
            print("The following Python files were detected in this folder:")
            for py_file in py_files_in_dir[:15]:
                print(f"  - {py_file}")
            if len(py_files_in_dir) > 15:
                print("  - ...and more")
            print("\nPlease verify if your script filenames match the list above exactly.")
        elif not py_files_in_dir:
            print("\n[DIAGNOSTIC] No Python files (other than run_all.py) were found in this folder.")
            print(f"Current lookup directory: {os.getcwd()}")
            print("Please make sure run_all.py is placed inside the exact directory containing your scripts.")
            
    print(f"[*] Check results in folder: '{OUTPUT_DIR}/'")
    print("=" * 60)

if __name__ == "__main__":
    main()