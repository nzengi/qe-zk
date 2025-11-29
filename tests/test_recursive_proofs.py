"""
Recursive Proofs Tests

Tests for recursive proofs functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, RecursiveProver, ProofComposer,
    NestedProofBuilder, ProofAggregator, RecursiveQEZK
)
from qezk.exceptions import ProtocolError, VerificationError


class TestRecursiveProofs(unittest.TestCase):
    """Test cases for recursive proofs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    def test_recursive_prover(self):
        """Test recursive prover"""
        recursive_prover = RecursiveProver(self.qezk)
        
        # Generate base proof
        base_proof = self.qezk.prove("I know the secret", "11010110", seed=42)
        
        # Generate proof of proof
        proof_of_proof = recursive_prover.prove_proof(base_proof, seed=43)
        
        self.assertIsNotNone(proof_of_proof)
        self.assertGreaterEqual(proof_of_proof.chsh_value, 0.0)
        self.assertLessEqual(proof_of_proof.chsh_value, 3.0)
    
    def test_proof_composer(self):
        """Test proof composer"""
        composer = ProofComposer(self.qezk)
        
        # Generate multiple proofs (use binary strings)
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        # Compose
        composite = composer.compose_proofs(proofs, "Composite", seed=50)
        
        self.assertIsNotNone(composite)
        self.assertEqual(composite.statement, "Composite")
    
    def test_proof_composer_empty(self):
        """Test proof composer with empty list"""
        composer = ProofComposer(self.qezk)
        
        with self.assertRaises(ProtocolError):
            composer.compose_proofs([])
    
    def test_nested_proof_builder(self):
        """Test nested proof builder"""
        builder = NestedProofBuilder(self.qezk)
        
        nested_proof = builder.build_nested_proof(
            "I know the secret", "11010110", depth=2, seed=42
        )
        
        self.assertIsNotNone(nested_proof)
        self.assertEqual(nested_proof.recursion_depth, 2)
        self.assertEqual(len(nested_proof.inner_proofs), 2)
        self.assertIsNotNone(nested_proof.outer_proof)
    
    def test_nested_proof_invalid_depth(self):
        """Test nested proof with invalid depth"""
        builder = NestedProofBuilder(self.qezk)
        
        with self.assertRaises(ProtocolError):
            builder.build_nested_proof("test", "1101", depth=0)
    
    def test_proof_aggregator(self):
        """Test proof aggregator"""
        aggregator = ProofAggregator(self.qezk)
        
        # Generate proofs (use binary strings)
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        # Aggregate (don't verify all, some may be invalid due to randomness)
        aggregated, metadata = aggregator.aggregate_proofs(proofs, verify_all=False, seed=50)
        
        self.assertIsNotNone(aggregated)
        self.assertIn('num_proofs', metadata)
        self.assertEqual(metadata['num_proofs'], 3)
    
    def test_proof_aggregator_empty(self):
        """Test proof aggregator with empty list"""
        aggregator = ProofAggregator(self.qezk)
        
        with self.assertRaises(ProtocolError):
            aggregator.aggregate_proofs([])
    
    def test_batch_aggregate(self):
        """Test batch aggregation"""
        aggregator = ProofAggregator(self.qezk)
        
        # Create batches
        batch1 = [
            self.qezk.prove("Statement 1", "11010110", seed=42),
            self.qezk.prove("Statement 2", "10101010", seed=43)
        ]
        batch2 = [
            self.qezk.prove("Statement 3", "11111111", seed=44)
        ]
        
        batches = [batch1, batch2]
        aggregated = aggregator.batch_aggregate(batches, verify_all=False, seed=50)
        
        self.assertEqual(len(aggregated), 2)
    
    def test_recursive_qezk(self):
        """Test recursive QE-ZK"""
        recursive_qezk = RecursiveQEZK(self.qezk)
        
        # Recursive proof
        recursive_proof = recursive_qezk.prove_recursively(
            "I know the secret", "11010110", depth=2, seed=42
        )
        
        self.assertIsNotNone(recursive_proof)
        self.assertEqual(recursive_proof.recursion_depth, 2)
    
    def test_proof_of_proof_integration(self):
        """Test proof of proof integration"""
        recursive_qezk = RecursiveQEZK(self.qezk)
        
        base_proof = self.qezk.prove("I know the secret", "11010110", seed=42)
        proof_of_proof = recursive_qezk.prove_proof_of_proof(base_proof, seed=43)
        
        self.assertIsNotNone(proof_of_proof)
        self.assertGreaterEqual(proof_of_proof.chsh_value, 0.0)
        self.assertLessEqual(proof_of_proof.chsh_value, 3.0)


if __name__ == '__main__':
    unittest.main()

