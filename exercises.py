"""Exercise definitions for the programming diagnostic."""
from dataclasses import dataclass, asdict
from typing import Any, Optional, List, Dict, Union, Tuple, Set

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
    summary: str  # Short description for the home page
    template: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None
    commands: Optional[List[str]] = None
    expected_command_patterns: Optional[List[str]] = None  # Patterns that should appear in the command
    expected_output_patterns: Optional[List[str]] = None   # Patterns that should appear in the output

EXERCISES = [
    Exercise(
        id=1,
        type="python",
        title="Basic Python Operations",
        summary="Write a function to calculate the sum and product of two numbers.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that takes two numbers and returns their sum and product.

The function should return both values as a tuple.</pre>""",
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
        summary="Generate a list of squares using list comprehension.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that returns a list of squares of even numbers from 1 to 10.

The function should use a list comprehension to generate the squares.</pre>""",
        template="def squares():\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=None, output=[4, 16, 36, 64, 100], description="Squares of even numbers 1-10")
        ]
    ),
    Exercise(
        id=3,
        type="terminal",
        title="Basic Terminal Commands",
        summary="Practice basic file operations using ls and touch commands.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">List all files in the current directory and create a new file called 'test.txt'.

Required steps:
1. Create a new file named 'test.txt'
2. List the contents of the current directory to verify the file was created</pre>""",
        commands=["ls", "touch test.txt", "ls"],
        expected_command_patterns=[
            "ls"
        ],
        expected_output_patterns=[
            "test.txt"
        ]
    ),
    Exercise(
        id=4,
        type="python",
        title="String Manipulation",
        summary="Create a character frequency counter for strings.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that takes a string and returns a dictionary with the count of each character.

The function should:
- Count how many times each character appears in the string
- Return a dictionary where keys are characters and values are their counts</pre>""",
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
        summary="Count occurrences of a word in a text file.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that reads a file and returns the number of lines containing a specific word.

Requirements:
- The search should be case-insensitive (e.g., 'Python', 'PYTHON', and 'python' should all match)
- The function should return the count of matching lines
- Handle file reading errors appropriately</pre>""",
        template="def count_word_occurrences(filename, word):\n    # Your code here\n    pass",
        test_cases=[
            TestCase(input=["sample.txt", "python"], output=3, description="Count Python occurrences")
        ]
    ),
    Exercise(
        id=6,
        type="terminal",
        title="Working with Text Files",
        summary="Create and search text files using echo, cat, and grep.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">In this exercise, you'll create and manipulate a text file using basic terminal commands.

Required steps:
1. Create a file named 'names.txt' containing exactly these four names, one per line:</pre>
<pre class="ascii-art">   Alice
   Bob
   Charlie
   David</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Display the contents of names.txt to verify it was created correctly
3. Use grep to find and display the line containing 'Bob'

Hint: You can use 'echo' with the -e flag and \\n for newlines to create the file in one command.</pre>""",
        commands=[
            "echo -e 'Alice\\nBob\\nCharlie\\nDavid' > names.txt",
            "cat names.txt",
            "grep 'Bob' names.txt"
        ],
        expected_command_patterns=[
            "names\\.txt",  # File name with escaped dot
            "grep.*\\bBob\\b"  # grep followed by word-bounded Bob
        ],
        expected_output_patterns=[
            "^\\s*Bob\\s*\\n*$"  # Bob on its own line, allowing for whitespace and newline
        ]
    ),
    Exercise(
        id=7,
        type="terminal",
        title="Directory Structure",
        summary="Create and navigate a web project directory structure.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Create and navigate a specific directory structure for a web project.

Required steps:
1. Create the following directory structure:</pre>
<pre class="ascii-art">   webapp/
   ├── src/
   │   ├── components/
   │   └── styles/
   └── public/</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Navigate into the components directory
3. Run pwd to verify you're in the correct location (path should end with webapp/src/components)

Commands you'll need: mkdir -p, cd, pwd</pre>""",
        commands=[
            "mkdir -p webapp/src/components webapp/src/styles webapp/public",
            "cd webapp/src/components",
            "pwd"
        ],
        expected_command_patterns=[
            "pwd"  # Must use pwd command to verify location
        ],
        expected_output_patterns=[
            "\\/home\\/pyodide\\/webapp\\/src\\/components\\n*$"  # Full path must match exactly, with optional newline at end
        ]
    ),
    Exercise(
        id=8,
        type="terminal",
        title="Script Creation and Permissions",
        summary="Create a shell script and set executable permissions.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Create a shell script and make it executable.

Required steps:
1. Create a file named 'greet.sh' with these exact contents:</pre>
<pre class="ascii-art">   #!/bin/bash
   echo "Hello, World!"</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Display the current permissions of greet.sh
3. Make the script executable (add +x permission)
4. Display the new permissions to verify the change

The final permissions should show the executable bit set for all users (chmod a+x).</pre>""",
        commands=[
            "echo -e '#!/bin/bash\\necho \"Hello, World!\"' > greet.sh",
            "ls -l greet.sh",
            "chmod a+x greet.sh",
            "ls -l greet.sh"
        ],
        expected_command_patterns=[],
        expected_output_patterns=[
            "-.*x.*x.*x.*greet\\.sh"
        ]
    ),
    Exercise(
        id=9,
        type="terminal",
        title="Text Processing Pipeline",
        summary="Process text using sort, uniq, and pipes to count duplicates.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Process a list of fruits to count duplicates using pipes.

Required steps:
1. Create a file named 'fruits.txt' with these exact contents (one fruit per line):</pre>
<pre class="ascii-art">   apple
   banana
   apple
   cherry
   banana
   date
   apple</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Use a pipeline of commands to:
   - Sort the fruits alphabetically
   - Count how many times each fruit appears
   - Show only fruits that appear more than once

The output should show the count followed by the fruit name.</pre>""",
        commands=[
            "echo -e 'apple\\nbanana\\napple\\ncherry\\nbanana\\ndate\\napple' > fruits.txt",
            "sort fruits.txt | uniq -c | sort -nr | grep -v '^ *1 '"
        ],
        expected_command_patterns=["sort", "uniq", "fruits.txt"],
        expected_output_patterns=[
            "\\s*3\\s+apple",  # Match "3 apple" with flexible spacing
            "\\s*2\\s+banana"  # Match "2 banana" with flexible spacing
        ]
    ),
    Exercise(
        id=10,
        type="terminal",
        title="File Finding and Counting",
        summary="Use find command to locate and count specific file types.",
        description="""<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Search for specific files and count them.

Required steps:
1. Create this directory structure with files:</pre>
<pre class="ascii-art">   test/
   ├── a.txt
   ├── b.txt
   ├── sub1/
   │   ├── c.txt
   │   └── d.log
   └── sub2/
       ├── e.txt
       └── f.log</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Use the find command to:
   - Find all .txt files
   - Count how many there are

The final output should show only the number of .txt files found.</pre>""",
        commands=[
            "mkdir -p test/sub1 test/sub2",
            "touch test/a.txt test/b.txt test/sub1/c.txt test/sub1/d.log test/sub2/e.txt test/sub2/f.log",
            "find test -name '*.txt' | wc -l"
        ],
        expected_command_patterns=["find", "txt"],
        expected_output_patterns=["4"]
    )
]

def get_exercise(exercise_id: int) -> Optional[Exercise]:
    """Get an exercise by ID."""
    return next((ex for ex in EXERCISES if ex.id == exercise_id), None) 