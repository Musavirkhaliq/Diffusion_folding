# Protein Design Workflow

This guide provides a comprehensive walkthrough for the protein design pipeline that integrates:

1. **Backbone generation** using FoldingDiff (bin/sample)
2. **Sequence design** using ProteinMPNN
3. **Structure prediction** using OmegaFold
4. **Visualization** using PyMOL

## Prerequisites

Before starting, ensure you have the following installed:

- **FoldingDiff**: Already installed in this repository
- **ProteinMPNN**: Located at `/home/musa/Documents/augment-projects/foldingdiff/software/ProteinMPNN`
- **OmegaFold**: Installed in a conda environment named 'omegafold'
- **PyMOL**: Located at `/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol`

## Quick Start: Integrated Pipeline

For the simplest workflow, use the integrated interface that combines all steps:

```bash
# First activate the conda environment for OmegaFold
conda init
conda activate omegafold

# Then run the integrated interface
python bin/protein_design_interface.py -o ./my_protein_designs
```

This will:
- Generate protein backbones using FoldingDiff
- Design sequences using ProteinMPNN
- Predict structures using OmegaFold
- Visualize results with PyMOL

## Step-by-Step Workflow

If you prefer to run each step separately or need more control, follow this step-by-step guide:

### 1. Generate Protein Backbones with FoldingDiff

```bash
# Generate 10 backbones per length ranging from 50 to 128
python bin/sample.py -l 50 128 -n 10 -b 512 --device cuda:0 -o ./demo_backbone_samples

# To save the full diffusion history (for visualization)
python bin/sample.py -l 50 128 -n 10 -b 512 --device cuda:0 -o ./demo_backbone_samples --fullhistory
```

Key parameters:
- `-l`: Length range [min max]
- `-n`: Number of samples per length
- `-b`: Batch size
- `-o`: Output directory
- `--fullhistory`: Save intermediate steps of the diffusion process

Output:
- `sampled_angles/`: CSV files with backbone angles
- `sampled_pdb/`: PDB files of the generated backbones
- `plots/`: Distribution plots and Ramachandran plots

### 2. Design Sequences with ProteinMPNN

Once you have generated backbone structures, you can design sequences that would fold into these structures:

```bash
# Process all PDB files in the sampled_pdb directory
python bin/pdb_to_residue_proteinmpnn.py demo_backbone_samples/sampled_pdb -o demo_mpnn_samples
```

This will:
- Create a directory called `proteinmpnn_residues` containing FASTA files
- Generate multiple sequence designs per backbone (default: 8)

To customize the number of sequences or temperature:

```bash
# Generate 3 sequences with lower temperature (less diversity)
python bin/mpnn_utils.py demo_backbone_samples/sampled_pdb --num-sequences 3 --temperature 0.1
```

### 3. Predict Structures with OmegaFold

After designing sequences, predict their 3D structures using OmegaFold:

```bash
# Activate the OmegaFold conda environment
conda init
conda activate omegafold

# Run OmegaFold on all FASTA files, distributing across available GPUs
python bin/omegafold_across_gpus.py demo_mpnn_samples/proteinmpnn_residues/*.fasta -o ./demo_omegafold_predictions -g 0
```

Key parameters:
- First argument: Path to FASTA files
- `-o`: Output directory
- `-g`: GPU indices to use (e.g., 0 1 for using the first two GPUs)

### 4. Visualize with PyMOL

Finally, visualize the structures using PyMOL:

```bash
# Convert a single PDB to PNG
python foldingdiff/pymol_vis.py pdb2png -i omegafold_predictions/sample_0.pdb -o visualizations/sample_0.png --psea

# Convert a directory of PDBs to PNGs
python foldingdiff/pymol_vis.py pdb2png_batch -i omegafold_predictions -o visualizations --psea

# Create an animation from diffusion steps (if --fullhistory was used)
python foldingdiff/pymol_vis.py pdb2gif -i backbone_samples/sampled_pdb/sample_history/generated_0/*.pdb -o visualizations/generated_0.gif
```

## Comparing Original Backbones with Predicted Structures

To assess how well the designed sequences fold back to the original backbone:

```bash
# Calculate self-consistency TM scores
python bin/sctm.py -f omegafold_predictions
```

This produces:
- A JSON file with all scTM scores
- PDF plots showing the distribution of scores

## Troubleshooting

### OmegaFold Issues

If OmegaFold fails to run:
1. Ensure the conda environment is properly activated: `conda activate omegafold`
2. Check that OmegaFold is installed in the environment: `which omegafold`
3. Verify GPU availability: `nvidia-smi`

### ProteinMPNN Issues

If sequence design fails:
1. Verify ProteinMPNN is at the correct path: `/home/musa/Documents/augment-projects/foldingdiff/software/ProteinMPNN`
2. Check that the PDB files from FoldingDiff are valid

### PyMOL Issues

If visualization fails:
1. Ensure PyMOL is installed at the correct path: `/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol`
2. Try running PyMOL directly to check for any installation issues

## Output Directory Structure

When using the integrated pipeline, your output directory will have this structure:

```
my_protein_designs/
├── backbones/
│   ├── sampled_angles/     # CSV files with backbone angles
│   ├── sampled_pdb/        # PDB files of generated backbones
│   └── plots/              # Distribution plots
├── mpnn_sequences/         # FASTA files with designed sequences
├── omegafold_predictions/  # PDB files of predicted structures
└── visualizations/         # PNG images of structures
```

## Advanced Usage

### Customizing the Integrated Pipeline

The integrated interface supports many customization options:

```bash
python bin/protein_design_interface.py -o ./my_designs \
  --lengths 80 150 \
  --num-samples 5 \
  --mpnn-num-sequences 3 \
  --mpnn-temperature 0.2 \
  --gpus 0 1 \
  --omegafold-env omegafold
```

Run `python bin/protein_design_interface.py --help` for a full list of options.

### Running Only Specific Steps

To run only certain steps of the pipeline:

```bash
# Start from step 2 (sequence design) and end at step 3 (structure prediction)
python bin/protein_design_interface.py -o ./my_designs --start-from-step 2 --end-at-step 3
```

## References

- FoldingDiff: [arXiv paper](https://arxiv.org/abs/2209.15611)
- ProteinMPNN: [GitHub repository](https://github.com/dauparas/ProteinMPNN)
- OmegaFold: [GitHub repository](https://github.com/HeliXonProtein/OmegaFold)
