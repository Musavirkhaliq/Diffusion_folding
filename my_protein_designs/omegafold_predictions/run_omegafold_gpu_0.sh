#!/bin/bash
# Script to run OmegaFold with conda environment

# Activate conda
# Try different methods to activate conda
if [ -f "$(conda info --base)/etc/profile.d/conda.sh" ]; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    echo "Activated conda using conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    echo "Activated conda using miniconda3 path"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
    echo "Activated conda using anaconda3 path"
else
    echo "Could not find conda.sh file. Trying conda init directly."
    conda init bash
    source ~/.bashrc
fi

# Activate the omegafold environment
conda activate omegafold

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate omegafold conda environment"
    echo "Trying alternative method..."
    export PATH="$HOME/miniconda3/envs/omegafold/bin:$PATH"
    if [ $? -ne 0 ]; then
        echo "Alternative method also failed. Exiting."
        exit 1
    fi
fi

# Print conda environment info for debugging
echo "Using conda environment:"
conda info
echo "Python path:"
which python
echo "OmegaFold path:"
ls -la /home/musa/anaconda3/envs/omegafold

# Run OmegaFold
CUDA_VISIBLE_DEVICES=0 python /home/musa/anaconda3/envs/omegafold/main.py my_protein_designs/omegafold_predictions/combined_gpu_0.fasta my_protein_designs/omegafold_predictions --device cuda:0
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "OmegaFold failed with exit code $exit_code"
    echo "Trying with pip installed omegafold..."
    CUDA_VISIBLE_DEVICES={gpus[gpu]} omegafold {combined_fasta} {omegafold_output_dir} --device cuda:0
fi
