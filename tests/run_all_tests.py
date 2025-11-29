"""
Run All Tests with Detailed Output

This script runs all tests and provides a comprehensive summary,
similar to test suites in zk-SNARK, zk-STARK, and Halo2 projects.
"""

import unittest
import sys
import time

def run_all_tests():
    """Run all tests and provide summary"""
    print("=" * 70)
    print("Quantum Entanglement Zero-Knowledge (QE-ZK) - Test Suite")
    print("=" * 70)
    print()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Total Time: {elapsed_time:.2f} seconds")
    print()
    
    if result.failures:
        print("Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("=" * 70)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

