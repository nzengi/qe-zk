"""
Basic Usage Example

Demonstrates basic usage of the Quantum Entanglement Zero-Knowledge system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import QuantumEntanglementZK, QEZKSecurity


def main():
    """Basic usage demonstration"""
    print("=" * 70)
    print("Quantum Entanglement Zero-Knowledge (QE-ZK) System")
    print("Basic Usage Example")
    print("=" * 70)
    print()
    
    # Initialize system
    print("Initializing QE-ZK system...")
    qezk = QuantumEntanglementZK(num_epr_pairs=1000, chsh_threshold=2.2)
    print("✓ System initialized")
    print()
    
    # Example statement and witness
    statement = "I know the secret password"
    witness = "1101011010110101"  # 16-bit witness
    
    print(f"Statement: {statement}")
    print(f"Witness: {witness}")
    print()
    
    # Generate proof
    print("Generating QE-ZK proof...")
    proof = qezk.prove(statement, witness, seed=42)
    print("✓ Proof generated")
    print()
    
    # Display results
    print("Proof Results:")
    print(f"  CHSH Value: {proof.chsh_value:.4f}")
    print(f"  Classical Bound: 2.0")
    print(f"  Quantum Bound: 2.828")
    print(f"  Is Valid: {proof.is_valid}")
    print(f"  Measurement Bases: {proof.measurement_bases[:10]}... (showing first 10)")
    print()
    
    # Security analysis
    print("Security Properties:")
    security = QEZKSecurity.information_theoretic_security()
    for prop, value in security.items():
        print(f"  {prop}: {value}")
    print()
    
    print("=" * 70)
    print("Basic Usage Example Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

