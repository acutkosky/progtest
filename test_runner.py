"""Test runner for Python exercises."""
import sys
import os
import tempfile
import importlib.util
from typing import Any, Tuple, List
from dataclasses import dataclass
from io import StringIO
from exercises import TestCase

@dataclass
class TestResult:
    """Result of a single test case."""
    passed: bool
    expected: Any
    got: Any
    output: str
    description: str

def create_temp_module(code: str) -> Tuple[str, str]:
    """Create a temporary Python module from the given code.
    
    Returns:
        Tuple of (module_name, module_path)
    """
    # Create a temporary file with the code
    fd, path = tempfile.mkstemp(suffix='.py', prefix='exercise_')
    with os.fdopen(fd, 'w') as f:
        f.write(code)
    
    # Get the module name from the file name
    module_name = os.path.splitext(os.path.basename(path))[0]
    return module_name, path

def import_temp_module(module_name: str, module_path: str) -> Any:
    """Import a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load module {module_name} from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_test_case(module: Any, function_name: str, test_case: 'TestCase') -> TestResult:
    """Run a single test case and return the result."""
    # Capture stdout
    stdout = StringIO()
    original_stdout = sys.stdout
    sys.stdout = stdout
    
    try:
        # Get the function from the module
        func = getattr(module, function_name)
        
        # Special handling for exercise 5 (file processing)
        if function_name == 'count_word_occurrences':
            # Create sample.txt with test content
            with open('sample.txt', 'w') as f:
                f.write('''Python is a great language
I love PYTHON programming
python makes coding fun
Java is another language''')
        
        # Run the test
        if test_case.input is None:
            result = func()
        else:
            result = func(*test_case.input)
            
        # Compare results
        if isinstance(result, dict) and isinstance(test_case.output, dict):
            passed = result == test_case.output
        elif isinstance(result, (list, tuple)) and isinstance(test_case.output, (list, tuple)):
            passed = tuple(result) == tuple(test_case.output)
        else:
            passed = result == test_case.output
            
        return TestResult(
            passed=passed,
            expected=test_case.output,
            got=result,
            output=stdout.getvalue(),
            description=test_case.description
        )
        
    except Exception as e:
        return TestResult(
            passed=False,
            expected=test_case.output,
            got=f"Error: {str(e)}",
            output=stdout.getvalue(),
            description=test_case.description
        )
    finally:
        sys.stdout = original_stdout
        # Clean up sample.txt if it was created
        if function_name == 'count_word_occurrences' and os.path.exists('sample.txt'):
            os.remove('sample.txt')

def run_tests(code: str, test_cases: List['TestCase'], function_name: str = None) -> List[TestResult]:
    """Run all test cases for a given piece of code.
    
    Args:
        code: The Python code to test
        test_cases: List of TestCase objects
        function_name: Name of the function to test (if None, extracted from code)
    
    Returns:
        List of TestResult objects
    """
    # Extract function name from code if not provided
    if not function_name:
        import re
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if not match:
            raise ValueError("Could not find function definition in code")
        function_name = match.group(1)
    
    # Create and import temporary module
    module_name, module_path = create_temp_module(code)
    try:
        module = import_temp_module(module_name, module_path)
        # Run all test cases
        results = [run_test_case(module, function_name, test_case) 
                  for test_case in test_cases]
        return results
    finally:
        # Clean up temporary file
        os.unlink(module_path) 