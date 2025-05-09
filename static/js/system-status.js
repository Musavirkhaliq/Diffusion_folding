// Enhanced System Status Visualization

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the system status visualization
    initSystemStatusVis();
});

// Initialize the system status visualization
function initSystemStatusVis() {
    // Create backbone nodes
    createBackboneNodes();
    
    // Create amino acid letters
    createAminoAcidLetters();
    
    // Create protein structure elements
    createProteinStructure();
    
    // Create visualization elements
    createVisualizationElements();
}

// Create backbone nodes for the backbone generation visualization
function createBackboneNodes() {
    const backboneVis = document.querySelector('.backbone-vis');
    if (!backboneVis) return;
    
    // Create 8 nodes along the chain
    for (let i = 0; i < 8; i++) {
        const node = document.createElement('div');
        node.className = 'backbone-node';
        node.style.left = `${(i + 1) * 12.5}%`;
        backboneVis.appendChild(node);
    }
}

// Create amino acid letters for the sequence design visualization
function createAminoAcidLetters() {
    const sequenceVis = document.querySelector('.sequence-vis');
    if (!sequenceVis) return;
    
    // Sample of amino acids with their property classes
    const aminoAcids = [
        { letter: 'M', class: 'hydrophobic' },
        { letter: 'K', class: 'positive' },
        { letter: 'T', class: 'polar' },
        { letter: 'L', class: 'hydrophobic' },
        { letter: 'F', class: 'aromatic' },
        { letter: 'G', class: 'special' },
        { letter: 'D', class: 'negative' },
        { letter: 'I', class: 'hydrophobic' },
        { letter: 'Y', class: 'aromatic' },
        { letter: 'R', class: 'positive' },
        { letter: 'S', class: 'polar' },
        { letter: 'P', class: 'special' },
        { letter: 'E', class: 'negative' },
        { letter: 'V', class: 'hydrophobic' },
        { letter: 'H', class: 'aromatic' }
    ];
    
    // Create amino acid letters
    aminoAcids.forEach(aa => {
        const letter = document.createElement('div');
        letter.className = `aa-letter ${aa.class}`;
        letter.textContent = aa.letter;
        sequenceVis.appendChild(letter);
    });
}

// Create protein structure elements for the structure prediction visualization
function createProteinStructure() {
    const structureVis = document.querySelector('.structure-vis');
    if (!structureVis) return;
    
    // Create protein model container
    const proteinModel = document.createElement('div');
    proteinModel.className = 'protein-model';
    structureVis.appendChild(proteinModel);
    
    // Create alpha helices
    for (let i = 0; i < 3; i++) {
        const helix = document.createElement('div');
        helix.className = 'helix';
        helix.style.transform = `rotate(${i * 60}deg) translateY(${i * 10}px)`;
        proteinModel.appendChild(helix);
    }
    
    // Create beta sheets
    for (let i = 0; i < 2; i++) {
        const sheet = document.createElement('div');
        sheet.className = 'sheet';
        sheet.style.transform = `rotate(${i * 90}deg) translateX(${i * 5}px)`;
        proteinModel.appendChild(sheet);
    }
}

// Create visualization elements for the visualization step
function createVisualizationElements() {
    const visualizationVis = document.querySelector('.visualization-vis');
    if (!visualizationVis) return;
    
    // Create render frame
    const renderFrame = document.createElement('div');
    renderFrame.className = 'render-frame';
    visualizationVis.appendChild(renderFrame);
    
    // Create render dots (scanning effect)
    for (let i = 0; i < 3; i++) {
        const renderDot = document.createElement('div');
        renderDot.className = 'render-dot';
        renderDot.style.left = `${(i + 1) * 25}%`;
        renderDot.style.top = '0';
        renderFrame.appendChild(renderDot);
    }
}

// Update the system status visualization based on job status
function updateSystemStatusVis(status) {
    const progress = status.progress;
    
    // Update backbone generation visualization
    updateBackboneVis(progress);
    
    // Update sequence design visualization
    updateSequenceVis(progress);
    
    // Update structure prediction visualization
    updateStructureVis(progress);
    
    // Update visualization step visualization
    updateVisualizationVis(progress);
}

// Update backbone generation visualization
function updateBackboneVis(progress) {
    const backboneCard = document.querySelector('.backbone-card');
    const backboneChain = document.querySelector('.backbone-chain');
    const backboneNodes = document.querySelectorAll('.backbone-node');
    
    if (!backboneCard || !backboneChain || !backboneNodes.length) return;
    
    // Update card status
    updateCardStatus(backboneCard, progress, 0, 25);
    
    // If running or completed
    if (progress > 0) {
        // Calculate backbone progress (0-100% within its phase)
        const backboneProgress = Math.min(100, progress * 4);
        
        // Animate the backbone chain
        backboneChain.style.width = `${backboneProgress}%`;
        
        // Show nodes based on progress
        backboneNodes.forEach((node, index) => {
            const nodeThreshold = (index + 1) * 12.5;
            if (backboneProgress >= nodeThreshold) {
                node.style.opacity = '1';
                node.style.animation = 'pulse 2s infinite';
            }
        });
    }
}

// Update sequence design visualization
function updateSequenceVis(progress) {
    const sequenceCard = document.querySelector('.sequence-card');
    const aaLetters = document.querySelectorAll('.aa-letter');
    
    if (!sequenceCard || !aaLetters.length) return;
    
    // Update card status
    updateCardStatus(sequenceCard, progress, 25, 50);
    
    // If running or completed
    if (progress > 25) {
        // Calculate sequence progress (0-100% within its phase)
        const sequenceProgress = Math.min(100, (progress - 25) * 4);
        
        // Show amino acids based on progress
        aaLetters.forEach((letter, index) => {
            const letterThreshold = (index + 1) * (100 / aaLetters.length);
            if (sequenceProgress >= letterThreshold) {
                letter.style.opacity = '1';
                letter.style.transform = 'scale(1)';
            }
        });
    }
}

// Update structure prediction visualization
function updateStructureVis(progress) {
    const structureCard = document.querySelector('.structure-card');
    const proteinModel = document.querySelector('.protein-model');
    const helices = document.querySelectorAll('.helix');
    const sheets = document.querySelectorAll('.sheet');
    
    if (!structureCard || !proteinModel || !helices.length || !sheets.length) return;
    
    // Update card status
    updateCardStatus(structureCard, progress, 50, 75);
    
    // If running or completed
    if (progress > 50) {
        // Calculate structure progress (0-100% within its phase)
        const structureProgress = Math.min(100, (progress - 50) * 4);
        
        // Show protein model based on progress
        proteinModel.style.transform = `translate(-50%, -50%) scale(${structureProgress / 100})`;
        
        // Show secondary structure elements based on progress
        helices.forEach((helix, index) => {
            const helixThreshold = (index + 1) * (100 / helices.length);
            if (structureProgress >= helixThreshold) {
                helix.style.opacity = '1';
            }
        });
        
        sheets.forEach((sheet, index) => {
            const sheetThreshold = (index + 1) * (100 / sheets.length);
            if (structureProgress >= sheetThreshold) {
                sheet.style.opacity = '1';
            }
        });
    }
}

// Update visualization step visualization
function updateVisualizationVis(progress) {
    const visualizationCard = document.querySelector('.visualization-card');
    const renderFrame = document.querySelector('.render-frame');
    const renderDots = document.querySelectorAll('.render-dot');
    
    if (!visualizationCard || !renderFrame || !renderDots.length) return;
    
    // Update card status
    updateCardStatus(visualizationCard, progress, 75, 100);
    
    // If running or completed
    if (progress > 75) {
        // Calculate visualization progress (0-100% within its phase)
        const visualizationProgress = Math.min(100, (progress - 75) * 4);
        
        // Show render frame based on progress
        renderFrame.style.opacity = '1';
        
        // Animate render dots if running
        if (progress < 100) {
            renderDots.forEach(dot => {
                dot.style.animation = 'scanLine 2s infinite alternate';
            });
        } else {
            // Stop animation when completed
            renderDots.forEach(dot => {
                dot.style.animation = 'none';
                dot.style.top = '50%';
            });
        }
    }
}

// Helper function to update card status
function updateCardStatus(card, progress, minProgress, maxProgress) {
    if (!card) return;
    
    // Remove all status classes
    card.classList.remove('pending', 'running', 'completed');
    
    // Add appropriate status class
    if (progress >= maxProgress) {
        card.classList.add('completed');
    } else if (progress > minProgress) {
        card.classList.add('running');
    } else {
        card.classList.add('pending');
    }
}
