// Terminal interface for the static website
class TerminalInterface {
    constructor(outputElement, inputElement) {
        this.outputElement = outputElement;
        this.inputElement = inputElement;
        this.pyodideReady = false;
        this.terminalModule = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.statusCallback = null;
        this.exerciseCompleted = false; // Track if exercise was already completed
    }

    // Initialize Pyodide and load terminal.py
    async initialize() {
        try {
            // Add loading message
            this.addOutputLine('Loading terminal environment...', 'text-info');
            
            // Get the global Pyodide instance
            if (typeof initPyodide !== 'function') {
                throw new Error("initPyodide function not found. Make sure the main.js script is properly loaded.");
            }
            
            window.pyodide = await initPyodide();
            if (!window.pyodide) {
                throw new Error("Failed to initialize Pyodide.");
            }
            
            // Load the terminal.py module
            console.log("Loading terminal.py...");
            const response = await fetch('./python/terminal.py');
            const terminalCode = await response.text();
            
            // Create terminal module in Python
            console.log("Creating terminal module...");
            pyodide.runPython('import sys');
            pyodide.runPython('from io import StringIO');
            pyodide.runPython('import os');
            pyodide.runPython('terminal = type(sys)("terminal")');
            pyodide.runPython('sys.modules["terminal"] = terminal');
            
            // Add terminal code to module
            pyodide.globals.set('terminal_code', terminalCode);
            pyodide.runPython('exec(terminal_code, sys.modules["terminal"].__dict__)');
            
            // Import terminal module
            this.terminalModule = pyodide.pyimport("terminal");
            
            this.pyodideReady = true;
            this.addOutputLine('Terminal ready. Enter commands to begin.', 'text-success');
            console.log("Terminal environment initialized successfully!");
            return true;
        } catch (error) {
            console.error('Error loading terminal:', error);
            this.addOutputLine(`Error initializing terminal: ${error}`, 'text-danger');
            return false;
        }
    }

    // Add a line to the terminal output
    addOutputLine(text, className = '') {
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        line.textContent = text;
        this.outputElement.appendChild(line);
        this.outputElement.scrollTop = this.outputElement.scrollHeight;
    }

    // Execute a terminal command
    async executeCommand(command) {
        if (!this.pyodideReady) {
            this.addOutputLine('Terminal environment is still loading...', 'text-warning');
            return false;
        }

        if (!command.trim()) {
            return true;
        }

        // Add to command history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;

        // Add command to output
        this.addOutputLine(`$ ${command}`, 'text-primary');

        try {
            // Execute command via Pyodide
            const output = this.terminalModule.execute_command(command);
            
            // Display output
            if (output && output.trim()) {
                const lines = output.split('\n');
                lines.forEach(line => this.addOutputLine(line));
            }

            // Add a small delay before checking status to ensure output is rendered
            setTimeout(() => {
                if (this.statusCallback) {
                    this.statusCallback(command);
                }
            }, 50);

            return true;
        } catch (error) {
            // Instead of showing the Python error, display a more user-friendly error
            console.error('Command execution error:', error);
            
            // Extract the command name from the input
            const cmdName = command.trim().split(/\s+/)[0];
            
            // Format a Unix-like error message based on the error type
            if (error.message && error.message.includes('No such file or directory')) {
                // Extract the filename if possible
                const args = command.trim().split(/\s+/).slice(1);
                const filename = args.find(arg => !arg.startsWith('-')) || 'file';
                this.addOutputLine(`${cmdName}: ${filename}: No such file or directory`, 'text-danger');
            } else if (error.message && error.message.includes('Permission denied')) {
                this.addOutputLine(`${cmdName}: Permission denied`, 'text-danger');
            } else if (error.message && error.message.includes('command not found')) {
                this.addOutputLine(`${cmdName}: command not found`, 'text-danger');
            } else {
                // Generic error message that mimics Unix-style errors
                this.addOutputLine(`${cmdName}: error: ${error.message || 'Command failed'}`, 'text-danger');
            }
            
            return false;
        }
    }

    // Check if a terminal exercise is complete
    checkExerciseCompletion(exercise) {
        if (!exercise || exercise.type !== 'terminal') {
            return false;
        }

        try {
            // For Exercise 3, we only want to check completion on 'ls' commands
            const mostRecentCommand = this.commandHistory[this.commandHistory.length - 1] || "";
            
            // If this isn't an 'ls' command, don't check for completion
            if (exercise.id === 3 && !mostRecentCommand.match(/\bls\b/i)) {
                return false;
            }
            
            // Get the terminal output content
            const terminalLines = Array.from(this.outputElement.children).map(el => el.textContent.toLowerCase());
            
            // Find the last command's output
            let commandIndex = -1;
            for (let i = terminalLines.length - 1; i >= 0; i--) {
                if (terminalLines[i].startsWith('$ ' + mostRecentCommand.toLowerCase())) {
                    commandIndex = i;
                    break;
                }
            }
            
            // If we couldn't find the command line, don't proceed
            if (commandIndex === -1) {
                console.log("Couldn't find the most recent command in the terminal output");
                return false;
            }
            
            // Get only the output lines that follow the most recent command
            const recentOutputLines = terminalLines.slice(commandIndex + 1);
            
            // Find where the next command starts (if any)
            let nextCommandIndex = recentOutputLines.findIndex(line => line.startsWith('$ '));
            if (nextCommandIndex === -1) {
                // No next command, use all lines
                nextCommandIndex = recentOutputLines.length;
            }
            
            // Get just the output between this command and the next one
            const commandOutput = recentOutputLines.slice(0, nextCommandIndex).join('\n');
            
            console.log("Most recent command:", mostRecentCommand);
            console.log("Command output:", commandOutput);
            
            // Check if the most recent command matches the expected pattern
            const commandPatterns = exercise.expectedCommandPatterns || [];
            const commandMatches = commandPatterns.length === 0 || 
                commandPatterns.some(pattern => {
                    const regex = new RegExp(pattern, 'i');
                    const matches = regex.test(mostRecentCommand);
                    console.log(`Command pattern '${pattern}' matches recent command: ${matches}`);
                    return matches;
                });
            
            // Check if the output of the most recent command contains the expected pattern
            const outputPatterns = exercise.expectedOutputPatterns || [];
            const outputMatches = outputPatterns.length === 0 || 
                outputPatterns.every(pattern => {
                    const regex = new RegExp(pattern, 'i');
                    const matches = regex.test(commandOutput);
                    console.log(`Output pattern '${pattern}' matches command output: ${matches}`);
                    return matches;
                });
            
            // Exercise is complete if both the command and output match
            const isComplete = commandMatches && outputMatches;
            console.log(`Exercise completion: command matches = ${commandMatches}, output matches = ${outputMatches}, isComplete = ${isComplete}`);
            
            // Display success message if newly completed
            if (isComplete && !this.exerciseCompleted) {
                this.exerciseCompleted = true;
                this.addOutputLine('', '');
                this.addOutputLine('🎉 Exercise completed successfully! 🎉', 'text-success');
            }
            
            return isComplete;
        } catch (error) {
            console.error('Error checking exercise completion:', error);
            return false;
        }
    }

    // Set status change callback
    setStatusCallback(callback) {
        this.statusCallback = callback;
    }

    // Handle keyboard navigation (up/down arrows for history)
    handleKeyDown(event) {
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            if (this.historyIndex > 0) {
                this.historyIndex--;
                this.inputElement.value = this.commandHistory[this.historyIndex];
            }
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
                this.inputElement.value = this.commandHistory[this.historyIndex];
            } else {
                this.historyIndex = this.commandHistory.length;
                this.inputElement.value = '';
            }
        } else if (event.key === 'Enter') {
            event.preventDefault();
            const command = this.inputElement.value;
            this.executeCommand(command);
            this.inputElement.value = '';
        }
    }

    // Set up the terminal for specific exercises
    setupExercise(exercise) {
        if (!exercise || !this.pyodideReady) {
            return false;
        }

        try {
            // Exercise-specific setup
            switch (exercise.id) {
                case 9:
                    // Text Processing Pipeline exercise - Create words.txt automatically
                    console.log("Setting up Exercise 9 - Creating words.txt");
                    this.addOutputLine("Creating words.txt for this exercise...", "text-info");
                    
                    // Create the file directly using Python with explicit list for better control
                    const pythonCode = `
# Define the words as a list to ensure proper formatting
words = [
    "apple",
    "banana",
    "apple",
    "cherry",
    "banana",
    "apple",
    "date",
    "cherry"
]

# Write each word on its own line with proper line endings
with open('words.txt', 'w') as f:
    for i, word in enumerate(words):
        f.write(word)
        # Ensure every line has a newline, even the last one
        f.write('\\n')
`;
                    pyodide.runPython(pythonCode);
                    
                    this.addOutputLine("File words.txt has been created. You can proceed with the exercise.", "text-success");
                    break;
                
                default:
                    // No special setup for other exercises
                    break;
            }
            return true;
        } catch (error) {
            console.error('Error setting up exercise:', error);
            this.addOutputLine(`Error setting up exercise: ${error}`, 'text-danger');
            return false;
        }
    }
}

// Function to create a new terminal instance
function createTerminal(outputElementId, inputElementId) {
    const outputElement = document.getElementById(outputElementId);
    const inputElement = document.getElementById(inputElementId);
    
    if (!outputElement || !inputElement) {
        console.error('Terminal elements not found');
        return null;
    }
    
    const terminal = new TerminalInterface(outputElement, inputElement);
    
    // Set up event handlers
    inputElement.addEventListener('keydown', (event) => {
        terminal.handleKeyDown(event);
    });
    
    return terminal;
} 