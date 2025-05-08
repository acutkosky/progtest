// Python code execution handler for static website
class PythonRunner {
    constructor(outputElement) {
        this.outputElement = outputElement;
        this.pyodideReady = false;
        this.exercisesModule = null;
        this.testRunnerModule = null;
    }

    // Initialize Pyodide and load Python modules
    async initialize() {
        try {
            this.setOutput('Initializing Python environment...');
            
            // Get the global Pyodide instance or initialize it
            if (typeof initPyodide !== 'function') {
                throw new Error("initPyodide function not found. Make sure the main.js script is properly loaded.");
            }
            
            // Get the global Pyodide instance
            window.pyodide = await initPyodide();
            if (!window.pyodide) {
                throw new Error("Failed to initialize Pyodide.");
            }
            
            // Load exercises.py
            console.log("Loading exercises.py...");
            const exercisesResponse = await fetch('./python/exercises.py');
            const exercisesCode = await exercisesResponse.text();
            
            // Load test_runner.py
            console.log("Loading test_runner.py...");
            const testRunnerResponse = await fetch('./python/test_runner.py');
            const testRunnerCode = await testRunnerResponse.text();
            
            // Set up the Python modules
            console.log("Setting up Python modules...");
            pyodide.runPython('import sys');
            pyodide.runPython('from io import StringIO');
            
            // Create exercises module
            console.log("Creating exercises module...");
            pyodide.runPython('exercises = type(sys)("exercises")');
            pyodide.runPython('sys.modules["exercises"] = exercises');
            pyodide.globals.set('exercises_code', exercisesCode);
            pyodide.runPython('exec(exercises_code, sys.modules["exercises"].__dict__)');
            this.exercisesModule = pyodide.pyimport("exercises");
            
            // Create test_runner module
            console.log("Creating test_runner module...");
            pyodide.runPython('test_runner = type(sys)("test_runner")');
            pyodide.runPython('sys.modules["test_runner"] = test_runner');
            pyodide.globals.set('test_runner_code', testRunnerCode);
            pyodide.runPython('exec(test_runner_code, sys.modules["test_runner"].__dict__)');
            this.testRunnerModule = pyodide.pyimport("test_runner");
            
            this.pyodideReady = true;
            this.setOutput('Python environment ready. Write your code and click "Run Code" to test.');
            console.log("Python environment initialized successfully!");
            return true;
        } catch (error) {
            console.error('Error initializing Python environment:', error);
            this.setOutput(`Error initializing Python environment: ${error}`);
            return false;
        }
    }

    // Run Python code and test it against test cases
    async runCode(code, exercise) {
        if (!this.pyodideReady) {
            this.setOutput('Python environment is still loading...');
            return false;
        }

        if (!exercise || !exercise.testCases) {
            this.setOutput('Invalid exercise or missing test cases');
            return false;
        }

        try {
            // Clear output
            this.setOutput('Running tests...');
            
            // Modify test cases for proper Python representation
            const testCases = this.convertTestCases(exercise.testCases);
            
            // Run tests using the test_runner module
            console.log("Running test_runner.run_tests with:", code, testCases);
            const pyResult = this.testRunnerModule.run_tests(code, testCases);
            
            // Convert Python results to JavaScript objects
            console.log("Raw Pyodide result:", pyResult);
            
            // Ensure we have a proper result by explicitly converting to JS
            let results;
            if (pyResult && typeof pyResult.toJs === 'function') {
                // Use toJs() to convert Python object to JavaScript
                results = pyResult.toJs();
                console.log("Converted results:", results);
            } else {
                console.error("Failed to get proper results from Python");
                this.setOutput('Error: Failed to process test results');
                return false;
            }
            
            // Format results
            const output = [];
            let passedTests = 0;
            
            // Process each result
            for (let i = 0; i < results.length; i++) {
                const result = results[i];
                output.push(`Test case: ${result.description}`);
                output.push(`Expected: ${result.expected}`);
                output.push(`Got: ${result.got}`);
                
                if (result.output) {
                    output.push('Output:');
                    output.push(result.output);
                }
                
                // Get the passed status directly
                let passed = result.passed;
                
                output.push(`Passed: ${passed ? 'Yes' : 'No'}`);
                output.push('---');
                
                if (passed) {
                    passedTests++;
                }
            }
            
            output.push(`\nPassed ${passedTests} out of ${results.length} tests`);
            
            // Set output
            this.setOutput(output.join('\n'));
            
            return passedTests === results.length;
        } catch (error) {
            console.error('Error running code:', error);
            this.setOutput(`Error running code: ${error}`);
            return false;
        }
    }
    
    // Convert JS test cases to Python format
    convertTestCases(testCases) {
        const pythonTestCases = [];
        
        for (const testCase of testCases) {
            // Prepare the input and output for Python
            let input = testCase.input;
            let output = testCase.output;
            
            // Convert JavaScript arrays to Python lists
            if (Array.isArray(input)) {
                // Create a properly structured input that Python will understand
                input = pyodide.toPy(input);
            }
            
            // Convert output to Python format
            if (Array.isArray(output)) {
                output = pyodide.toPy(output);
            } else if (typeof output === 'object' && output !== null) {
                // For dictionaries/objects
                output = pyodide.toPy(output);
            }
            
            // Create a Python TestCase object
            const pyTestCase = pyodide.globals.get('exercises').TestCase(
                input === null ? null : input,
                output,
                testCase.description
            );
            
            pythonTestCases.push(pyTestCase);
        }
        
        return pythonTestCases;
    }

    // Set output text
    setOutput(text) {
        if (this.outputElement) {
            this.outputElement.textContent = text;
        }
    }
}

// Create a new Python runner
function createPythonRunner(outputElementId) {
    const outputElement = document.getElementById(outputElementId);
    
    if (!outputElement) {
        console.error('Output element not found');
        return null;
    }
    
    return new PythonRunner(outputElement);
} 