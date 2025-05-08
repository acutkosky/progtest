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
            // Load Pyodide if not already loaded
            if (!window.pyodide) {
                window.pyodide = await loadPyodide();
                await pyodide.loadPackagesFromImports('numpy pandas');
            }
            
            // Load exercises.py
            const exercisesResponse = await fetch('/python/exercises.py');
            const exercisesCode = await exercisesResponse.text();
            
            // Load test_runner.py
            const testRunnerResponse = await fetch('/python/test_runner.py');
            const testRunnerCode = await testRunnerResponse.text();
            
            // Set up the Python modules
            pyodide.runPython('import sys');
            pyodide.runPython('from io import StringIO');
            
            // Create exercises module
            pyodide.runPython('exercises = type(sys)("exercises")');
            pyodide.runPython('sys.modules["exercises"] = exercises');
            pyodide.globals.set('exercises_code', exercisesCode);
            pyodide.runPython('exec(exercises_code, sys.modules["exercises"].__dict__)');
            this.exercisesModule = pyodide.pyimport("exercises");
            
            // Create test_runner module
            pyodide.runPython('test_runner = type(sys)("test_runner")');
            pyodide.runPython('sys.modules["test_runner"] = test_runner');
            pyodide.globals.set('test_runner_code', testRunnerCode);
            pyodide.runPython('exec(test_runner_code, sys.modules["test_runner"].__dict__)');
            this.testRunnerModule = pyodide.pyimport("test_runner");
            
            this.pyodideReady = true;
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
            
            // Convert JS test cases to Python format
            const testCases = this.convertTestCases(exercise.testCases);
            
            // Run tests using the test_runner module
            const results = this.testRunnerModule.run_tests(code, testCases);
            
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
                
                output.push(`Passed: ${result.passed ? 'Yes' : 'No'}`);
                output.push('---');
                
                if (result.passed) {
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
            // Create a Python TestCase object
            const pyTestCase = pyodide.globals.get('exercises').TestCase(
                testCase.input === null ? null : testCase.input,
                testCase.output,
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