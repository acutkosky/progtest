"""Exercise definitions for the programming diagnostic."""
from dataclasses import dataclass
from typing import Any, Optional, List, Dict, Union, Tuple

@dataclass
class TestCase:
    """A test case for a Python exercise."""
    input: Optional[List[Any]]
    output: Any
    description: str = ""

@dataclass
class Exercise:
    """An exercise definition."""
    id: int
    type: str  # 'python' or 'terminal'
    title: str
    description: str
    template: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None
    commands: Optional[List[str]] = None
    expected_output: Optional[str] = None

EXERCISES = [
    Exercise(
        id=1,
        type="python",
        title="Basic Python Operations",
        description="""Write a function that takes two numbers and returns their sum and product.
The function should return both values as a tuple.""",
        template="def calculate(a, b):\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=[2, 3], output=(5, 6), description="Basic positive numbers"),
            TestCase(input=[0, 5], output=(5, 0), description="Zero case"),
            TestCase(input=[-1, 1], output=(0, -1), description="Negative number")
        ]
    ),
    Exercise(
        id=2,
        type="python",
        title="List Comprehension",
        description="""Write a function that returns a list of squares of even numbers from 1 to 10.
The function should use a list comprehension to generate the squares.""",
        template="def squares():\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=None, output=[4, 16, 36, 64, 100], description="Squares of even numbers 1-10")
        ]
    ),
    Exercise(
        id=3,
        type="terminal",
        title="Basic Terminal Commands",
        description="""List all files in the current directory and create a new file called 'test.txt'.""",
        commands=["ls", "touch test.txt"],
        expected_output="test.txt"
    ),
    Exercise(
        id=4,
        type="python",
        title="String Manipulation",
        description="""Write a function that takes a string and returns a dictionary with the count of each character.

The function should:
- Count how many times each character appears in the string
- Return a dictionary where keys are characters and values are their counts""",
        template="def count_chars(text):\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=["hello"], output={"h": 1, "e": 1, "l": 2, "o": 1}, description="Basic string"),
            TestCase(input=["python"], output={"p": 1, "y": 1, "t": 1, "h": 1, "o": 1, "n": 1}, description="No repeating chars"),
            TestCase(input=[""], output={}, description="Empty string")
        ]
    ),
    Exercise(
        id=5,
        type="python",
        title="File Processing",
        description="""Write a function that reads a file and returns the number of lines containing a specific word.

Requirements:
- The search should be case-insensitive (e.g., 'Python', 'PYTHON', and 'python' should all match)
- The function should return the count of matching lines
- Handle file reading errors appropriately""",
        template="def count_word_occurrences(filename, word):\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=["sample.txt", "python"], output=3, description="Count Python occurrences")
        ]
    )
]

def get_exercise(exercise_id: int) -> Optional[Exercise]:
    """Get an exercise by ID."""
    return next((ex for ex in EXERCISES if ex.id == exercise_id), None) 