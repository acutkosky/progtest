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
    }

    // Initialize Pyodide and load terminal.py
    async initialize() {
        try {
            // Add loading message
            this.addOutputLine('Loading terminal environment...', 'text-info');
            
            // Load Pyodide if not already loaded
            if (!window.pyodide) {
                window.pyodide = await loadPyodide();
                await pyodide.loadPackagesFromImports('numpy pandas');
            }
            
            // Load the terminal.py module
            const response = await fetch('/python/terminal.py');
            const terminalCode = await response.text();
            
            // Create terminal module in Python
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

            // Notify status change if callback is set
            if (this.statusCallback) {
                this.statusCallback(command);
            }

            return true;
        } catch (error) {
            console.error('Command execution error:', error);
            this.addOutputLine(`Error executing command: ${error}`, 'text-danger');
            return false;
        }
    }

    // Check if a terminal exercise is complete
    checkExerciseCompletion(exercise) {
        if (!exercise || exercise.type !== 'terminal') {
            return false;
        }

        try {
            // For demonstration purposes, assume the exercise is complete if all expected commands
            // have been run. In a real implementation, you'd check against the patterns.
            // This is simplified since we can't easily access the filesystem state from JS.
            const commandsHistory = this.commandHistory.join('\n').toLowerCase();
            const requiredCommands = exercise.expectedCommandPatterns || [];
            
            // Check if all required command patterns are in history
            return requiredCommands.every(pattern => {
                const regex = new RegExp(pattern, 'i');
                return regex.test(commandsHistory);
            });
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