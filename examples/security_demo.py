"""
Security Demonstration

Demonstrates security properties and attack resistance of QE-ZK.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import QEZKSecurity


def main():
    """Security demonstration"""
    print("=" * 70)
    print("QE-ZK Security Properties Demonstration")
    print("=" * 70)
    print()
    
    # Information-theoretic security
    print("Information-Theoretic Security Properties:")
    print("-" * 70)
    security_props = QEZKSecurity.information_theoretic_security()
    for prop, value in security_props.items():
        status = "✓" if value else "✗"
        print(f"  {status} {prop}: {value}")
    print()
    
    # Attack resistance
    print("Attack Resistance:")
    print("-" * 70)
    attack_resistance = QEZKSecurity.attack_resistance()
    for attack_type, info in attack_resistance.items():
        status = "✓" if info['resistant'] else "✗"
        print(f"  {status} {attack_type}:")
        print(f"      Resistant: {info['resistant']}")
        print(f"      Reason: {info['reason']}")
    print()
    
    # Completeness and soundness
    print("Completeness and Soundness:")
    print("-" * 70)
    completeness_soundness = QEZKSecurity.completeness_soundness()
    for prop, value in completeness_soundness.items():
        print(f"  {prop}: {value}")
    print()
    
    print("=" * 70)
    print("Security Demonstration Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

