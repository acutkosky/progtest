from flask import Flask, render_template, request, jsonify
import os
import subprocess
import tempfile
import json

app = Flask(__name__)

# Exercise definitions
EXERCISES = [
    {
        "id": 1,
        "type": "python",
        "title": "Basic Python Operations",
        "description": """Write a function that takes two numbers and returns their sum and product.
The function should return both values as a tuple.""",
        "template": "def calculate(a, b):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": [2, 3], "output": (5, 6)},
            {"input": [0, 5], "output": (5, 0)},
            {"input": [-1, 1], "output": (0, -1)}
        ]
    },
    {
        "id": 2,
        "type": "python",
        "title": "List Comprehension",
        "description": """Write a function that returns a list of squares of even numbers from 1 to 10.
The function should use a list comprehension to generate the squares.""",
        "template": "def squares():\n    # Your code here\n    pass",
        "test_cases": [
            {"input": None, "output": [4, 16, 36, 64, 100]}
        ]
    },
    {
        "id": 3,
        "type": "terminal",
        "title": "Basic Terminal Commands",
        "description": """List all files in the current directory and create a new file called 'test.txt'.

You can use the following commands:
- ls: to list files
- touch: to create a new file""",
        "commands": ["ls", "touch test.txt"],
        "expected_output": "test.txt"
    },
    {
        "id": 4,
        "type": "python",
        "title": "String Manipulation",
        "description": """Write a function that takes a string and returns a dictionary with the count of each character.

The function should:
- Count how many times each character appears in the string
- Return a dictionary where keys are characters and values are their counts""",
        "template": "def count_chars(text):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": ["hello"], "output": {"h": 1, "e": 1, "l": 2, "o": 1}},
            {"input": ["python"], "output": {"p": 1, "y": 1, "t": 1, "h": 1, "o": 1, "n": 1}},
            {"input": [""], "output": {}}
        ]
    },
    {
        "id": 5,
        "type": "python",
        "title": "File Processing",
        "description": """Write a function that reads a file and returns the number of lines containing a specific word.

Requirements:
- The search should be case-insensitive (e.g., 'Python', 'PYTHON', and 'python' should all match)
- The function should return the count of matching lines
- Handle file reading errors appropriately""",
        "template": "def count_word_occurrences(filename, word):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": ["sample.txt", "python"], "output": 3}
        ]
    },
    {
        "id": 6,
        "type": "terminal",
        "title": "File System Navigation",
        "description": """Create a project structure for a Python application.

Steps:
1. Create a directory called 'project'
2. Inside 'project', create two subdirectories: 'src' and 'tests'
3. Navigate into the 'project' directory
4. Create a file 'main.py' in the 'src' directory with the content: print('Hello, World!')

Available commands:
- mkdir: create directories
- cd: change directory
- echo: print text
- >: redirect output to a file""",
        "commands": ["mkdir -p project/src project/tests", "cd project", "echo 'print(\"Hello, World!\")' > src/main.py"],
        "expected_output": "Hello, World!"
    },
    {
        "id": 7,
        "type": "python",
        "title": "Regular Expressions",
        "description": """Write a function that validates if a string is a valid email address.

Requirements:
- The email should have a valid format (e.g., user@domain.com)
- The domain should have at least one dot
- The function should return True for valid emails and False for invalid ones""",
        "template": "def is_valid_email(email):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": ["user@example.com"], "output": True},
            {"input": ["invalid.email"], "output": False},
            {"input": ["name.surname@domain.co.uk"], "output": True}
        ]
    },
    {
        "id": 8,
        "type": "terminal",
        "title": "Text Processing",
        "description": """Create a file with multiple lines and use grep to find specific content.

Steps:
1. Create a file called 'python.txt' with multiple lines about Python
2. Use grep to find lines containing the word 'awesome'

Available commands:
- echo: create file content
- >: redirect output to a file
- grep: search for text patterns""",
        "commands": [
            "echo 'Python is awesome\nPython is fun\nPython is powerful' > python.txt",
            "grep 'awesome' python.txt"
        ],
        "expected_output": "awesome"
    },
    {
        "id": 9,
        "type": "python",
        "title": "Data Structures",
        "description": """Implement a function that finds the most common element in a list.

Requirements:
- The function should return the element that appears most frequently
- If there's a tie, return the first element that reaches that count
- The function should work with both numbers and strings""",
        "template": "def most_common(lst):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 2, 3, 2, 4]], "output": 2},
            {"input": [['a', 'b', 'a', 'c', 'a']], "output": 'a'},
            {"input": [[1, 1, 2, 2]], "output": 1}
        ]
    },
    {
        "id": 10,
        "type": "terminal",
        "title": "Advanced File Operations",
        "description": """Create a backup of a file and verify its contents.

Steps:
1. Create a file called 'data.txt' with some content
2. Make a backup copy of the file
3. Verify that both files have identical content

Available commands:
- echo: create file content
- cp: copy files
- diff: compare files""",
        "commands": [
            "echo 'Important data' > data.txt",
            "cp data.txt data.txt.bak",
            "diff data.txt data.txt.bak"
        ],
        "expected_output": "data.txt.bak"
    }
]

@app.route('/')
def index():
    return render_template('index.html', exercises=EXERCISES)

@app.route('/exercise/<int:exercise_id>')
def exercise(exercise_id):
    exercise = next((ex for ex in EXERCISES if ex["id"] == exercise_id), None)
    if exercise:
        return render_template('exercise.html', exercise=exercise)
    return "Exercise not found", 404

@app.route('/submit/terminal', methods=['POST'])
def submit_terminal():
    data = request.json
    command = data.get('command')
    
    try:
        result = subprocess.run(command, 
                              shell=True,
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        return jsonify({
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=8080) 