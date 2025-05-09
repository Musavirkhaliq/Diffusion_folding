#!/usr/bin/env python3
"""
Test script for the OmegaFold structure prediction step.
This script tests if the OmegaFold step works correctly.
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
TEST_DIR = os.path.join(FOLDINGDIFF_PATH, "test_omegafold")
MPNN_DIR = os.path.join(FOLDINGDIFF_PATH, "my_protein_designs/mpnn_sequences")
OMEGAFOLD_ENV = "omegafold"  # Conda environment name

def main():
    """Run the test"""
    # Create test directory
    os.makedirs(TEST_DIR, exist_ok=True)

    # Create output directory
    omegafold_dir = os.path.join(TEST_DIR, "omegafold_predictions")
    if os.path.exists(omegafold_dir):
        logger.info(f"Removing existing directory: {omegafold_dir}")
        shutil.rmtree(omegafold_dir)
    os.makedirs(omegafold_dir, exist_ok=True)

    # Copy FASTA files to a temporary directory to avoid permission issues
    temp_fasta_dir = os.path.join(omegafold_dir, "temp_fasta")
    os.makedirs(temp_fasta_dir, exist_ok=True)

    # Check if MPNN directory exists
    if not os.path.exists(MPNN_DIR):
        logger.error(f"MPNN directory not found: {MPNN_DIR}")
        return False

    # Copy all FASTA files from MPNN_DIR to temp_fasta_dir
    fasta_count = 0
    for fasta_file in os.listdir(MPNN_DIR):
        if fasta_file.endswith('.fasta'):
            src = os.path.join(MPNN_DIR, fasta_file)
            dst = os.path.join(temp_fasta_dir, fasta_file)
            shutil.copy2(src, dst)
            # Ensure the file has the right permissions
            os.chmod(dst, 0o644)
            fasta_count += 1

    # Check if we have any FASTA files
    if fasta_count == 0:
        logger.error("No FASTA files found in the MPNN output directory")
        return False

    logger.info(f"Found {fasta_count} FASTA files for structure prediction")

    # Create a separate output directory for OmegaFold to avoid the exist_ok=False issue
    omegafold_output_dir = os.path.join(omegafold_dir, "predictions")
    if os.path.exists(omegafold_output_dir):
        logger.info(f"Removing existing directory: {omegafold_output_dir}")
        shutil.rmtree(omegafold_output_dir)

    # Build command with conda activation
    # Format the GPU arguments correctly
    gpu_args = "0"  # Use GPU 0 by default

    cmd = f"""#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate {OMEGAFOLD_ENV}
python {os.path.join(FOLDINGDIFF_PATH, "bin/omegafold_across_gpus.py")} {temp_fasta_dir}/*.fasta -o {omegafold_output_dir} -g {gpu_args}
"""

    # Write the command to a temporary script file
    script_path = os.path.join(omegafold_dir, "run_omegafold.sh")
    with open(script_path, 'w') as f:
        f.write(cmd)

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Run the script
    logger.info(f"Running script: {script_path}")
    process = subprocess.Popen(
        script_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        logger.error(f"Structure prediction failed: {stderr}")
        return False

    logger.info(f"Structure prediction completed successfully")

    # Move PDB files from the predictions directory to the main omegafold_dir
    omegafold_output_dir = os.path.join(omegafold_dir, "predictions")
    if os.path.exists(omegafold_output_dir):
        for file in os.listdir(omegafold_output_dir):
            if file.endswith('.pdb'):
                src = os.path.join(omegafold_output_dir, file)
                dst = os.path.join(omegafold_dir, file)
                shutil.copy2(src, dst)

    # Check if PDB files were created
    pdb_files = [f for f in os.listdir(omegafold_dir) if f.endswith('.pdb')]
    if pdb_files:
        logger.info(f"Found {len(pdb_files)} PDB files in {omegafold_dir}")
        return True
    else:
        logger.error(f"No PDB files found in {omegafold_dir}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Test passed! The OmegaFold structure prediction step works correctly.")
    else:
        print("\n❌ Test failed! The OmegaFold structure prediction step does not work correctly.")
