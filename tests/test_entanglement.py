"""
Tests for entanglement source
"""

import unittest
import numpy as np
from qezk.quantum_state import QuantumStatePreparation
from qezk.entanglement import EntanglementSource


class TestEntanglementSource(unittest.TestCase):
    """Test cases for EntanglementSource"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.quantum_prep = QuantumStatePreparation()
        self.entanglement = EntanglementSource(self.quantum_prep)
    
    def test_generate_epr_pairs(self):
        """Test EPR pair generation"""
        num_pairs = 10
        epr_pairs = self.entanglement.generate_epr_pairs(num_pairs)
        
        self.assertEqual(len(epr_pairs), num_pairs)
        
        # Check that all pairs are valid Bell states
        for pair in epr_pairs:
            self.assertEqual(len(pair), 4)  # 2-qubit state
            norm = np.sqrt(np.sum(np.abs(pair)**2))
            self.assertAlmostEqual(norm, 1.0, places=10)
    
    def test_split_epr_pairs(self):
        """Test splitting EPR pairs"""
        epr_pairs = self.entanglement.generate_epr_pairs(5)
        prover_particles, verifier_particles = self.entanglement.split_epr_pairs(epr_pairs)
        
        self.assertEqual(len(prover_particles), 5)
        self.assertEqual(len(verifier_particles), 5)
    
    def test_seed_reproducibility(self):
        """Test that seed produces reproducible results"""
        seed = 42
        
        self.entanglement.set_seed(seed)
        pairs1 = self.entanglement.generate_epr_pairs(10)
        
        self.entanglement.set_seed(seed)
        pairs2 = self.entanglement.generate_epr_pairs(10)
        
        # Results should be identical with same seed
        for p1, p2 in zip(pairs1, pairs2):
            np.testing.assert_array_almost_equal(p1, p2)


if __name__ == '__main__':
    unittest.main()

