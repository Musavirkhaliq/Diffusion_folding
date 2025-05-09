```mermaid
graph TD
    subgraph "1. Data Preparation"
        A1[CATH Protein Dataset] --> A2[Extract Dihedral Angles]
        A2 --> A3[Normalize to [-π, π]]
        A3 --> A4[Create Train/Val/Test Splits]
    end

    subgraph "2. Diffusion Model Training"
        B1[Forward Process: Add Noise] --> B2[BERT-based Transformer]
        B2 --> B3[Predict Added Noise]
        B3 --> B4[Compute Loss]
        B4 --> B5[Update Model Parameters]
        B5 --> |Next Batch| B1
    end

    subgraph "3. Backbone Sampling"
        C1[Initialize Random Noise] --> C2[Iterative Denoising]
        C2 --> C3[Convert Angles to 3D Coordinates]
        C3 --> C4[Generate PDB Files]
    end

    subgraph "4. Sequence Design"
        D1[Backbone PDB Files] --> D2[ProteinMPNN]
        D2 --> D3[Design Amino Acid Sequences]
        D3 --> D4[Generate FASTA Files]
    end

    subgraph "5. Structure Prediction"
        E1[FASTA Files] --> E2[OmegaFold]
        E2 --> E3[Predict 3D Structures]
        E3 --> E4[Generate PDB Files]
    end

    subgraph "6. Evaluation & Visualization"
        F1[Original Backbone] --> F2[TM-Score Calculation]
        E4 --> F2
        F2 --> F3[Self-Consistency Analysis]
        F3 --> F4[PyMOL Visualization]
    end

    A4 --> B1
    B5 --> |Trained Model| C1
    C4 --> D1
    D4 --> E1
    C4 --> F1
    F4 --> G[Final Protein Designs]
```
