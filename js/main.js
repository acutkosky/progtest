// Global state
let currentExercise = null;
let pyodide = null;
let pythonRunner = null;
let terminal = null;
let editor = null;
let exercisesLoaded = false;

// Initialize application
document.addEventListener('DOMContentLoaded', async function() {
    // Set up tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Load exercises
    if (typeof getAllExercises === 'function') {
        exercisesLoaded = true;
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
    if (!exercisesLoaded) {
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
    if (!exercisesLoaded) {
        showError('Failed to load exercises');
        return;
    }
    
    // Get exercise data
    currentExercise = getExercise(exerciseId);
    
    if (!currentExercise) {
        showError('Exercise not found');
        return;
    }
    
    // Update page title and description
    document.getElementById('exercise-title').textContent = currentExercise.title;
    document.getElementById('exercise-description').innerHTML = currentExercise.description;
    
    // Set up based on exercise type
    if (currentExercise.type === 'python') {
        setupPythonExercise();
    } else if (currentExercise.type === 'terminal') {
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
    codeEditor.value = currentExercise.template || '';
    
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(codeEditor, {
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
    pythonRunner = createPythonRunner('output');
    await pythonRunner.initialize();
    
    // Set up run button
    const runButton = document.getElementById('run-button');
    if (runButton) {
        runButton.addEventListener('click', runPythonCode);
    }
}

// Run Python code for current exercise
async function runPythonCode() {
    if (!editor || !pythonRunner) {
        showError('Python environment not initialized');
        return;
    }
    
    const code = editor.getValue();
    await pythonRunner.runCode(code, currentExercise);
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
    terminal = createTerminal('terminal-output', 'terminal-input');
    
    // Set status callback to check exercise completion
    terminal.setStatusCallback(checkTerminalExerciseStatus);
    
    // Initialize terminal
    await terminal.initialize();
}

// Check terminal exercise status after each command
function checkTerminalExerciseStatus(command) {
    if (!terminal || !currentExercise) return;
    
    const isComplete = terminal.checkExerciseCompletion(currentExercise);
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