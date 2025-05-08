// JavaScript representation of exercises from exercises.py
const EXERCISES = [
    {
        id: 1,
        type: "python",
        title: "Basic Python Operations",
        summary: "Write a function to calculate the sum and product of two numbers.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that takes two numbers and returns their sum and product.

The function should return both values as a tuple.</pre>`,
        template: "def calculate(a, b):\n    # Your code here\n    pass",
        testCases: [
            { input: [2, 3], output: [5, 6], description: "Basic positive numbers" },
            { input: [0, 5], output: [5, 0], description: "Zero case" },
            { input: [-1, 1], output: [0, -1], description: "Negative number" }
        ]
    },
    {
        id: 2,
        type: "python",
        title: "List Comprehension",
        summary: "Generate a list of squares using list comprehension.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that returns a list of squares of even numbers from 1 to 10.

The function should use a list comprehension to generate the squares.</pre>`,
        template: "def squares():\n    # Your code here\n    pass",
        testCases: [
            { input: null, output: [4, 16, 36, 64, 100], description: "Squares of even numbers 1-10" }
        ]
    },
    {
        id: 3,
        type: "terminal",
        title: "Basic Terminal Commands",
        summary: "Practice basic file operations using ls and touch commands.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">List all files in the current directory and create a new file called 'test.txt'.

Required steps:
1. Create a new file named 'test.txt'
2. List the contents of the current directory to verify the file was created</pre>`,
        commands: ["ls", "touch test.txt", "ls"],
        expectedCommandPatterns: ["ls"],
        expectedOutputPatterns: ["test.txt"]
    },
    {
        id: 4,
        type: "python",
        title: "String Manipulation",
        summary: "Create a character frequency counter for strings.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that takes a string and returns a dictionary with the count of each character.

The function should:
- Count how many times each character appears in the string
- Return a dictionary where keys are characters and values are their counts</pre>`,
        template: "def count_chars(text):\n    # Your code here\n    pass",
        testCases: [
            { input: ["hello"], output: {"h": 1, "e": 1, "l": 2, "o": 1}, description: "Basic string" },
            { input: ["python"], output: {"p": 1, "y": 1, "t": 1, "h": 1, "o": 1, "n": 1}, description: "No repeating chars" },
            { input: [""], output: {}, description: "Empty string" }
        ]
    },
    {
        id: 5,
        type: "python",
        title: "File Processing",
        summary: "Count occurrences of a word in a text file.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Write a function that reads a file and returns the number of lines containing a specific word.

Requirements:
- The search should be case-insensitive (e.g., 'Python', 'PYTHON', and 'python' should all match)
- The function should return the count of matching lines
- Handle file reading errors appropriately</pre>`,
        template: "def count_word_occurrences(filename, word):\n    # Your code here\n    pass",
        testCases: [
            { input: ["sample.txt", "python"], output: 3, description: "Count Python occurrences" }
        ]
    },
    {
        id: 6,
        type: "terminal",
        title: "Working with Text Files",
        summary: "Create and search text files using echo, cat, and grep.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">In this exercise, you'll create and manipulate a text file using basic terminal commands.

Required steps:
1. Create a file named 'names.txt' containing exactly these four names, one per line:</pre>
<pre class="ascii-art">   Alice
   Bob
   Charlie
   David</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Display the contents of names.txt to verify it was created correctly
3. Use grep to find and display the line containing 'Bob'

Hint: You can use 'echo' with the -e flag and \\n for newlines to create the file in one command.</pre>`,
        commands: [
            "echo -e 'Alice\\nBob\\nCharlie\\nDavid' > names.txt",
            "cat names.txt",
            "grep 'Bob' names.txt"
        ],
        expectedCommandPatterns: [
            "names\\.txt",
            "grep.*\\bBob\\b"
        ],
        expectedOutputPatterns: [
            "^\\s*Bob\\s*\\n*$"
        ]
    },
    {
        id: 7,
        type: "terminal",
        title: "Directory Structure",
        summary: "Create and navigate a web project directory structure.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Create and navigate a specific directory structure for a web project.

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

Commands you'll need: mkdir -p, cd, pwd</pre>`,
        commands: [
            "mkdir -p webapp/src/components webapp/src/styles webapp/public",
            "cd webapp/src/components",
            "pwd"
        ],
        expectedCommandPatterns: [
            "pwd"
        ],
        expectedOutputPatterns: [
            "\\/webapp\\/src\\/components\\n*$"
        ]
    },
    {
        id: 8,
        type: "terminal",
        title: "Script Creation and Permissions",
        summary: "Create a shell script and set executable permissions.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Create a shell script and make it executable.

Required steps:
1. Create a file named 'greet.sh' with these exact contents:</pre>
<pre class="ascii-art">   #!/bin/bash
   echo "Hello, World!"</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Display the current permissions of greet.sh
3. Make the script executable (add +x permission)
4. Display the new permissions to verify the change

The final permissions should show the executable bit set for all users (chmod a+x).</pre>`,
        commands: [
            "echo -e '#!/bin/bash\\necho \"Hello, World!\"' > greet.sh",
            "ls -l greet.sh",
            "chmod a+x greet.sh",
            "ls -l greet.sh"
        ],
        expectedCommandPatterns: [],
        expectedOutputPatterns: [
            "-.*x.*x.*x.*greet\\.sh"
        ]
    },
    {
        id: 9,
        type: "terminal",
        title: "Text Processing Pipeline",
        summary: "Process text using sort, uniq, and pipes to count duplicates.",
        description: `<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">Use text processing commands to analyze the frequency of words.

Required steps:
1. Create a file named 'words.txt' containing the following words, one per line:</pre>
<pre class="ascii-art">   apple
   banana
   apple
   cherry
   banana
   apple
   date
   cherry</pre>
<pre class="exercise-description" style="white-space: pre-wrap; font-family: inherit;">
2. Use a pipeline of commands (sort | uniq -c) to count the occurrences of each word
3. The output should show the word frequency in ascending order

Expected output should show apple appears 3 times, banana 2 times, cherry 2 times, and date 1 time.</pre>`,
        commands: [
            "echo -e 'apple\\nbanana\\napple\\ncherry\\nbanana\\napple\\ndate\\ncherry' > words.txt",
            "sort words.txt | uniq -c | sort -n"
        ],
        expectedCommandPatterns: [
            "sort.*\\|.*uniq.*-c"
        ],
        expectedOutputPatterns: [
            ".*1.*date",
            ".*2.*banana",
            ".*2.*cherry",
            ".*3.*apple"
        ]
    }
];

// Function to get a specific exercise by ID
function getExercise(exerciseId) {
    return EXERCISES.find(exercise => exercise.id === exerciseId);
}

// Function to get all exercises
function getAllExercises() {
    return EXERCISES;
} 