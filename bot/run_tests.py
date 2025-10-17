"""Run all tests - convenience script"""
import sys
import os
import subprocess

# Ensure we're in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

print(f"Running tests from: {os.getcwd()}")

# Run the test runner from the tests directory
test_runner = os.path.join(project_root, 'tests', 'run_all_tests.py')
result = subprocess.run(
    [sys.executable, test_runner],
    cwd=project_root  # Ensure .env is found
)

sys.exit(result.returncode)