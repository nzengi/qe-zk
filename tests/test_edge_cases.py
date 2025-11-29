"""
Edge Case Tests

Tests for edge cases and boundary conditions.
Similar to comprehensive test suites in zk-SNARK/zk-STARK implementations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import QuantumEntanglementZK


class TestEdgeCases(unittest.TestCase):
    """Edge case and boundary condition tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100, chsh_threshold=2.2)
    
    def test_empty_witness(self):
        """Test with empty witness"""
        statement = "I know the secret"
        witness = ""
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        
        print(f"\n  Empty Witness Test:")
        print(f"    Proof generated: ✓")
    
    def test_very_long_witness(self):
        """Test with very long witness"""
        statement = "I know the secret"
        witness = "1" * 1000  # 1000-bit witness
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        
        print(f"\n  Very Long Witness Test:")
        print(f"    Proof generated: ✓")
        print(f"    Witness length: {len(witness)} bits")
    
    def test_very_short_statement(self):
        """Test with very short statement"""
        statement = "X"
        witness = "1101011010110101"
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, statement)
        
        print(f"\n  Very Short Statement Test:")
        print(f"    Proof generated: ✓")
    
    def test_very_long_statement(self):
        """Test with very long statement"""
        statement = "I know the secret " * 100
        witness = "1101011010110101"
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, statement)
        
        print(f"\n  Very Long Statement Test:")
        print(f"    Proof generated: ✓")
        print(f"    Statement length: {len(statement)} characters")
    
    def test_single_epr_pair(self):
        """Test with minimum EPR pairs"""
        qezk = QuantumEntanglementZK(num_epr_pairs=1, chsh_threshold=2.2)
        statement = "I know the secret"
        witness = "1101011010110101"
        
        proof = qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), 1)
        
        print(f"\n  Single EPR Pair Test:")
        print(f"    Proof generated: ✓")
    
    def test_unicode_statement(self):
        """Test with Unicode characters in statement"""
        statement = "我知道秘密"  # Chinese: "I know the secret"
        witness = "1101011010110101"
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, statement)
        
        print(f"\n  Unicode Statement Test:")
        print(f"    Proof generated: ✓")
    
    def test_special_characters_statement(self):
        """Test with special characters"""
        statement = "I know the secret! @#$%^&*()"
        witness = "1101011010110101"
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, statement)
        
        print(f"\n  Special Characters Test:")
        print(f"    Proof generated: ✓")
    
    def test_all_zeros_witness(self):
        """Test with all zeros witness"""
        statement = "I know the secret"
        witness = "0" * 16
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        
        print(f"\n  All Zeros Witness Test:")
        print(f"    Proof generated: ✓")
    
    def test_all_ones_witness(self):
        """Test with all ones witness"""
        statement = "I know the secret"
        witness = "1" * 16
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        
        print(f"\n  All Ones Witness Test:")
        print(f"    Proof generated: ✓")
    
    def test_alternating_witness(self):
        """Test with alternating pattern witness"""
        statement = "I know the secret"
        witness = "01" * 8
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), self.qezk.num_epr_pairs)
        
        print(f"\n  Alternating Witness Test:")
        print(f"    Proof generated: ✓")
    
    def test_different_chsh_thresholds(self):
        """Test with different CHSH thresholds"""
        statement = "I know the secret"
        witness = "1101011010110101"
        
        thresholds = [1.0, 1.5, 2.0, 2.2, 2.5]
        
        for threshold in thresholds:
            qezk = QuantumEntanglementZK(num_epr_pairs=100, chsh_threshold=threshold)
            proof = qezk.prove(statement, witness, seed=42)
            
            self.assertIsNotNone(proof)
            self.assertEqual(qezk.chsh_threshold, threshold)
        
        print(f"\n  Different CHSH Thresholds Test:")
        print(f"    All thresholds work: ✓")


if __name__ == '__main__':
    unittest.main()

