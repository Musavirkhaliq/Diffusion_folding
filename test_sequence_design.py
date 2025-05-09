#!/usr/bin/env python3
"""
Test script for the sequence design step.
This script tests if the sequence design step works correctly.
"""

import os
import shutil
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
FOLDINGDIFF_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(FOLDINGDIFF_PATH, "test_sequence_design")
BACKBONE_DIR = os.path.join(FOLDINGDIFF_PATH, "backbone_samples")
MPNN_DIR = os.path.join(TEST_DIR, "mpnn_sequences")

def main():
    """Run the test"""
    # Create test directory
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # If the MPNN directory already exists, remove it
    if os.path.exists(MPNN_DIR):
        logger.info(f"Removing existing directory: {MPNN_DIR}")
        shutil.rmtree(MPNN_DIR)
    
    # Get path to PDB files
    pdb_dir = os.path.join(BACKBONE_DIR, "sampled_pdb")
    
    # Build command
    cmd = [
        "python", 
        os.path.join(FOLDINGDIFF_PATH, "bin/pdb_to_residue_proteinmpnn.py"),
        pdb_dir,
        "-o", MPNN_DIR,
        "-n", "3",
        "-t", "0.1"
    ]
    
    # Run command
    logger.info(f"Running command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Sequence design failed: {stderr}")
        return False
    
    logger.info(f"Sequence design completed successfully")
    
    # Check if files were created
    if os.path.exists(MPNN_DIR) and os.listdir(MPNN_DIR):
        logger.info(f"Found {len(os.listdir(MPNN_DIR))} files in {MPNN_DIR}")
        return True
    else:
        logger.error(f"No files found in {MPNN_DIR}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Test passed! The sequence design step works correctly.")
    else:
        print("\n❌ Test failed! The sequence design step does not work correctly.")
