```mermaid
graph LR
    subgraph "Forward Process (Training)"
        A1[Clean Protein Angles x₀] --> |Add Noise| A2[Noisy Angles x₁]
        A2 --> |Add Noise| A3[Noisy Angles x₂]
        A3 --> |...| A4[Pure Noise xₜ]
    end

    subgraph "Model Training"
        B1[Noisy Angles xₜ] --> B2[BERT Transformer]
        B3[Timestep t] --> B2
        B2 --> B4[Predicted Noise ε_θ]
        B4 --> B5[Loss Function]
        B6[Actual Noise ε] --> B5
        B5 --> B7[Update Parameters]
    end

    subgraph "Reverse Process (Sampling)"
        C1[Random Noise xₜ] --> |Denoise| C2[Less Noisy x_{t-1}]
        C2 --> |Denoise| C3[Less Noisy x_{t-2}]
        C3 --> |...| C4[Clean Protein Angles x₀]
    end

    A4 --> B1
    B7 --> |Trained Model| C1
```
