# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: run_tests.py
"""Run Prompt Generator Tests.

This script runs all test cases for the prompt generator application,
providing comprehensive validation of the functionality.
"""
import sys
import unittest
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import test modules
from intelligence.test.test_prompt_generator import TestPromptGenerator


def main():
    """Main function to run all tests."""
    print("Starting Prompt Generator Test Suite")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPromptGenerator))

    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )

    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print(f"Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print(f"\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"   • {test}")

    if result.errors:
        print(f"\nTest Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}")

    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print(f"\nSome tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
