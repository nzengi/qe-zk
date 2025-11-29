"""
Performance Analysis Example

Demonstrates performance analysis capabilities of the QE-ZK simulation framework.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import QEZKSimulation


def main():
    """Performance analysis demonstration"""
    print("=" * 70)
    print("QE-ZK Performance Analysis")
    print("=" * 70)
    print()
    
    # Initialize simulator
    print("Initializing simulation framework...")
    simulator = QEZKSimulation(num_epr_pairs=500)
    print("✓ Simulator initialized")
    print()
    
    # Single statement simulation
    print("Running single statement simulation (10 trials)...")
    statement = "I know the secret password"
    witness = "1101011010110101"
    
    results = simulator.simulate_protocol(statement, witness, num_trials=10, seed=42)
    
    print(f"  Success Rate: {results['success_rate']:.2%}")
    print(f"  Average CHSH: {results['avg_chsh']:.4f}")
    print(f"  Std Dev CHSH: {results['std_chsh']:.4f}")
    print(f"  Valid Proofs: {results['valid_proofs']}/{results['total_trials']}")
    print()
    
    # Multiple statements analysis
    print("Running performance analysis across multiple statements...")
    statements = [
        "I know the first secret",
        "I know the second secret",
        "I know the third secret"
    ]
    witnesses = [
        "1101011010110101",
        "1010101010101010",
        "1111000011110000"
    ]
    
    perf_results = simulator.performance_analysis(statements, witnesses)
    
    print(f"  Overall Success Rate: {perf_results['overall_success_rate']:.2%}")
    print(f"  Overall Average CHSH: {perf_results['overall_avg_chsh']:.4f}")
    print(f"  Number of Statements: {len(perf_results['individual_results'])}")
    print()
    
    # Individual results
    print("Individual Statement Results:")
    for i, result in enumerate(perf_results['individual_results']):
        print(f"  Statement {i+1}:")
        print(f"    Success Rate: {result['success_rate']:.2%}")
        print(f"    Average CHSH: {result['avg_chsh']:.4f}")
    print()
    
    print("=" * 70)
    print("Performance Analysis Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

