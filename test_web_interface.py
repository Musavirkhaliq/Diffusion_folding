#!/usr/bin/env python3
"""
Test script for the protein design web interface.
This script checks if all the required components are available.
"""

import os
import sys
import subprocess
import shutil

def check_component(name, check_function):
    """Check if a component is available"""
    print(f"Checking {name}... ", end="")
    result, message = check_function()
    if result:
        print("✓ Available")
        return True
    else:
        print(f"✗ Not available: {message}")
        return False

def check_flask():
    """Check if Flask is installed"""
    try:
        import flask
        return True, ""
    except ImportError:
        return False, "Flask is not installed. Install with 'pip install flask'"

def check_foldingdiff():
    """Check if FoldingDiff is available"""
    try:
        import foldingdiff
        return True, ""
    except ImportError:
        return False, "FoldingDiff module not found in Python path"

def check_proteinmpnn():
    """Check if ProteinMPNN is available"""
    proteinmpnn_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "software/ProteinMPNN")
    if os.path.exists(proteinmpnn_path) and os.path.exists(os.path.join(proteinmpnn_path, "protein_mpnn_run.py")):
        return True, ""
    else:
        return False, f"ProteinMPNN not found at {proteinmpnn_path}"

def check_omegafold():
    """Check if OmegaFold is available"""
    try:
        result = subprocess.run(
            "conda env list | grep omegafold",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if "omegafold" in result.stdout:
            return True, ""
        else:
            return False, "OmegaFold conda environment not found"
    except Exception as e:
        return False, f"Error checking OmegaFold: {str(e)}"

def check_pymol():
    """Check if PyMOL is available"""
    pymol_path = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol"
    if os.path.exists(pymol_path):
        return True, ""
    else:
        return False, f"PyMOL not found at {pymol_path}"

def check_gpu():
    """Check if GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            return True, f"Found {torch.cuda.device_count()} GPU(s)"
        else:
            return False, "No GPU available"
    except ImportError:
        return False, "PyTorch not installed"

def main():
    """Run all checks"""
    print("Testing Protein Design Web Interface Components\n")
    
    all_checks_passed = True
    
    # Check Flask
    if not check_component("Flask", check_flask):
        all_checks_passed = False
    
    # Check FoldingDiff
    if not check_component("FoldingDiff", check_foldingdiff):
        all_checks_passed = False
    
    # Check ProteinMPNN
    if not check_component("ProteinMPNN", check_proteinmpnn):
        all_checks_passed = False
    
    # Check OmegaFold
    if not check_component("OmegaFold", check_omegafold):
        all_checks_passed = False
    
    # Check PyMOL
    if not check_component("PyMOL", check_pymol):
        all_checks_passed = False
    
    # Check GPU
    if not check_component("GPU", check_gpu):
        all_checks_passed = False
    
    # Check directories
    print("\nChecking required directories:")
    for directory in ["templates", "static", "uploads", "results"]:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ (not found)")
            all_checks_passed = False
    
    # Final result
    print("\nTest result:")
    if all_checks_passed:
        print("✅ All components are available. The web interface should work correctly.")
        print("\nTo start the web interface, run:")
        print("  python app.py")
        print("\nThen open your browser at: http://localhost:5000")
    else:
        print("❌ Some components are missing. Please fix the issues above before running the web interface.")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
