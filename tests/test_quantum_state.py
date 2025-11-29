"""
Tests for quantum state preparation
"""

import unittest
import numpy as np
from qezk.quantum_state import QuantumStatePreparation


class TestQuantumStatePreparation(unittest.TestCase):
    """Test cases for QuantumStatePreparation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.quantum_prep = QuantumStatePreparation()
    
    def test_bell_state_phi_plus(self):
        """Test creation of |Φ⁺⟩ Bell state"""
        state = self.quantum_prep.create_bell_state('phi_plus')
        
        # |Φ⁺⟩ = (|00⟩ + |11⟩)/√2 = [1/√2, 0, 0, 1/√2]
        expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        
        np.testing.assert_array_almost_equal(state, expected)
    
    def test_bell_state_normalization(self):
        """Test that Bell states are normalized"""
        for state_type in ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus']:
            state = self.quantum_prep.create_bell_state(state_type)
            norm = np.sqrt(np.sum(np.abs(state)**2))
            self.assertAlmostEqual(norm, 1.0, places=10)
    
    def test_apply_gate(self):
        """Test applying gates to quantum states"""
        state = self.quantum_prep.create_bell_state('phi_plus')
        
        # Apply X gate to first qubit
        transformed = self.quantum_prep.apply_gate(state, self.quantum_prep.X, qubit=0)
        
        # Should still be normalized
        norm = np.sqrt(np.sum(np.abs(transformed)**2))
        self.assertAlmostEqual(norm, 1.0, places=10)
    
    def test_normalize_state(self):
        """Test state normalization"""
        unnormalized = np.array([2, 0, 0, 2], dtype=complex)
        normalized = self.quantum_prep.normalize_state(unnormalized)
        
        norm = np.sqrt(np.sum(np.abs(normalized)**2))
        self.assertAlmostEqual(norm, 1.0, places=10)


if __name__ == '__main__':
    unittest.main()

