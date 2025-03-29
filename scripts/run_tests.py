#!/usr/bin/env python3
"""
Script to run all tests with coverage
"""

import sys
import os
import subprocess
import shutil

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running tests with coverage...")
    
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Determine which Python command to use (python3 or python)
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    # Run pytest with coverage
    try:
        result = subprocess.run([
            python_cmd, "-m", "pytest",
            "tests/",
            "-v",
            "--cov=src",
            "--cov=scripts",
            "--cov-report=term",
            "--cov-report=html:coverage_html"
        ], check=True)
        
        print("\n✅ Tests completed successfully!")
        print("\n📊 Coverage report generated in ./coverage_html/")
        print("   Open ./coverage_html/index.html in a browser to view the report")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Determine which pip command to use
    python_cmd = "python3" if shutil.which("python3") else "python"
    pip_cmd = f"{python_cmd} -m pip"
    
    # Install test dependencies if needed
    if os.path.exists("requirements-dev.txt"):
        print("📦 Installing test dependencies...")
        try:
            subprocess.run(
                f"{pip_cmd} install -r requirements-dev.txt", 
                shell=True, 
                check=True
            )
            
            # Also install pytest-cov for coverage reports
            subprocess.run(
                f"{pip_cmd} install pytest-cov", 
                shell=True, 
                check=True
            )
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to install dependencies: {e}")
            sys.exit(e.returncode)
    
    # Run the tests
    run_tests()