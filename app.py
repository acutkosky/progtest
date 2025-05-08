from flask import Flask, render_template, request, jsonify
import os
import json
from exercises import EXERCISES, get_exercise
from test_runner import run_tests
from static.terminal import execute_command

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', exercises=EXERCISES)

@app.route('/exercise/<int:exercise_id>')
def exercise(exercise_id):
    exercise = get_exercise(exercise_id)
    if exercise:
        return render_template('exercise.html', exercise=exercise)
    return "Exercise not found", 404

@app.route('/submit/python', methods=['POST'])
def submit_python():
    data = request.json
    exercise_id = data.get('exercise_id')
    code = data.get('code')
    
    exercise = get_exercise(exercise_id)
    if not exercise or not exercise.test_cases:
        return jsonify({
            "success": False,
            "error": "Invalid exercise"
        })
    
    try:
        # Run tests
        results = run_tests(code, exercise.test_cases)
        
        # Format results for display
        output = []
        passed_tests = 0
        
        for result in results:
            output.append(f"Test case: {result.description}")
            output.append(f"Expected: {result.expected}")
            output.append(f"Got: {result.got}")
            if result.output:
                output.append("Output:")
                output.append(result.output)
            output.append(f"Passed: {result.passed}")
            output.append("---")
            
            if result.passed:
                passed_tests += 1
        
        output.append(f"\nPassed {passed_tests} out of {len(results)} tests")
        
        return jsonify({
            "success": True,
            "output": "\n".join(output),
            "passed": passed_tests == len(results)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/submit/terminal', methods=['POST'])
def submit_terminal():
    data = request.json
    command = data.get('command')
    
    try:
        output = execute_command(command)
        return jsonify({
            "success": True,
            "output": output
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=8080) 