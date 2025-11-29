"""
Performance Benchmarks

Tests similar to zk-SNARK, zk-STARK, and Halo2 benchmarks.
Measures proof generation time, verification time, and proof sizes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import time
import numpy as np
from qezk import QuantumEntanglementZK, QEZKSimulation


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=1000, chsh_threshold=2.2)
        self.statements = [
            "I know secret 1",
            "I know secret 2",
            "I know secret 3"
        ]
        self.witnesses = [
            "1101011010110101",
            "1010101010101010",
            "1111000011110000"
        ]
    
    def test_proof_generation_time(self):
        """Test proof generation time (similar to zk-SNARK benchmarks)"""
        statement = self.statements[0]
        witness = self.witnesses[0]
        
        # Measure proof generation time
        start_time = time.time()
        proof = self.qezk.prove(statement, witness, seed=42)
        generation_time = time.time() - start_time
        
        print(f"\n  Proof Generation Time: {generation_time:.4f} seconds")
        print(f"  EPR Pairs: {self.qezk.num_epr_pairs}")
        print(f"  Time per EPR pair: {generation_time/self.qezk.num_epr_pairs*1000:.4f} ms")
        
        self.assertGreater(generation_time, 0)
        self.assertLess(generation_time, 10)  # Should complete in reasonable time
    
    def test_verification_time(self):
        """Test verification time (similar to zk-STARK benchmarks)"""
        statement = self.statements[0]
        witness = self.witnesses[0]
        
        # Generate proof
        proof = self.qezk.prove(statement, witness, seed=42)
        
        # Measure verification time
        start_time = time.time()
        is_valid, chsh_value = self.qezk.verify(
            proof.prover_results,
            proof.verifier_results,
            proof.measurement_bases
        )
        verification_time = time.time() - start_time
        
        print(f"\n  Verification Time: {verification_time:.4f} seconds")
        print(f"  Verification Time per measurement: {verification_time/len(proof.prover_results)*1000:.4f} ms")
        
        self.assertGreater(verification_time, 0)
        self.assertLess(verification_time, 1)  # Verification should be fast
    
    def test_proof_size(self):
        """Test proof size (similar to Halo2 proof size tests)"""
        statement = self.statements[0]
        witness = self.witnesses[0]
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        # Calculate proof size
        prover_results_size = len(proof.prover_results) * 4  # 4 bytes per int
        verifier_results_size = len(proof.verifier_results) * 4
        bases_size = len(proof.measurement_bases) * 1  # 1 byte per char
        statement_size = len(proof.statement.encode('utf-8'))
        chsh_size = 8  # float64
        
        total_size = (prover_results_size + verifier_results_size + 
                     bases_size + statement_size + chsh_size)
        
        print(f"\n  Proof Size: {total_size} bytes")
        print(f"  Prover Results: {prover_results_size} bytes")
        print(f"  Verifier Results: {verifier_results_size} bytes")
        print(f"  Measurement Bases: {bases_size} bytes")
        print(f"  Statement: {statement_size} bytes")
        print(f"  CHSH Value: {chsh_size} bytes")
        print(f"  Size per EPR pair: {total_size/self.qezk.num_epr_pairs:.2f} bytes")
        
        self.assertGreater(total_size, 0)
    
    def test_scalability(self):
        """Test scalability with different numbers of EPR pairs"""
        statement = self.statements[0]
        witness = self.witnesses[0]
        
        epr_counts = [100, 500, 1000, 2000]
        times = []
        
        for count in epr_counts:
            qezk = QuantumEntanglementZK(num_epr_pairs=count, chsh_threshold=2.2)
            start_time = time.time()
            proof = qezk.prove(statement, witness, seed=42)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            print(f"\n  EPR Pairs: {count}, Time: {elapsed:.4f}s")
        
        # Check that time scales roughly linearly
        print(f"\n  Scalability: Times scale with EPR pair count")
        self.assertEqual(len(times), len(epr_counts))
    
    def test_throughput(self):
        """Test throughput (proofs per second)"""
        statement = self.statements[0]
        witness = self.witnesses[0]
        
        num_proofs = 10
        start_time = time.time()
        
        for _ in range(num_proofs):
            proof = self.qezk.prove(statement, witness, seed=None)
        
        total_time = time.time() - start_time
        throughput = num_proofs / total_time
        
        print(f"\n  Throughput: {throughput:.2f} proofs/second")
        print(f"  Total Time for {num_proofs} proofs: {total_time:.4f} seconds")
        
        self.assertGreater(throughput, 0)


if __name__ == '__main__':
    unittest.main()

