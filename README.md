# Python/Terminal Diagnostic Test

A static web application for Python programming and terminal command exercises, designed to be hosted on GitHub Pages.

## Features

- Python coding exercises with automated testing
- Terminal command exercises for practicing shell commands
- Browser-based execution using Pyodide
- No server required - runs entirely in the browser
- Mobile-friendly responsive design

## How It Works

- Python code is executed in the browser using [Pyodide](https://pyodide.org/)
- Terminal commands are simulated using a Python-based virtual file system
- All exercise definitions are stored in JavaScript

## Development

To run the site locally:

1. Clone the repository
2. Serve the files using any static file server:
   ```
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in your browser

## Modifying Exercises

The exercises are defined in `js/exercises.js`. You can modify existing exercises or add new ones by following the format:

```javascript
{
    id: 10,  // Unique ID
    type: "python", // 'python' or 'terminal'
    title: "Exercise Title",
    summary: "Short description for the home page",
    description: "Detailed HTML description",
    template: "def function():\n    pass", // Template code for Python exercises
    testCases: [
        { input: [arg1, arg2], output: expectedOutput, description: "Test description" }
    ],
    // For terminal exercises
    commands: ["command1", "command2"],
    expectedCommandPatterns: ["pattern1", "pattern2"], 
    expectedOutputPatterns: ["pattern1", "pattern2"]
}
```

## Adding Python Files

If you need to add or modify the Python backend files:

1. Add your Python files to the `python/` directory
2. Update the relevant JavaScript files to load and use your Python code

## GitHub Pages Deployment

The site is automatically deployed to GitHub Pages using the workflow in `.github/workflows/github-pages.yml`. When you push to the main branch, GitHub Actions will build and deploy the site.

## Credits

This project was migrated from a Flask application to a static GitHub Pages site. It uses:

- [Pyodide](https://pyodide.org/) for Python execution in the browser
- [Bootstrap](https://getbootstrap.com/) for UI components
- [CodeMirror](https://codemirror.net/) for the code editor 