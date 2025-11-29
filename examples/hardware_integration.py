"""
Hardware Integration Example

Demonstrates how to use QE-ZK with quantum hardware backends.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    HardwareQEZK, SimulationBackend, HardwareInterface,
    IBMQBackend, GoogleQuantumAIBackend
)


def example_simulation_backend():
    """Example using simulation backend (default)"""
    print("=" * 70)
    print("Example 1: Simulation Backend")
    print("=" * 70)
    print()
    
    # Use default simulation backend
    qezk = HardwareQEZK()
    
    statement = "I know the secret password"
    witness = "1101011010110101"
    
    print(f"Statement: {statement}")
    print(f"Witness: {witness}")
    print()
    
    # Generate proof
    proof = qezk.prove_with_hardware(statement, witness, seed=42)
    
    print(f"CHSH Value: {proof.chsh_value:.4f}")
    print(f"Is Valid: {proof.is_valid}")
    print(f"Backend: {qezk.hardware.get_backend_info()['backend_type']}")
    print()


def example_ibmq_backend():
    """Example using IBM Quantum backend (requires API token)"""
    print("=" * 70)
    print("Example 2: IBM Quantum Backend")
    print("=" * 70)
    print()
    
    print("Note: This requires IBM Quantum API token")
    print("Get token from: https://quantum-computing.ibm.com/")
    print()
    
    # Uncomment and add your API token:
    # api_token = "YOUR_IBM_QUANTUM_API_TOKEN"
    # ibmq_backend = IBMQBackend(api_token=api_token)
    # qezk = HardwareQEZK(hardware_backend=ibmq_backend)
    # 
    # statement = "I know the secret"
    # witness = "11010110"
    # proof = qezk.prove_with_hardware(statement, witness)
    # print(f"CHSH Value: {proof.chsh_value:.4f}")
    # print(f"Is Valid: {proof.is_valid}")
    
    print("IBM Quantum backend example (commented out - requires API token)")
    print()


def example_custom_backend():
    """Example using custom hardware interface"""
    print("=" * 70)
    print("Example 3: Custom Hardware Interface")
    print("=" * 70)
    print()
    
    # Create simulation backend
    backend = SimulationBackend(num_qubits=2)
    hardware = HardwareInterface(backend=backend)
    
    # Get backend info
    info = hardware.get_backend_info()
    print(f"Backend Type: {info['backend_type']}")
    print(f"Is Simulation: {info['is_simulation']}")
    print(f"Number of Qubits: {info['num_qubits']}")
    print()
    
    # Generate EPR pairs
    epr_pairs = hardware.generate_epr_pairs(num_pairs=5)
    print(f"Generated {len(epr_pairs)} EPR pairs")
    print()
    
    # Measure particles
    print("Measurement Results:")
    for i in range(3):
        result = hardware.measure_particle(0, 'Z')
        print(f"  Particle {i}, Z basis: {result}")
    print()


def main():
    """Run all examples"""
    example_simulation_backend()
    example_ibmq_backend()
    example_custom_backend()
    
    print("=" * 70)
    print("Hardware Integration Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()

