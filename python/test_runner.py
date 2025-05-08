"""Test runner for Python exercises."""
import sys
import os
import tempfile
import importlib.util
from typing import Any, Tuple, List, Optional
from dataclasses import dataclass
from io import StringIO
from exercises import TestCase
import traceback

@dataclass
class TestResult:
    """Result of a test case execution."""
    description: str
    expected: Any
    got: Any
    passed: bool
    output: Optional[str] = None

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

def run_tests(code: str, test_cases: List[Any]) -> List[TestResult]:
    """
    Run the provided code against the given test cases.
    Returns a list of TestResult objects.
    """
    results = []
    
    # Create a namespace for the code execution
    namespace = {}
    
    try:
        # Execute the code to define the function
        exec(code, namespace)
    except Exception as e:
        # If there's an error in the code itself, return that for all test cases
        error_msg = f"Error in code: {str(e)}\n{traceback.format_exc()}"
        return [TestResult(
            description=tc.description,
            expected=tc.output,
            got=error_msg,
            passed=False
        ) for tc in test_cases]
    
    # Run each test case
    for tc in test_cases:
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            # Get the function - assume it's the first function defined
            for name, obj in namespace.items():
                if callable(obj) and name != 'exec' and not name.startswith('__'):
                    function = obj
                    break
            else:
                raise ValueError("No function defined in code")
            
            # Special handling for exercise 5 (file processing)
            # Create sample.txt with test content before running the test
            if function.__name__ == 'count_word_occurrences':
                with open('sample.txt', 'w') as f:
                    f.write('''Python is a great language
I love PYTHON programming
python makes coding fun
Java is another language''')
            
            # Call the function with the test inputs
            if tc.input is None:
                result = function()
            else:
                result = function(*tc.input)
            
            # Get any printed output
            output = mystdout.getvalue()
            
            # Check if the result matches the expected output
            # This is where we handle tuple vs list comparison
            passed = compare_values(result, tc.output)
            
            results.append(TestResult(
                description=tc.description,
                expected=tc.output,
                got=result,
                passed=passed,
                output=output.strip() if output.strip() else None
            ))
            
        except Exception as e:
            # Capture exceptions during function execution
            error_msg = f"Error during execution: {str(e)}\n{traceback.format_exc()}"
            results.append(TestResult(
                description=tc.description,
                expected=tc.output,
                got=error_msg,
                passed=False,
                output=mystdout.getvalue().strip() if mystdout.getvalue().strip() else None
            ))
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
            # Clean up sample.txt if it was created
            try:
                if function.__name__ == 'count_word_occurrences' and os.path.exists('sample.txt'):
                    os.remove('sample.txt')
            except:
                pass
    
    return results

def compare_values(got, expected):
    """
    Compare values with better support for Python tuples vs JavaScript arrays.
    
    This handles cases where a Python tuple like (5, 6) needs to match 
    a JavaScript array representation like [5, 6].
    """
    # Check if values are directly equal
    if got == expected:
        return True
    
    # For tuples and lists, compare their elements
    if isinstance(got, (tuple, list)) and isinstance(expected, (tuple, list)):
        if len(got) != len(expected):
            return False
        return all(compare_values(g, e) for g, e in zip(got, expected))
    
    # If the expected value is a string representation like "5,6" and 
    # the actual is a tuple/list like (5, 6) or [5, 6], try to compare them
    if isinstance(got, (tuple, list)) and isinstance(expected, str):
        # Convert "5,6" to [5, 6] for comparison
        try:
            expected_values = [int(x.strip()) if x.strip().isdigit() or (x.strip() and x.strip()[0] == '-' and x.strip()[1:].isdigit()) else x.strip() for x in expected.split(',')]
            if len(expected_values) == len(got):
                return all(compare_values(g, e) for g, e in zip(got, expected_values))
        except:
            # If any parsing error, fall back to string comparison
            return str(got) == expected
    
    # For any other types, convert to strings and compare
    try:
        return str(got).strip() == str(expected).strip()
    except:
        return False 