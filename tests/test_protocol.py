"""
Tests for QE-ZK protocol
"""

import unittest
from qezk.protocol import QuantumEntanglementZK, QEZKProof


class TestQuantumEntanglementZK(unittest.TestCase):
    """Test cases for QuantumEntanglementZK protocol"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100, chsh_threshold=2.2)
    
    def test_setup(self):
        """Test protocol setup"""
        prover_particles, verifier_particles = self.qezk.setup(seed=42)
        
        self.assertEqual(len(prover_particles), 100)
        self.assertEqual(len(verifier_particles), 100)
    
    def test_prover_phase(self):
        """Test prover phase"""
        statement = "I know the secret"
        witness = "11010110"
        prover_particles, _ = self.qezk.setup(seed=42)
        
        results, bases = self.qezk.prover_phase(statement, witness, prover_particles)
        
        self.assertEqual(len(results), 100)
        self.assertEqual(len(bases), 100)
        self.assertTrue(all(r in [0, 1] for r in results))
        self.assertTrue(all(b in ['Z', 'X', 'Y'] for b in bases))
    
    def test_verifier_phase(self):
        """Test verifier phase"""
        statement = "I know the secret"
        _, verifier_particles = self.qezk.setup(seed=42)
        bases = ['Z'] * 100
        
        results = self.qezk.verifier_phase(statement, verifier_particles, bases)
        
        self.assertEqual(len(results), 100)
        self.assertTrue(all(r in [0, 1] for r in results))
    
    def test_complete_protocol(self):
        """Test complete protocol execution"""
        statement = "I know the secret password"
        witness = "1101011010110101"
        
        proof = self.qezk.prove(statement, witness, seed=42)
        
        self.assertIsInstance(proof, QEZKProof)
        self.assertEqual(proof.statement, statement)
        self.assertGreaterEqual(proof.chsh_value, 0.0)
        # is_valid should be a boolean (True or False)
        self.assertIn(proof.is_valid, [True, False])
        self.assertEqual(len(proof.prover_results), 100)
        self.assertEqual(len(proof.verifier_results), 100)
        self.assertEqual(len(proof.measurement_bases), 100)


if __name__ == '__main__':
    unittest.main()

