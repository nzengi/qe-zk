"""
Protocol Correctness Tests

Tests similar to Halo2 circuit correctness tests.
Verifies protocol correctness, consistency, and edge cases.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from qezk import QuantumEntanglementZK
from qezk.quantum_state import QuantumStatePreparation
from qezk.measurement import BellMeasurement


class TestProtocolCorrectness(unittest.TestCase):
    """Protocol correctness verification tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=500, chsh_threshold=2.2)
        self.statement = "I know the secret"
        self.witness = "1101011010110101"
    
    def test_proof_structure_correctness(self):
        """Test that proof structure is correct"""
        proof = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # Check all required fields exist
        self.assertIsNotNone(proof.prover_results)
        self.assertIsNotNone(proof.verifier_results)
        self.assertIsNotNone(proof.measurement_bases)
        self.assertIsNotNone(proof.chsh_value)
        self.assertIsNotNone(proof.is_valid)
        self.assertEqual(proof.statement, self.statement)
        
        # Check lengths match
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        self.assertEqual(len(proof.verifier_results), self.qezk.num_epr_pairs)
        self.assertEqual(len(proof.measurement_bases), self.qezk.num_epr_pairs)
        
        print(f"\n  Proof Structure Correctness:")
        print(f"    All fields present: ✓")
        print(f"    Lengths match: ✓")
    
    def test_measurement_results_validity(self):
        """Test that measurement results are valid (0 or 1)"""
        proof = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # All results should be 0 or 1
        for result in proof.prover_results:
            self.assertIn(result, [0, 1])
        
        for result in proof.verifier_results:
            self.assertIn(result, [0, 1])
        
        print(f"\n  Measurement Results Validity:")
        print(f"    All prover results valid: ✓")
        print(f"    All verifier results valid: ✓")
    
    def test_measurement_bases_validity(self):
        """Test that measurement bases are valid (Z, X, or Y)"""
        proof = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # All bases should be Z, X, or Y
        for basis in proof.measurement_bases:
            self.assertIn(basis, ['Z', 'X', 'Y'])
        
        print(f"\n  Measurement Bases Validity:")
        print(f"    All bases valid: ✓")
        print(f"    Basis distribution: Z={proof.measurement_bases.count('Z')}, "
              f"X={proof.measurement_bases.count('X')}, Y={proof.measurement_bases.count('Y')}")
    
    def test_chsh_value_range(self):
        """Test that CHSH value is in valid range"""
        proof = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # CHSH value should be between 0 and 3 (theoretical max is 2√2 ≈ 2.828)
        self.assertGreaterEqual(proof.chsh_value, 0.0)
        self.assertLessEqual(proof.chsh_value, 3.0)
        
        print(f"\n  CHSH Value Range:")
        print(f"    CHSH value: {proof.chsh_value:.4f}")
        print(f"    Classical bound: 2.0")
        print(f"    Quantum bound: 2.828")
        print(f"    Value in valid range: ✓")
    
    def test_deterministic_bases(self):
        """Test that same statement produces same bases"""
        proof1 = self.qezk.prove(self.statement, self.witness, seed=42)
        proof2 = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # Same statement should produce same bases
        self.assertEqual(proof1.measurement_bases, proof2.measurement_bases)
        
        print(f"\n  Deterministic Bases:")
        print(f"    Same statement → same bases: ✓")
    
    def test_reproducibility(self):
        """Test that same seed produces reproducible results"""
        proof1 = self.qezk.prove(self.statement, self.witness, seed=42)
        proof2 = self.qezk.prove(self.statement, self.witness, seed=42)
        
        # With same seed, results should be identical
        self.assertEqual(proof1.prover_results, proof2.prover_results)
        self.assertEqual(proof1.verifier_results, proof2.verifier_results)
        self.assertEqual(proof1.measurement_bases, proof2.measurement_bases)
        self.assertAlmostEqual(proof1.chsh_value, proof2.chsh_value, places=5)
        
        print(f"\n  Reproducibility:")
        print(f"    Same seed → same results: ✓")
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results"""
        proof1 = self.qezk.prove(self.statement, self.witness, seed=42)
        proof2 = self.qezk.prove(self.statement, self.witness, seed=43)
        
        # Different seeds should produce different results
        self.assertNotEqual(proof1.prover_results, proof2.prover_results)
        
        print(f"\n  Different Seeds:")
        print(f"    Different seeds → different results: ✓")
    
    def test_bell_state_correctness(self):
        """Test that Bell states are correctly generated"""
        quantum_prep = QuantumStatePreparation()
        
        # Test all Bell states
        bell_states = ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus']
        
        for state_type in bell_states:
            state = quantum_prep.create_bell_state(state_type)
            
            # Check normalization
            norm = np.sqrt(np.sum(np.abs(state)**2))
            self.assertAlmostEqual(norm, 1.0, places=10)
            
            # Check dimension
            self.assertEqual(len(state), 4)
        
        print(f"\n  Bell State Correctness:")
        print(f"    All Bell states normalized: ✓")
        print(f"    All Bell states have correct dimension: ✓")
    
    def test_measurement_consistency(self):
        """Test measurement consistency"""
        measurement = BellMeasurement()
        quantum_prep = QuantumStatePreparation()
        
        # Create Bell state
        state = quantum_prep.create_bell_state('phi_plus')
        
        # Measure multiple times in same basis
        results = [measurement.measure(state, 'Z') for _ in range(100)]
        
        # Results should be valid
        for result in results:
            self.assertIn(result, [0, 1])
        
        print(f"\n  Measurement Consistency:")
        print(f"    All measurements valid: ✓")
        print(f"    Result distribution: {sum(results)} ones, {100-sum(results)} zeros")


if __name__ == '__main__':
    unittest.main()

