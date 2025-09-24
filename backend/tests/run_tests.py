#!/usr/bin/env python3
"""
Test runner for Validatus comprehensive test suite.

This script provides a unified interface for running all tests across different phases
and categories with proper configuration and reporting.
"""

import sys
import os
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_command(command, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            cwd=backend_dir
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def install_test_dependencies():
    """Install test dependencies."""
    print("🔧 Installing test dependencies...")
    
    test_deps = [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.11.0",
        "pytest-xdist>=3.3.0",
        "pytest-html>=3.2.0",
        "pytest-json-report>=1.5.0",
        "psutil>=5.9.0",
        "httpx>=0.24.0",
        "fastapi[all]>=0.104.0"
    ]
    
    for dep in test_deps:
        print(f"  Installing {dep}...")
        returncode, stdout, stderr = run_command(f"pip install {dep}")
        if returncode != 0:
            print(f"❌ Failed to install {dep}: {stderr}")
            return False
    
    print("✅ Test dependencies installed successfully")
    return True

def run_unit_tests(phase=None, verbose=False, coverage=False):
    """Run unit tests."""
    print(f"🧪 Running unit tests{' for ' + phase if phase else ''}...")
    
    cmd_parts = ["python -m pytest backend/tests/unit/"]
    
    if phase:
        cmd_parts.append(f"-m phase_{phase.lower()}")
    
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "-x"  # Stop on first failure
    ])
    
    command = " ".join(cmd_parts)
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        print("✅ Unit tests passed")
    else:
        print(f"❌ Unit tests failed: {stderr}")
    
    return returncode == 0, stdout, stderr

def run_integration_tests(phase=None, verbose=False):
    """Run integration tests."""
    print(f"🔗 Running integration tests{' for ' + phase if phase else ''}...")
    
    cmd_parts = ["python -m pytest backend/tests/integration/"]
    
    if phase:
        cmd_parts.append(f"-m phase_{phase.lower()}")
    
    if verbose:
        cmd_parts.append("-v")
    
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--maxfail=5"  # Allow up to 5 failures
    ])
    
    command = " ".join(cmd_parts)
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        print("✅ Integration tests passed")
    else:
        print(f"❌ Integration tests failed: {stderr}")
    
    return returncode == 0, stdout, stderr

def run_performance_tests(phase=None, verbose=False):
    """Run performance tests."""
    print(f"⚡ Running performance tests{' for ' + phase if phase else ''}...")
    
    cmd_parts = ["python -m pytest backend/tests/performance/"]
    
    if phase:
        cmd_parts.append(f"-m phase_{phase.lower()}")
    
    if verbose:
        cmd_parts.append("-v")
    
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--maxfail=3",  # Allow fewer failures for performance tests
        "--durations=10"  # Show top 10 slowest tests
    ])
    
    command = " ".join(cmd_parts)
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        print("✅ Performance tests passed")
    else:
        print(f"❌ Performance tests failed: {stderr}")
    
    return returncode == 0, stdout, stderr

def run_api_tests(phase=None, verbose=False):
    """Run API tests."""
    print(f"🌐 Running API tests{' for ' + phase if phase else ''}...")
    
    cmd_parts = ["python -m pytest backend/tests/api/"]
    
    if phase:
        cmd_parts.append(f"-m phase_{phase.lower()}")
    
    if verbose:
        cmd_parts.append("-v")
    
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--maxfail=5"
    ])
    
    command = " ".join(cmd_parts)
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        print("✅ API tests passed")
    else:
        print(f"❌ API tests failed: {stderr}")
    
    return returncode == 0, stdout, stderr

def run_all_tests(phase=None, verbose=False, coverage=False, parallel=False):
    """Run all tests."""
    print(f"🚀 Running all tests{' for ' + phase if phase else ''}...")
    
    cmd_parts = ["python -m pytest backend/tests/"]
    
    if phase:
        cmd_parts.append(f"-m phase_{phase.lower()}")
    
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=json"
        ])
    
    if parallel:
        cmd_parts.append("-n auto")  # Use pytest-xdist for parallel execution
    
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--html=backend/tests/reports/test_report.html",
        "--json-report",
        "--json-report-file=backend/tests/reports/test_report.json"
    ])
    
    command = " ".join(cmd_parts)
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        print("✅ All tests passed")
    else:
        print(f"❌ Some tests failed: {stderr}")
    
    return returncode == 0, stdout, stderr

def generate_test_report():
    """Generate a comprehensive test report."""
    print("📊 Generating test report...")
    
    # Create reports directory
    reports_dir = backend_dir / "tests" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Run tests with JSON report
    returncode, stdout, stderr = run_command(
        "python -m pytest backend/tests/ --json-report --json-report-file=backend/tests/reports/test_results.json -v"
    )
    
    if os.path.exists(reports_dir / "test_results.json"):
        with open(reports_dir / "test_results.json", 'r') as f:
            test_data = json.load(f)
        
        # Generate summary report
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": test_data.get("summary", {}).get("total", 0),
            "passed": test_data.get("summary", {}).get("passed", 0),
            "failed": test_data.get("summary", {}).get("failed", 0),
            "skipped": test_data.get("summary", {}).get("skipped", 0),
            "duration": test_data.get("duration", 0),
            "test_categories": {
                "unit": 0,
                "integration": 0,
                "performance": 0,
                "api": 0
            },
            "phase_coverage": {
                "phase_a": 0,
                "phase_b": 0,
                "phase_c": 0,
                "phase_d": 0,
                "phase_e": 0
            }
        }
        
        # Analyze test results
        for test in test_data.get("tests", []):
            # Count by category
            if "unit" in test.get("nodeid", ""):
                summary["test_categories"]["unit"] += 1
            elif "integration" in test.get("nodeid", ""):
                summary["test_categories"]["integration"] += 1
            elif "performance" in test.get("nodeid", ""):
                summary["test_categories"]["performance"] += 1
            elif "api" in test.get("nodeid", ""):
                summary["test_categories"]["api"] += 1
            
            # Count by phase
            for phase in ["phase_a", "phase_b", "phase_c", "phase_d", "phase_e"]:
                if phase in test.get("nodeid", ""):
                    summary["phase_coverage"][phase] += 1
        
        # Save summary report
        with open(reports_dir / "test_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("✅ Test report generated")
        print(f"📁 Reports saved to: {reports_dir}")
        print(f"📊 Summary: {summary['passed']}/{summary['total_tests']} tests passed")
        
        return summary
    else:
        print("❌ Failed to generate test report")
        return None

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Validatus Test Suite Runner")
    parser.add_argument("--phase", choices=["a", "b", "c", "d", "e"], 
                       help="Run tests for specific phase")
    parser.add_argument("--type", choices=["unit", "integration", "performance", "api", "all"],
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install test dependencies")
    parser.add_argument("--report", action="store_true",
                       help="Generate test report")
    
    args = parser.parse_args()
    
    print("🧪 Validatus Comprehensive Test Suite")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
    
    # Determine phase
    phase_map = {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}
    phase = phase_map.get(args.phase) if args.phase else None
    
    success = True
    
    try:
        if args.type == "unit":
            success, _, _ = run_unit_tests(phase, args.verbose, args.coverage)
        elif args.type == "integration":
            success, _, _ = run_integration_tests(phase, args.verbose)
        elif args.type == "performance":
            success, _, _ = run_performance_tests(phase, args.verbose)
        elif args.type == "api":
            success, _, _ = run_api_tests(phase, args.verbose)
        elif args.type == "all":
            success, _, _ = run_all_tests(phase, args.verbose, args.coverage, args.parallel)
        
        # Generate report if requested
        if args.report:
            generate_test_report()
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
