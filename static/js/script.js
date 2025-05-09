// Enhanced JavaScript for the protein design pipeline web interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();

    // Initialize form validation
    initFormValidation();

    // Initialize device selection logic
    initDeviceSelection();

    // Initialize length range slider if it exists
    initRangeSliders();

    // Initialize protein visualization if on results page
    initProteinVisualization();

    // Add animation to workflow cards
    animateWorkflowCards();

    // Add molecule animation to header
    initMoleculeAnimation();

    // Initialize sequence viewer if on results page
    initSequenceViewer();
});

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation
function initFormValidation() {
    const form = document.querySelector('form');
    if (form) {
        // Add input validation on blur
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });

        // Form submission validation
        form.addEventListener('submit', function(event) {
            // Validate all inputs
            let isValid = true;
            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                event.preventDefault();
                return false;
            }

            // Additional validation for min/max length
            const minLength = parseInt(document.getElementById('min_length').value);
            const maxLength = parseInt(document.getElementById('max_length').value);

            if (minLength >= maxLength) {
                event.preventDefault();
                showValidationError(document.getElementById('min_length'), 'Minimum length must be less than maximum length');
                return false;
            }

            // Validate GPU selection
            const gpuCheckboxes = document.querySelectorAll('input[name="gpus[]"]:checked');
            if (gpuCheckboxes.length === 0) {
                event.preventDefault();

                // Find the GPU section and show error
                const gpuSection = document.querySelector('.gpu-section');
                if (gpuSection) {
                    showValidationError(gpuSection, 'Please select at least one GPU for OmegaFold');
                } else {
                    showAlert('Please select at least one GPU for OmegaFold', 'danger');
                }

                return false;
            }

            // Show loading state
            showLoadingState(form);
        });
    }
}

// Validate a single input
function validateInput(input) {
    // Skip validation for certain elements
    if (input.type === 'checkbox' || input.type === 'radio' || input.type === 'button' || input.type === 'submit') {
        return true;
    }

    let isValid = true;
    const value = input.value.trim();

    // Check if required
    if (input.hasAttribute('required') && value === '') {
        showValidationError(input, 'This field is required');
        isValid = false;
    }
    // Check min/max for number inputs
    else if (input.type === 'number') {
        const numValue = parseFloat(value);
        if (input.hasAttribute('min') && numValue < parseFloat(input.getAttribute('min'))) {
            showValidationError(input, `Value must be at least ${input.getAttribute('min')}`);
            isValid = false;
        }
        if (input.hasAttribute('max') && numValue > parseFloat(input.getAttribute('max'))) {
            showValidationError(input, `Value must be at most ${input.getAttribute('max')}`);
            isValid = false;
        }
    }

    // If valid, remove any error messages
    if (isValid) {
        clearValidationError(input);
    }

    return isValid;
}

// Show validation error for an input
function showValidationError(input, message) {
    // Clear any existing error
    clearValidationError(input);

    // Add error class to input
    input.classList.add('is-invalid');

    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;

    // Add error message after input
    input.parentNode.appendChild(errorDiv);
}

// Clear validation error for an input
function clearValidationError(input) {
    input.classList.remove('is-invalid');

    // Remove any existing error messages
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Show loading state on form submission
function showLoadingState(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    }

    // Add loading overlay to form
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Submitting job...</p>
        </div>
    `;

    form.parentNode.appendChild(loadingOverlay);
}

// Device selection logic
function initDeviceSelection() {
    const deviceSelect = document.getElementById('device');
    if (deviceSelect) {
        deviceSelect.addEventListener('change', function() {
            // If CPU is selected, show a warning
            if (this.value === 'cpu') {
                showAlert('Warning: Using CPU for backbone generation will be significantly slower than using a GPU.', 'warning');
            }
        });
    }
}

// Initialize range sliders
function initRangeSliders() {
    const lengthSlider = document.getElementById('length_range');
    if (lengthSlider) {
        const minLengthInput = document.getElementById('min_length');
        const maxLengthInput = document.getElementById('max_length');

        // Update the slider when inputs change
        minLengthInput.addEventListener('input', updateLengthRange);
        maxLengthInput.addEventListener('input', updateLengthRange);

        function updateLengthRange() {
            const min = parseInt(minLengthInput.value) || 10;
            const max = parseInt(maxLengthInput.value) || 200;

            // Update the range display
            lengthSlider.textContent = `${min} - ${max} amino acids`;

            // Update visual indicator if it exists
            const rangeIndicator = document.getElementById('length_indicator');
            if (rangeIndicator) {
                // Calculate percentage width based on min/max possible values
                const minPossible = 10;
                const maxPossible = 200;
                const leftPercent = ((min - minPossible) / (maxPossible - minPossible)) * 100;
                const widthPercent = ((max - min) / (maxPossible - minPossible)) * 100;

                rangeIndicator.style.left = `${leftPercent}%`;
                rangeIndicator.style.width = `${widthPercent}%`;
            }
        }

        // Initialize
        updateLengthRange();
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Find alert container or create one
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        document.body.prepend(alertContainer);
    }

    // Add alert to container
    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Initialize protein visualization
function initProteinVisualization() {
    const viewer = document.getElementById('modalProteinViewer');
    if (!viewer) {
        const proteinViewers = document.querySelectorAll('.protein-viewer');
        if (proteinViewers.length > 0) {
            // This is a placeholder for actual 3D visualization
            // In a real implementation, you would use a library like 3Dmol.js, NGL, or Mol*
            proteinViewers.forEach(viewer => {
                const pdbUrl = viewer.getAttribute('data-pdb-url');
                if (pdbUrl) {
                    // Here you would initialize the 3D viewer with the PDB data
                    console.log(`Initializing protein viewer with PDB: ${pdbUrl}`);

                    // Placeholder animation
                    viewer.innerHTML = `
                        <div class="d-flex justify-content-center align-items-center h-100">
                            <div class="text-center">
                                <div class="spinner-border text-primary mb-3" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p>Loading protein structure...</p>
                            </div>
                        </div>
                    `;

                    // Simulate loading
                    setTimeout(() => {
                        viewer.innerHTML = `
                            <div class="text-center">
                                <div class="protein-model-placeholder">
                                    <div class="protein-model-animation"></div>
                                </div>
                                <p class="mt-3">Protein structure loaded successfully</p>
                                <div class="btn-group mt-2">
                                    <button class="btn btn-sm btn-outline-primary">Cartoon</button>
                                    <button class="btn btn-sm btn-outline-primary">Surface</button>
                                    <button class="btn btn-sm btn-outline-primary">Sticks</button>
                                </div>
                            </div>
                        `;
                    }, 1500);
                }
            });
        }
        return;
    }

    const pdbUrl = viewer.getAttribute('data-pdb-url');
    if (!pdbUrl) return;

    // In a real implementation, this would use a 3D visualization library
    // like 3Dmol.js, NGL Viewer, or Mol*
    viewer.innerHTML = `
        <div class="text-center p-4">
            <div class="mb-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <p>Loading protein structure from ${pdbUrl}...</p>
            <p class="text-muted small">In a full implementation, this would display an interactive 3D model using a library like 3Dmol.js</p>
        </div>
    `;

    // Simulate loading
    setTimeout(() => {
        viewer.innerHTML = `
            <div class="text-center">
                <div class="protein-model-placeholder">
                    <div class="protein-model-animation"></div>
                </div>
                <p class="mt-3">Protein structure loaded successfully</p>
                <div class="btn-group mt-2">
                    <button class="btn btn-sm btn-outline-primary">Cartoon</button>
                    <button class="btn btn-sm btn-outline-primary">Surface</button>
                    <button class="btn btn-sm btn-outline-primary">Sticks</button>
                </div>
            </div>
        `;
    }, 1500);
}

// Animate workflow cards
function animateWorkflowCards() {
    const workflowCards = document.querySelectorAll('.workflow-card');
    if (workflowCards.length > 0) {
        // Add staggered animation
        workflowCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animated');
            }, 100 * index);
        });
    }
}

// Initialize molecule animation in header
function initMoleculeAnimation() {
    const header = document.querySelector('.page-header');
    if (header) {
        const moleculeAnimation = document.createElement('div');
        moleculeAnimation.className = 'molecule-animation';

        // This would be replaced with actual molecule animation
        // For now, just add a placeholder
        moleculeAnimation.innerHTML = `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="5" fill="#3498db" />
                <circle cx="70" cy="40" r="5" fill="#3498db" />
                <circle cx="30" cy="60" r="5" fill="#3498db" />
                <circle cx="60" cy="70" r="5" fill="#3498db" />
                <circle cx="40" cy="30" r="5" fill="#3498db" />
                <line x1="50" y1="50" x2="70" y2="40" stroke="#3498db" stroke-width="2" />
                <line x1="50" y1="50" x2="30" y2="60" stroke="#3498db" stroke-width="2" />
                <line x1="50" y1="50" x2="60" y2="70" stroke="#3498db" stroke-width="2" />
                <line x1="50" y1="50" x2="40" y2="30" stroke="#3498db" stroke-width="2" />
            </svg>
        `;

        header.appendChild(moleculeAnimation);
    }
}

// Initialize sequence viewer
function initSequenceViewer() {
    document.querySelectorAll('.sequence-display').forEach(container => {
        const sequence = container.getAttribute('data-sequence');
        if (sequence) {
            let formattedSequence = '';
            for (let i = 0; i < sequence.length; i++) {
                const aa = sequence[i];
                let colorClass = '';

                // Color amino acids by property
                if ('ILVAM'.includes(aa)) {
                    colorClass = 'hydrophobic';
                } else if ('FYWH'.includes(aa)) {
                    colorClass = 'aromatic';
                } else if ('KR'.includes(aa)) {
                    colorClass = 'positive';
                } else if ('DE'.includes(aa)) {
                    colorClass = 'negative';
                } else if ('STNQ'.includes(aa)) {
                    colorClass = 'polar';
                } else if ('CGP'.includes(aa)) {
                    colorClass = 'special';
                }

                formattedSequence += `<span class="aa ${colorClass}" title="${getAminoAcidName(aa)}">${aa}</span>`;

                // Add a space every 10 residues
                if ((i + 1) % 10 === 0) {
                    formattedSequence += ' ';
                }

                // Add a line break every 50 residues
                if ((i + 1) % 50 === 0) {
                    formattedSequence += '<br>';
                }
            }

            container.innerHTML = `
                <div class="sequence-numbers">1</div>
                <div class="sequence-content">${formattedSequence}</div>
            `;
        }
    });
}

// Get full amino acid name
function getAminoAcidName(code) {
    const aaNames = {
        'A': 'Alanine',
        'R': 'Arginine',
        'N': 'Asparagine',
        'D': 'Aspartic acid',
        'C': 'Cysteine',
        'E': 'Glutamic acid',
        'Q': 'Glutamine',
        'G': 'Glycine',
        'H': 'Histidine',
        'I': 'Isoleucine',
        'L': 'Leucine',
        'K': 'Lysine',
        'M': 'Methionine',
        'F': 'Phenylalanine',
        'P': 'Proline',
        'S': 'Serine',
        'T': 'Threonine',
        'W': 'Tryptophan',
        'Y': 'Tyrosine',
        'V': 'Valine'
    };
    return aaNames[code] || code;
}

// Add CSS for sequence display
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for amino acid coloring
    const style = document.createElement('style');
    style.textContent = `
        .sequence-display {
            font-family: var(--font-family-monospace);
            line-height: 1.5;
            letter-spacing: 1px;
        }
        .sequence-display .aa {
            display: inline-block;
            width: 1.2em;
            text-align: center;
            border-radius: 3px;
        }
        .sequence-display .hydrophobic { color: #FF9800; }
        .sequence-display .aromatic { color: #9C27B0; }
        .sequence-display .positive { color: #2196F3; }
        .sequence-display .negative { color: #F44336; }
        .sequence-display .polar { color: #4CAF50; }
        .sequence-display .special { color: #607D8B; }

        .protein-model-placeholder {
            width: 100%;
            height: 300px;
            background-color: rgba(10, 25, 41, 0.7);
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }

        .protein-model-animation {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 2px solid var(--primary-color);
            box-shadow: 0 0 20px var(--primary-color);
            animation: pulse 2s infinite, rotate 10s linear infinite;
        }

        .protein-model-animation::before,
        .protein-model-animation::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            border: 2px solid var(--secondary-color);
            animation: pulse 2s infinite 0.5s, rotate 8s linear infinite reverse;
        }

        .protein-model-animation::before {
            width: 100px;
            height: 100px;
        }

        .protein-model-animation::after {
            width: 50px;
            height: 50px;
            border-color: var(--accent-color);
            animation: pulse 2s infinite 1s, rotate 6s linear infinite;
        }
    `;
    document.head.appendChild(style);
});
