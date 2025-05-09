# Protein Design Web Interface

This modern, futuristic web interface provides a user-friendly way to run the protein design pipeline, which includes:

1. **Backbone generation** using FoldingDiff
2. **Sequence design** using ProteinMPNN
3. **Structure prediction** using OmegaFold
4. **Visualization** using PyMOL

## Features

- **Modern UI**: Clean, futuristic design with animations and visual feedback
- **Real-time job monitoring**: Track the progress of your protein design jobs
- **Interactive visualization**: View protein structures and sequences
- **Responsive design**: Works on desktop and mobile devices

## Prerequisites

Before running the web interface, ensure you have the following installed:

- **FoldingDiff**: Already installed in this repository
- **ProteinMPNN**: Located at `/home/musa/Documents/augment-projects/foldingdiff/software/ProteinMPNN`
- **OmegaFold**: Installed in a conda environment named 'omegafold'
- **PyMOL**: Located at `/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol`
- **Flask**: Install with `pip install flask`

## Running the Web Interface

1. Navigate to the root directory of the FoldingDiff repository:
   ```bash
   cd /home/musa/Documents/augment-projects/foldingdiff
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Using the Web Interface

### 1. Configure Parameters

On the main page, you can configure the following parameters:

#### Basic Settings:
- **Backbone Generation**:
  - Minimum Length: Minimum protein length (default: 50)
  - Maximum Length: Maximum protein length (default: 128)
  - Number of Samples: Number of backbones to generate per length (default: 3)

- **Sequence Design**:
  - Sequences per Backbone: Number of sequences to design per backbone (default: 3)
  - Temperature: Sampling temperature for ProteinMPNN (default: 0.1)

- **GPU Settings**:
  - Device: Device for backbone generation (default: GPU 0)
  - GPUs for OmegaFold: Select which GPUs to use for structure prediction

#### Advanced Settings:
- Batch Size: Batch size for backbone generation (default: 512)

### 2. Start the Pipeline

Click the "Start Protein Design Pipeline" button to begin the process. You'll be redirected to a job status page where you can monitor the progress.

### 3. Monitor Progress

The job status page shows:
- Current status of the job (submitted, running, completed, or failed)
- Progress bar indicating overall completion
- Step indicators showing which stage of the pipeline is currently running
- Status messages with details about the current operation

### 4. View Results

Once the job is completed, you can:
- View visualizations of the generated structures
- Download the generated files:
  - Backbone PDB files
  - Sequence FASTA files
  - Predicted structure PDB files
  - Visualization PNG files

## Troubleshooting

### OmegaFold Issues

If structure prediction fails:
1. Ensure the conda environment is properly activated
2. Check that OmegaFold is installed in the environment
3. Verify GPU availability with `nvidia-smi`

### PyMOL Issues

If visualization fails:
1. Ensure PyMOL is installed at the correct path
2. Try running PyMOL directly to check for any installation issues

## Output Directory Structure

For each job, the output directory will have this structure:

```
results/[job_id]/
├── backbone_sampling/
│   ├── sampled_angles/     # CSV files with backbone angles
│   ├── sampled_pdb/        # PDB files of generated backbones
│   └── plots/              # Distribution plots
├── mpnn_sequences/         # FASTA files with designed sequences
├── omegafold_predictions/  # PDB files of predicted structures
└── visualizations/         # PNG images of structures
```

## Advanced Usage

For more control over the protein design pipeline, you can use the command-line tools directly as described in the `PROTEIN_DESIGN_WORKFLOW.md` file.
