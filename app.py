#!/usr/bin/env python3
"""
Web interface for protein design workflow using FoldingDiff, ProteinMPNN, OmegaFold, and PyMOL.
"""

import os
import sys
import uuid
import json
import shutil
import subprocess
import threading
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, redirect

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Global dictionary to store job status
job_status = {}

# Paths to required tools
FOLDINGDIFF_PATH = os.path.dirname(os.path.abspath(__file__))
PROTEINMPNN_PATH = os.path.join(FOLDINGDIFF_PATH, "software/ProteinMPNN")
OMEGAFOLD_ENV = "omegafold"  # Conda environment name
PYMOL_PATH = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol"

def generate_job_id():
    """Generate a unique job ID"""
    return str(uuid.uuid4())

def update_job_status(job_id, status, message="", progress=0):
    """Update the status of a job"""
    job_status[job_id] = {
        "status": status,
        "message": message,
        "progress": progress
    }
    logger.info(f"Job {job_id}: {status} - {message} ({progress}%)")

def run_backbone_generation(job_id, output_dir, min_length, max_length, num_samples, batch_size, device):
    """Run the backbone generation step using FoldingDiff"""
    try:
        update_job_status(job_id, "running", "Generating protein backbones...", 10)

        # Create output directory
        backbone_dir = os.path.join(output_dir, "backbone_sampling")
        os.makedirs(backbone_dir, exist_ok=True)

        # Build command
        cmd = [
            "python",
            os.path.join(FOLDINGDIFF_PATH, "bin/sample.py"),
            "-l", str(min_length), str(max_length),
            "-n", str(num_samples),
            "-b", str(batch_size),
            "--device", device,
            "-o", backbone_dir
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
            logger.error(f"Backbone generation failed: {stderr}")
            update_job_status(job_id, "failed", f"Backbone generation failed: {stderr}", 10)
            return False

        logger.info(f"Backbone generation completed successfully")
        update_job_status(job_id, "running", "Backbone generation completed", 25)
        return backbone_dir

    except Exception as e:
        logger.exception("Error in backbone generation")
        update_job_status(job_id, "failed", f"Error in backbone generation: {str(e)}", 10)
        return False

def run_sequence_design(job_id, output_dir, backbone_dir, num_sequences, temperature):
    """Run the sequence design step using ProteinMPNN"""
    try:
        update_job_status(job_id, "running", "Designing sequences...", 30)

        # Create output directory
        mpnn_dir = os.path.join(output_dir, "mpnn_sequences")

        # If the directory already exists, remove it first
        if os.path.exists(mpnn_dir):
            logger.info(f"Removing existing directory: {mpnn_dir}")
            shutil.rmtree(mpnn_dir)

        # Get path to PDB files
        pdb_dir = os.path.join(backbone_dir, "sampled_pdb")

        # Build command
        cmd = [
            "python",
            os.path.join(FOLDINGDIFF_PATH, "bin/pdb_to_residue_proteinmpnn.py"),
            pdb_dir,
            "-o", mpnn_dir,
            "-n", str(num_sequences),
            "-t", str(temperature)
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
            update_job_status(job_id, "failed", f"Sequence design failed: {stderr}", 30)
            return False

        logger.info(f"Sequence design completed successfully")
        update_job_status(job_id, "running", "Sequence design completed", 50)
        return mpnn_dir

    except Exception as e:
        logger.exception("Error in sequence design")
        update_job_status(job_id, "failed", f"Error in sequence design: {str(e)}", 30)
        return False

def run_structure_prediction(job_id, output_dir, mpnn_dir, gpus):
    """Run the structure prediction step using OmegaFold"""
    try:
        update_job_status(job_id, "running", "Predicting structures...", 55)

        # Create output directory
        omegafold_dir = os.path.join(output_dir, "omegafold_predictions")
        if os.path.exists(omegafold_dir):
            logger.info(f"Removing existing directory: {omegafold_dir}")
            shutil.rmtree(omegafold_dir)
        os.makedirs(omegafold_dir, exist_ok=True)

        # Copy FASTA files to a temporary directory to avoid permission issues
        temp_fasta_dir = os.path.join(omegafold_dir, "temp_fasta")
        os.makedirs(temp_fasta_dir, exist_ok=True)

        # Copy all FASTA files from mpnn_dir to temp_fasta_dir
        for fasta_file in os.listdir(mpnn_dir):
            if fasta_file.endswith('.fasta'):
                src = os.path.join(mpnn_dir, fasta_file)
                dst = os.path.join(temp_fasta_dir, fasta_file)
                shutil.copy2(src, dst)
                # Ensure the file has the right permissions
                os.chmod(dst, 0o644)

        # Check if we have any FASTA files
        fasta_files = [f for f in os.listdir(temp_fasta_dir) if f.endswith('.fasta')]
        if not fasta_files:
            logger.error("No FASTA files found in the MPNN output directory")
            update_job_status(job_id, "failed", "No FASTA files found in the MPNN output directory", 55)
            return False

        logger.info(f"Found {len(fasta_files)} FASTA files for structure prediction")

        # Create a separate output directory for OmegaFold to avoid the exist_ok=False issue
        omegafold_output_dir = os.path.join(omegafold_dir, "predictions")
        if os.path.exists(omegafold_output_dir):
            logger.info(f"Removing existing directory: {omegafold_output_dir}")
            shutil.rmtree(omegafold_output_dir)

        # Build command with conda activation
        # Format the GPU arguments correctly
        gpu_args = " ".join(map(str, gpus)) if gpus else "0"

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
            update_job_status(job_id, "failed", f"Structure prediction failed: {stderr}", 55)
            return False

        # Move PDB files from the predictions directory to the main omegafold_dir
        omegafold_output_dir = os.path.join(omegafold_dir, "predictions")
        if os.path.exists(omegafold_output_dir):
            for file in os.listdir(omegafold_output_dir):
                if file.endswith('.pdb'):
                    src = os.path.join(omegafold_output_dir, file)
                    dst = os.path.join(omegafold_dir, file)
                    shutil.copy2(src, dst)

        # Check if any PDB files were created
        pdb_files = [f for f in os.listdir(omegafold_dir) if f.endswith('.pdb')]
        if not pdb_files:
            logger.error("No PDB files were generated by OmegaFold")
            update_job_status(job_id, "failed", "No PDB files were generated by OmegaFold", 55)
            return False

        logger.info(f"Structure prediction completed successfully with {len(pdb_files)} PDB files")
        update_job_status(job_id, "running", "Structure prediction completed", 75)
        return omegafold_dir

    except Exception as e:
        logger.exception("Error in structure prediction")
        update_job_status(job_id, "failed", f"Error in structure prediction: {str(e)}", 55)
        return False

def run_visualization(job_id, output_dir, omegafold_dir):
    """Run the visualization step using PyMOL"""
    try:
        update_job_status(job_id, "running", "Generating visualizations...", 80)

        # Create output directory
        vis_dir = os.path.join(output_dir, "visualizations")
        os.makedirs(vis_dir, exist_ok=True)

        # Path to PyMOL executable
        PYMOL_EXECUTABLE = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol/pymol"

        # Check if PyMOL executable exists
        if not os.path.exists(PYMOL_EXECUTABLE):
            logger.error(f"PyMOL executable not found at {PYMOL_EXECUTABLE}")
            update_job_status(job_id, "failed", f"PyMOL executable not found at {PYMOL_EXECUTABLE}", 80)
            return False

        # Get list of PDB files
        pdb_files = [f for f in os.listdir(omegafold_dir) if f.endswith('.pdb')]
        if not pdb_files:
            logger.error("No PDB files found for visualization")
            update_job_status(job_id, "failed", "No PDB files found for visualization", 80)
            return False

        logger.info(f"Found {len(pdb_files)} PDB files for visualization")

        # Process each PDB file
        for pdb_file in pdb_files:
            pdb_path = os.path.join(omegafold_dir, pdb_file)
            png_path = os.path.join(vis_dir, pdb_file.replace('.pdb', '.png'))

            # Create a PyMOL script
            pymol_script = os.path.join(vis_dir, f"render_{pdb_file}.pml")
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
                logger.warning(f"PyMOL visualization failed for {pdb_file}: {stderr}")
                # Continue with other files even if one fails

        # Check if any PNG files were created
        png_files = [f for f in os.listdir(vis_dir) if f.endswith('.png')]
        if not png_files:
            logger.error("No PNG files were generated by PyMOL")
            update_job_status(job_id, "failed", "No PNG files were generated by PyMOL", 80)
            return False

        logger.info(f"Visualization completed successfully with {len(png_files)} PNG files")
        update_job_status(job_id, "completed", "All steps completed successfully", 100)
        return vis_dir

    except Exception as e:
        logger.exception("Error in visualization")
        update_job_status(job_id, "failed", f"Error in visualization: {str(e)}", 80)
        return False

def run_protein_design_pipeline(job_id, params):
    """Run the complete protein design pipeline"""
    try:
        # Create output directory
        output_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        os.makedirs(output_dir, exist_ok=True)

        # Save parameters
        with open(os.path.join(output_dir, "params.json"), "w") as f:
            json.dump(params, f, indent=2)

        # Step 1: Generate backbones
        backbone_dir = run_backbone_generation(
            job_id,
            output_dir,
            params["min_length"],
            params["max_length"],
            params["num_samples"],
            params["batch_size"],
            params["device"]
        )
        if not backbone_dir:
            return

        # Step 2: Design sequences
        mpnn_dir = run_sequence_design(
            job_id,
            output_dir,
            backbone_dir,
            params["mpnn_num_sequences"],
            params["mpnn_temperature"]
        )
        if not mpnn_dir:
            return

        # Step 3: Predict structures
        omegafold_dir = run_structure_prediction(
            job_id,
            output_dir,
            mpnn_dir,
            params["gpus"]
        )
        if not omegafold_dir:
            return

        # Step 4: Visualize structures
        vis_dir = run_visualization(
            job_id,
            output_dir,
            omegafold_dir
        )
        if not vis_dir:
            return

        # All steps completed successfully
        update_job_status(job_id, "completed", "All steps completed successfully", 100)

    except Exception as e:
        logger.exception("Error in protein design pipeline")
        update_job_status(job_id, "failed", f"Error in protein design pipeline: {str(e)}", 0)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_job():
    """Submit a new protein design job"""
    try:
        # Generate a unique job ID
        job_id = generate_job_id()

        # Get parameters from form
        params = {
            "min_length": int(request.form.get('min_length', 50)),
            "max_length": int(request.form.get('max_length', 128)),
            "num_samples": int(request.form.get('num_samples', 3)),
            "batch_size": int(request.form.get('batch_size', 512)),
            "device": request.form.get('device', 'cuda:0'),
            "mpnn_num_sequences": int(request.form.get('mpnn_num_sequences', 3)),
            "mpnn_temperature": float(request.form.get('mpnn_temperature', 0.1)),
            "gpus": [int(g) for g in request.form.getlist('gpus[]')] if request.form.getlist('gpus[]') else [0]
        }

        # Initialize job status
        update_job_status(job_id, "submitted", "Job submitted", 0)

        # Run the pipeline in a separate thread
        thread = threading.Thread(
            target=run_protein_design_pipeline,
            args=(job_id, params)
        )
        thread.daemon = True
        thread.start()

        # Redirect to the job status page
        return redirect(url_for('job_status_page', job_id=job_id))

    except Exception as e:
        logger.exception("Error submitting job")
        return render_template('index.html', error=str(e))

@app.route('/job/<job_id>')
def job_status_page(job_id):
    """Render the job status page"""
    if job_id not in job_status:
        return render_template('error.html', message="Job not found"), 404

    return render_template('job.html', job_id=job_id)

@app.route('/api/job/<job_id>')
def get_job_status(job_id):
    """Get the status of a job"""
    if job_id not in job_status:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job_status[job_id])



@app.route('/results/<job_id>')
def view_results(job_id):
    """View the results of a completed job"""
    if job_id not in job_status:
        return render_template('error.html', message="Job not found"), 404

    if job_status[job_id]["status"] != "completed":
        return redirect(url_for('job_status_page', job_id=job_id))

    # Get paths to results
    output_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    vis_dir = os.path.join(output_dir, "visualizations")
    backbone_dir = os.path.join(output_dir, "backbone_sampling/sampled_pdb")
    omegafold_dir = os.path.join(output_dir, "omegafold_predictions")

    # Get list of visualization files
    vis_files = []
    if os.path.exists(vis_dir):
        vis_files = [f for f in os.listdir(vis_dir) if f.endswith('.png')]

    # Get list of backbone PDB files
    backbone_files = []
    if os.path.exists(backbone_dir):
        backbone_files = [f for f in os.listdir(backbone_dir) if f.endswith('.pdb')]

        # Generate visualizations for backbone PDBs if they don't exist
        backbone_vis_dir = os.path.join(vis_dir, "backbones")
        os.makedirs(backbone_vis_dir, exist_ok=True)

        # Check if we need to generate visualizations
        existing_backbone_vis = [f for f in os.listdir(backbone_vis_dir) if f.endswith('.png')] if os.path.exists(backbone_vis_dir) else []
        if len(existing_backbone_vis) < len(backbone_files):
            # Path to PyMOL executable
            PYMOL_EXECUTABLE = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol/pymol"

            # Generate visualizations for backbone PDBs
            for pdb_file in backbone_files:
                png_file = pdb_file.replace('.pdb', '.png')
                if png_file not in existing_backbone_vis:
                    pdb_path = os.path.join(backbone_dir, pdb_file)
                    png_path = os.path.join(backbone_vis_dir, png_file)

                    # Create a PyMOL script
                    pymol_script = os.path.join(backbone_vis_dir, f"render_{pdb_file}.pml")
                    with open(pymol_script, 'w') as f:
                        f.write(f"""
load {pdb_path}, protein
bg_color white
hide everything
show cartoon
color cyan
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
                    try:
                        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except Exception as e:
                        logger.warning(f"Failed to generate visualization for backbone {pdb_file}: {str(e)}")

    # Get parameters
    params = {}
    params_file = os.path.join(output_dir, "params.json")
    if os.path.exists(params_file):
        with open(params_file, "r") as f:
            params = json.load(f)

    return render_template(
        'results.html',
        job_id=job_id,
        vis_files=vis_files,
        backbone_files=backbone_files,
        params=params
    )

@app.route('/download/<job_id>/<path:filename>')
def download_file(job_id, filename):
    """Download a file from the results"""
    output_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    return send_from_directory(output_dir, filename, as_attachment=True)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
