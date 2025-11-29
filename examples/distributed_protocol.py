"""
Distributed Protocol Example

Demonstrates distributed QE-ZK protocol over network.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from qezk import (
    QuantumEntanglementZK, DistributedProver, DistributedVerifier
)


def run_prover():
    """Run prover server"""
    print("=" * 70)
    print("Starting Prover Server")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    prover = DistributedProver(qezk, host='localhost', port=8888)
    
    try:
        prover.start_server()
    except KeyboardInterrupt:
        print("\nStopping prover...")
        prover.stop()


def run_verifier():
    """Run verifier client"""
    print("=" * 70)
    print("Starting Verifier Client")
    print("=" * 70)
    print()
    
    time.sleep(2)  # Wait for prover to start
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier = DistributedVerifier(qezk, prover_host='localhost', prover_port=8888)
    
    statement = "I know the secret password"
    witness = "11010110"  # Note: Verifier doesn't know witness
    
    print(f"Statement: {statement}")
    print("Connecting to prover...")
    print()
    
    # Note: In real distributed scenario, verifier wouldn't have witness
    # This is just for demonstration
    proof = verifier.verify_statement(statement, seed=42)
    
    if proof:
        print(f"CHSH Value: {proof.chsh_value:.4f}")
        print(f"Is Valid: {proof.is_valid}")
        print(f"Statement: {proof.statement}")
    else:
        print("Verification failed")
    
    verifier.disconnect()


def main():
    """Run distributed protocol example"""
    print("=" * 70)
    print("Distributed QE-ZK Protocol Example")
    print("=" * 70)
    print()
    print("This example demonstrates distributed protocol execution.")
    print("In a real scenario, prover and verifier would run on different machines.")
    print()
    
    # For demonstration, run both in same process
    # In real usage, they would be separate processes/machines
    
    # Start prover in background thread
    prover_thread = threading.Thread(target=run_prover, daemon=True)
    prover_thread.start()
    
    # Run verifier
    run_verifier()
    
    print()
    print("=" * 70)
    print("Distributed Protocol Example Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


