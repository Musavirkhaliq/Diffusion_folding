# FoldingDiff: Protein Design Pipeline Presentation

## Overview

FoldingDiff is a diffusion model-based approach for generating novel protein backbone structures. This presentation outlines the complete workflow from training the diffusion model to generating protein structures and designing functional sequences.

![Animation of diffusion model protein folds over timesteps](plots/generated_0.gif)

## Table of Contents

1. [Diffusion Model Training](#1-diffusion-model-training)
2. [Backbone Sampling](#2-backbone-sampling)
3. [Sequence Design with ProteinMPNN](#3-sequence-design-with-proteinmpnn)
4. [Structure Prediction with OmegaFold](#4-structure-prediction-with-omegafold)
5. [Evaluation and Visualization](#5-evaluation-and-visualization)
6. [Integrated Pipeline](#6-integrated-pipeline)

---

## 1. Diffusion Model Training

### Data Preparation

- **Dataset**: CATH protein dataset
- **Representation**: Protein backbones represented as sequences of dihedral angles (φ, ψ, ω, χ)
- **Preprocessing**: Angles normalized to [-π, π] range

### Diffusion Process

1. **Forward Process (Noising)**
   - Gradually add noise to protein backbone angles according to a noise schedule
   - Transition from clean data distribution to pure noise

2. **Noise Schedules**
   - Linear, quadratic, or cosine variance schedules
   - Controls the rate of noise addition across timesteps

3. **Model Architecture**
   - BERT-based transformer architecture
   - Inputs: Noisy angles + timestep embedding
   - Outputs: Predicted noise at each position

4. **Training Objective**
   - Predict the noise added at each timestep
   - Loss functions: Smooth L1 loss with special handling for angular features
   - Additional regularization: L2 norm, L1 norm, circle regularization

### Training Loop

```
1. Sample clean data x₀ from dataset
2. Sample timestep t ~ Uniform(1, T)
3. Sample noise ε ~ N(0, I)
4. Create noisy sample xₜ using noise schedule
5. Predict noise ε_θ(xₜ, t)
6. Compute loss between predicted and actual noise
7. Update model parameters
```

### Implementation Details

- **Framework**: PyTorch Lightning
- **Hyperparameters**:
  - Learning rate: 5e-5
  - Batch size: 512
  - Timesteps: 1000
  - Hidden dimension: 384
  - Attention heads: 12

---

## 2. Backbone Sampling

### Reverse Diffusion Process

1. **Starting Point**: Pure noise xₜ ~ N(0, I)
2. **Iterative Denoising**:
   - Gradually remove noise using the trained model
   - For each timestep t from T to 1:
     - Predict noise ε_θ(xₜ, t)
     - Compute mean of posterior distribution
     - Sample xₜ₋₁ from posterior distribution

3. **Sampling Algorithm**:
   ```python
   def p_sample_loop(model, lengths, noise, timesteps, betas, is_angle):
       # Start from pure noise
       img = noise.to(device)
       imgs = []
       
       # Iteratively denoise
       for i in reversed(range(0, timesteps)):
           img = p_sample(model, img, t=i, seq_lens=lengths, t_index=i, betas=betas)
           
           # Wrap angular values to [-π, π]
           if is_angle:
               img = modulo_with_wrapped_range(img, range_min=-torch.pi, range_max=torch.pi)
               
           imgs.append(img.cpu())
       return torch.stack(imgs)
   ```

4. **Length Control**:
   - Generate proteins of specific lengths
   - Attention masking to handle variable-length sequences

5. **Output**:
   - Protein backbone angles (φ, ψ, ω, χ)
   - Converted to 3D coordinates using geometric transformations
   - Saved as PDB files for further processing

---

## 3. Sequence Design with ProteinMPNN

### ProteinMPNN Overview

- **Purpose**: Design amino acid sequences that would fold into the generated backbone
- **Architecture**: Message Passing Neural Network
- **Input**: Protein backbone structure (CA-only or full backbone)
- **Output**: Probability distribution over amino acids at each position

### Sequence Design Process

1. **Backbone Preparation**:
   - Convert sampled angles to 3D coordinates
   - Generate PDB files with backbone atoms

2. **ProteinMPNN Execution**:
   ```bash
   python software/ProteinMPNN/protein_mpnn_run.py \
       --pdb_path sampled_pdb/sample_0.pdb \
       --out_folder proteinmpnn_residues \
       --num_seq_per_target 8 \
       --sampling_temp 0.1
   ```

3. **Parameters**:
   - `num_seq_per_target`: Number of sequences to generate per backbone
   - `sampling_temp`: Temperature for sampling (higher = more diversity)

4. **Output**:
   - Multiple FASTA files containing designed amino acid sequences
   - Each sequence optimized to fold into the input backbone

---

## 4. Structure Prediction with OmegaFold

### OmegaFold Overview

- **Purpose**: Predict 3D structure from amino acid sequence
- **Advantage**: Fast runtime compared to AlphaFold2, designed for de novo proteins
- **Input**: Amino acid sequence (FASTA format)
- **Output**: Predicted 3D structure (PDB format)

### Structure Prediction Process

1. **Environment Setup**:
   - Conda environment with OmegaFold dependencies
   - GPU acceleration for faster prediction

2. **Prediction Execution**:
   ```bash
   CUDA_VISIBLE_DEVICES=0 omegafold input.fasta output_dir --device cuda:0
   ```

3. **Parallel Processing**:
   - Distribute predictions across multiple GPUs
   - Process batches of sequences for efficiency

4. **Output**:
   - PDB files containing predicted 3D structures
   - Used to validate the sequence design process

---

## 5. Evaluation and Visualization

### Self-Consistency Evaluation

1. **TM-Score Calculation**:
   - Compare original backbone with structure predicted from designed sequence
   - Higher TM-score indicates better self-consistency

2. **Analysis**:
   ```bash
   python bin/sctm.py -f omegafold_predictions
   ```

3. **Metrics**:
   - Self-consistency TM scores
   - RMSD between original and predicted structures
   - Statistical analysis of design quality

### Visualization

1. **PyMOL Visualization**:
   - Generate high-quality images of protein structures
   - Create animations of the diffusion process

2. **Commands**:
   ```bash
   # Convert PDB to PNG
   python foldingdiff/pymol_vis.py pdb2png -i structure.pdb -o image.png
   
   # Create animation from diffusion steps
   python foldingdiff/pymol_vis.py pdb2gif -i history/*.pdb -o animation.gif
   ```

---

## 6. Integrated Pipeline

### End-to-End Workflow

The entire process from backbone generation to structure prediction is integrated into a single interface:

```bash
python bin/protein_design_interface.py -o ./my_protein_designs
```

### Pipeline Steps

1. **Backbone Generation**:
   - Generate protein backbones using FoldingDiff
   - Control protein length and sampling parameters

2. **Sequence Design**:
   - Design sequences using ProteinMPNN
   - Multiple sequences per backbone with controlled diversity

3. **Structure Prediction**:
   - Predict structures using OmegaFold
   - Distribute across available GPUs

4. **Visualization and Analysis**:
   - Generate images and animations
   - Calculate self-consistency metrics

### Customization Options

- **Length Range**: Control the length of generated proteins
- **Number of Samples**: Generate multiple designs
- **Temperature**: Control sequence diversity
- **GPU Selection**: Specify which GPUs to use

---

## References

- FoldingDiff: [arXiv paper](https://arxiv.org/abs/2209.15611)
- ProteinMPNN: [GitHub repository](https://github.com/dauparas/ProteinMPNN)
- OmegaFold: [GitHub repository](https://github.com/HeliXonProtein/OmegaFold)
- PyMOL: [Official website](https://pymol.org/)
