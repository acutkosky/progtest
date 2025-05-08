// Global state - use window namespace to avoid conflicts
window.currentExercise = null;
window.pyodide = null;
window.pythonRunner = null;
window.terminal = null;
window.editor = null;
window.exercisesLoaded = false;
window.pyodideLoading = false;

// Initialize Pyodide globally
async function initPyodide() {
    if (window.pyodide !== null) return window.pyodide; // Already loaded
    if (window.pyodideLoading) {
        // Wait for it to finish loading
        while (window.pyodide === null && window.pyodideLoading) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return window.pyodide;
    }
    
    window.pyodideLoading = true;
    console.log("Starting Pyodide initialization...");
    
    try {
        // Make sure loadPyodide function exists
        if (typeof loadPyodide !== 'function') {
            throw new Error("loadPyodide function not found. Make sure the pyodide.js script is properly loaded.");
        }
        
        window.pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
        });
        console.log("Pyodide loaded successfully!");
        
        // Optional: Load some common packages
        await window.pyodide.loadPackagesFromImports('numpy pandas');
        console.log("Pyodide packages loaded!");
        
        return window.pyodide;
    } catch (error) {
        console.error("Failed to initialize Pyodide:", error);
        alert("Failed to initialize Python environment: " + error.message);
        window.pyodide = null;
        throw error;
    } finally {
        window.pyodideLoading = false;
    }
}

// Initialize application - skip if running on exercise page with direct init
document.addEventListener('DOMContentLoaded', async function() {
    // If we're on the exercise page with direct initialization, skip our init
    if (document.getElementById('loading-overlay')) {
        console.log("Skipping main.js initialization - using direct exercise page init");
        return;
    }
    
    // Set up tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Pyodide globally
    try {
        await initPyodide();
    } catch (error) {
        console.error("Could not initialize Pyodide:", error);
    }
    
    // Load exercises
    if (typeof getAllExercises === 'function') {
        window.exercisesLoaded = true;
    }
    
    // Check if we're on the index page or exercise page
    if (document.getElementById('exercises-container')) {
        // Index page - populate exercises
        populateExercises();
    } else if (document.getElementById('exercise-container')) {
        // Exercise page - load the specific exercise
        const urlParams = new URLSearchParams(window.location.search);
        const exerciseId = parseInt(urlParams.get('id'));
        
        if (!isNaN(exerciseId)) {
            loadExercise(exerciseId);
        } else {
            showError('Invalid exercise ID');
        }
    }
});

// Populate the exercises grid on the index page
function populateExercises() {
    if (!window.exercisesLoaded) {
        showError('Failed to load exercises');
        return;
    }
    
    const exercises = getAllExercises();
    const container = document.getElementById('exercises-container');
    
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Create a row
    const row = document.createElement('div');
    row.className = 'row mt-5';
    
    // Add each exercise
    exercises.forEach(exercise => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-4';
        
        col.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">Exercise ${exercise.id}: ${exercise.title}</h5>
                    <p class="card-text">${exercise.summary}</p>
                    <a href="exercise.html?id=${exercise.id}" class="btn btn-primary">Start Exercise</a>
                </div>
            </div>
        `;
        
        row.appendChild(col);
    });
    
    container.appendChild(row);
}

// Load a specific exercise
async function loadExercise(exerciseId) {
    if (!window.exercisesLoaded) {
        showError('Failed to load exercises');
        return;
    }
    
    // Get exercise data
    window.currentExercise = getExercise(exerciseId);
    
    if (!window.currentExercise) {
        showError('Exercise not found');
        return;
    }
    
    // Update page title and description
    document.getElementById('exercise-title').textContent = window.currentExercise.title;
    document.getElementById('exercise-description').innerHTML = window.currentExercise.description;
    
    // Set up based on exercise type
    if (window.currentExercise.type === 'python') {
        setupPythonExercise();
    } else if (window.currentExercise.type === 'terminal') {
        setupTerminalExercise();
    }
}

// Set up Python code exercise
async function setupPythonExercise() {
    const codeEditor = document.getElementById('code-editor');
    const outputElement = document.getElementById('output');
    
    if (!codeEditor || !outputElement) {
        showError('Missing required elements for Python exercise');
        return;
    }
    
    // Set template code
    codeEditor.value = window.currentExercise.template || '';
    
    // Initialize CodeMirror
    window.editor = CodeMirror.fromTextArea(codeEditor, {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true
    });
    
    // Initialize Python runner
    window.pythonRunner = createPythonRunner('output');
    await window.pythonRunner.initialize();
    
    // Set up run button
    const runButton = document.getElementById('run-button');
    if (runButton) {
        runButton.addEventListener('click', runPythonCode);
    }
}

// Run Python code for current exercise
async function runPythonCode() {
    if (!window.editor || !window.pythonRunner) {
        showError('Python environment not initialized');
        return;
    }
    
    const code = window.editor.getValue();
    await window.pythonRunner.runCode(code, window.currentExercise);
}

// Set up terminal exercise
async function setupTerminalExercise() {
    const terminalOutput = document.getElementById('terminal-output');
    const terminalInput = document.getElementById('terminal-input');
    
    if (!terminalOutput || !terminalInput) {
        showError('Missing required elements for terminal exercise');
        return;
    }
    
    // Create terminal
    window.terminal = createTerminal('terminal-output', 'terminal-input');
    
    // Set status callback to check exercise completion
    window.terminal.setStatusCallback(checkTerminalExerciseStatus);
    
    // Initialize terminal
    await window.terminal.initialize();
}

// Check terminal exercise status after each command
function checkTerminalExerciseStatus(command) {
    if (!window.terminal || !window.currentExercise) return;
    
    const isComplete = window.terminal.checkExerciseCompletion(window.currentExercise);
    const statusElement = document.getElementById('exercise-status');
    
    if (statusElement) {
        if (isComplete) {
            statusElement.innerHTML = '<span class="badge bg-success">Completed</span>';
        } else {
            statusElement.innerHTML = '<span class="badge bg-primary">In Progress</span>';
        }
    }
}

// Utility functions
function showError(message) {
    console.error(message);
    alert(message);
}

function showSuccess(message) {
    alert(message);
} 