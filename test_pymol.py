#!/usr/bin/env python3
"""
Test script for the PyMOL visualization step.
This script tests if the PyMOL visualization step works correctly.
"""

import os
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
FOLDINGDIFF_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(FOLDINGDIFF_PATH, "test_pymol")
OMEGAFOLD_DIR = os.path.join(FOLDINGDIFF_PATH, "my_protein_designs/omegafold_predictions")
PYMOL_EXECUTABLE = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol/pymol"

def main():
    """Run the test"""
    # Create test directory
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Check if PyMOL executable exists
    if not os.path.exists(PYMOL_EXECUTABLE):
        logger.error(f"PyMOL executable not found at {PYMOL_EXECUTABLE}")
        return False
    
    # Check if OmegaFold directory exists
    if not os.path.exists(OMEGAFOLD_DIR):
        logger.error(f"OmegaFold directory not found: {OMEGAFOLD_DIR}")
        return False
    
    # Get list of PDB files
    pdb_files = [f for f in os.listdir(OMEGAFOLD_DIR) if f.endswith('.pdb')]
    if not pdb_files:
        logger.error("No PDB files found for visualization")
        return False
    
    logger.info(f"Found {len(pdb_files)} PDB files for visualization")
    
    # Process each PDB file (limit to 1 for testing)
    pdb_file = pdb_files[0]
    pdb_path = os.path.join(OMEGAFOLD_DIR, pdb_file)
    png_path = os.path.join(TEST_DIR, pdb_file.replace('.pdb', '.png'))
    
    # Create a PyMOL script
    pymol_script = os.path.join(TEST_DIR, f"render_{pdb_file}.pml")
    with open(pymol_script, 'w') as f:
        f.write(f"""
load {pdb_path}, protein
bg_color white
hide everything
show cartoon
color spectrum
set ray_opaque_background, 0
set ray_shadows, 0
set antialias, 2
set ray_trace_mode, 1
ray 1200, 1200
png {png_path}, dpi=300
quit
""")
    
    # Run PyMOL with the script
    cmd = [PYMOL_EXECUTABLE, "-qc", pymol_script]
    
    logger.info(f"Running PyMOL for {pdb_file}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        logger.error(f"PyMOL visualization failed: {stderr}")
        return False
    
    # Check if PNG file was created
    if os.path.exists(png_path):
        logger.info(f"PNG file created successfully: {png_path}")
        return True
    else:
        logger.error(f"PNG file was not created: {png_path}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Test passed! The PyMOL visualization step works correctly.")
        print(f"Check the output image at: {os.path.join(TEST_DIR, os.listdir(TEST_DIR)[0])}")
    else:
        print("\n❌ Test failed! The PyMOL visualization step does not work correctly.")
