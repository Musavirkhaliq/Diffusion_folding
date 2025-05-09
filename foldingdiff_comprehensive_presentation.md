# FoldingDiff: Comprehensive Protein Design Pipeline

## Overview

FoldingDiff is a diffusion model-based approach for generating novel protein backbone structures. This presentation outlines the complete workflow from training the diffusion model to generating protein structures and designing functional sequences.

## Table of Contents

1. [Data Preparation](#1-data-preparation)
2. [Diffusion Model Training](#2-diffusion-model-training)
3. [Backbone Sampling](#3-backbone-sampling)
4. [Sequence Design with ProteinMPNN](#4-sequence-design-with-proteinmpnn)
5. [Structure Prediction with OmegaFold](#5-structure-prediction-with-omegafold)
6. [Evaluation and Visualization](#6-evaluation-and-visualization)
7. [Integrated Pipeline](#7-integrated-pipeline)

---

## 1. Data Preparation

### Dataset Processing

- **Source Dataset**: CATH protein dataset
- **Representation**: Protein backbones represented as sequences of dihedral angles (φ, ψ, ω, χ)
- **Preprocessing**:
  - Extract angles from PDB structures
  - Normalize angles to [-π, π] range
  - Pad sequences to fixed length
  - Create train/validation/test splits

### Angle Representation

- **Dihedral Angles**:
  - φ (phi): N-Cα bond rotation
  - ψ (psi): Cα-C bond rotation
  - ω (omega): C-N bond rotation
  - Additional angles for backbone geometry

- **Special Handling**:
  - Circular nature of angles requires special loss functions
  - Angles wrapped to [-π, π] range

---

## 2. Diffusion Model Training

### Diffusion Process

#### Forward Process (Noising)
- Gradually add noise to protein backbone angles according to a noise schedule
- Transition from clean data distribution to pure noise
- Implemented in `foldingdiff/datasets.py` as `NoisedAnglesDataset`

#### Noise Schedules
- **Options**: Linear, quadratic, or cosine variance schedules
- **Implementation**: `foldingdiff/beta_schedules.py`
- Controls the rate of noise addition across timesteps

```python
# Example of noise schedule implementation
def linear_beta_schedule(timesteps: int, beta_start=1e-4, beta_end=0.02) -> torch.Tensor:
    return torch.linspace(beta_start, beta_end, timesteps)
```

### Model Architecture

- **Base**: BERT-based transformer architecture
- **Implementation**: `foldingdiff/modelling.py` as `BertForDiffusion`
- **Components**:
  - Input embedding layer
  - Time embedding layer
  - Transformer encoder blocks
  - Output decoder layer

```python
# Model forward pass (simplified)
def forward(self, inputs, timestep, attention_mask=None):
    # Embed inputs
    inputs_upscaled = self.input_embed(inputs)
    
    # Embed timestep
    time_encoded = self.time_embed(timestep).unsqueeze(1)
    
    # Combine inputs with time embedding
    inputs_with_time = inputs_upscaled + time_encoded
    
    # Pass through transformer encoder
    encoder_outputs = self.encoder(inputs_with_time, attention_mask=attention_mask)
    
    # Decode outputs
    per_token_decoded = self.token_decoder(encoder_outputs[0])
    return per_token_decoded
```

### Training Objective

- **Goal**: Predict the noise added at each timestep
- **Loss Functions**: 
  - Smooth L1 loss with special handling for angular features
  - Optional pairwise distance loss
  - Additional regularization: L2 norm, L1 norm, circle regularization

```python
# Training step (simplified)
def training_step(self, batch, batch_idx):
    # Get loss terms for each feature
    loss_terms = self._get_loss_terms(batch)
    avg_loss = torch.mean(loss_terms)
    
    # Add regularization if needed
    if self.l1_lambda > 0:
        l1_penalty = sum(torch.linalg.norm(p, 1) for p in self.parameters())
        avg_loss += self.l1_lambda * l1_penalty
    
    # Log losses
    self.log_dict({"train_loss": avg_loss})
    return avg_loss
```

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
- **Training Script**: `bin/train.py`
- **Hyperparameters**:
  - Learning rate: 5e-5
  - Batch size: 512
  - Timesteps: 1000
  - Hidden dimension: 384
  - Attention heads: 12

---

## 3. Backbone Sampling

### Sampling Process

- **Reverse Diffusion**: Gradually denoise from random noise to protein structure
- **Implementation**: `foldingdiff/sampling.py`
- **Steps**:
  1. Start with random noise
  2. Iteratively apply denoising steps
  3. Convert final angles to 3D coordinates

```python
# Sampling process (simplified)
def sample(model, dataset, n=10, sweep_lengths=(50, 128)):
    # Initialize with random noise
    img = torch.randn(batch_size, seq_len, n_features)
    
    # Iteratively denoise
    for i in reversed(range(noise_timesteps)):
        img = p_sample(
            model=model,
            x=img,
            t=torch.full((batch_size,), fill_value=i),
            seq_lens=batch["lengths"],
            t_index=i,
            betas=dataset.alpha_beta_terms["betas"],
        )
        img = utils.modulo_with_wrapped_range(img)
    
    return img
```

### Angle to Structure Conversion

- **NERF Algorithm**: Natural extension reference frame
- **Implementation**: `foldingdiff/angles_and_coords.py`
- Converts dihedral angles to 3D atomic coordinates
- Generates PDB files with backbone atoms

### Sampling Interface

- **Script**: `bin/sample.py`
- **Features**:
  - Control protein length
  - Generate multiple samples
  - Save as PDB files
  - Visualize distributions

```bash
# Example sampling command
python bin/sample.py -m wukevin/foldingdiff_cath -o ./samples -n 10 -l 50 128
```

---

## 4. Sequence Design with ProteinMPNN

### ProteinMPNN Overview

- **Purpose**: Design amino acid sequences that would fold into the generated backbone
- **Architecture**: Message Passing Neural Network
- **Input**: Protein backbone structure (CA-only or full backbone)
- **Output**: Probability distribution over amino acids at each position

### Integration in FoldingDiff

- **Implementation**: `bin/mpnn_utils.py`
- **Wrapper**: `bin/protein_design_interface.py`
- Uses external ProteinMPNN software

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

3. **Output**:
   - FASTA files containing designed sequences
   - Multiple sequences per backbone with controlled diversity

---

## 5. Structure Prediction with OmegaFold

### OmegaFold Integration

- **Purpose**: Validate sequence designs by predicting their 3D structures
- **Implementation**: `bin/protein_design_interface.py`
- Uses external OmegaFold software

### Prediction Process

1. **Input Preparation**:
   - FASTA files from ProteinMPNN
   - Distribute across available GPUs

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

## 6. Evaluation and Visualization

### Self-Consistency Evaluation

1. **TM-Score Calculation**:
   - Compare original backbone with structure predicted from designed sequence
   - Implementation: `foldingdiff/tmalign.py` and `bin/sctm.py`
   - Higher TM-score indicates better self-consistency

2. **Analysis**:
   ```bash
   python bin/sctm.py -f omegafold_predictions
   ```

3. **Metrics**:
   - Self-consistency TM scores
   - RMSD between original and predicted structures
   - Statistical analysis of design quality

### Visualization with PyMOL

1. **Implementation**: `foldingdiff/pymol_vis.py`
2. **Features**:
   - Generate high-quality images of protein structures
   - Create animations of the diffusion process
   - Visualize secondary structure elements

3. **Commands**:
   ```bash
   # Convert PDB to PNG
   python foldingdiff/pymol_vis.py pdb2png -i structure.pdb -o image.png
   
   # Create animation from diffusion steps
   python foldingdiff/pymol_vis.py pdb2gif -i history/*.pdb -o animation.gif
   ```

---

## 7. Integrated Pipeline

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

### Implementation

- **Script**: `bin/protein_design_interface.py`
- **Features**:
  - Command-line interface
  - Configurable parameters
  - Progress tracking
  - Error handling

---

## Conclusion

FoldingDiff provides a complete pipeline for protein design:

1. **Novel Backbone Generation** using diffusion models
2. **Sequence Design** with ProteinMPNN
3. **Structure Validation** with OmegaFold
4. **Comprehensive Evaluation** with TM-score and visualization

This integrated approach enables the design of novel proteins with controlled structural properties.
