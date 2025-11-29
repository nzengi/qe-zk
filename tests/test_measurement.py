"""
Tests for Bell measurement
"""

import unittest
import numpy as np
from qezk.measurement import BellMeasurement
from qezk.quantum_state import QuantumStatePreparation


class TestBellMeasurement(unittest.TestCase):
    """Test cases for BellMeasurement"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.measurement = BellMeasurement()
        self.quantum_prep = QuantumStatePreparation()
    
    def test_measurement_bases(self):
        """Test measurement in different bases"""
        # Create a Bell state
        state = self.quantum_prep.create_bell_state('phi_plus')
        
        # Measure in each basis
        for basis in ['Z', 'X', 'Y']:
            result = self.measurement.measure(state, basis)
            self.assertIn(result, [0, 1])
    
    def test_bell_state_measurement(self):
        """Test Bell state identification"""
        # Test with |Φ⁺⟩
        phi_plus = self.quantum_prep.create_bell_state('phi_plus')
        name, prob = self.measurement.bell_state_measurement(phi_plus)
        
        self.assertIn(name, ['Φ⁺', 'Φ⁻', 'Ψ⁺', 'Ψ⁻'])
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
    
    def test_chsh_inequality(self):
        """Test CHSH inequality calculation"""
        # Create correlated results (simulating perfect entanglement)
        alice_results = [0, 1, 0, 1] * 100
        bob_results = [0, 1, 0, 1] * 100  # Perfect correlation
        alice_bases = ['Z', 'X', 'Z', 'X'] * 100
        bob_bases = ['Z', 'X', 'Z', 'X'] * 100
        
        chsh_value, E = self.measurement.chsh_inequality_test(
            alice_results, bob_results, alice_bases, bob_bases
        )
        
        self.assertGreaterEqual(chsh_value, 0.0)
        self.assertLessEqual(chsh_value, 3.0)  # Should be less than 2√2 ≈ 2.828


if __name__ == '__main__':
    unittest.main()

