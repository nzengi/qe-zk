"""
Hardware Interface Tests

Tests for quantum hardware interface and backend integration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from qezk import (
    SimulationBackend, HardwareInterface, HardwareQEZK
)
from qezk.exceptions import MeasurementError, QuantumStateError


class TestHardwareInterface(unittest.TestCase):
    """Test cases for hardware interface"""
    
    def test_simulation_backend_bell_state(self):
        """Test Bell state creation on simulation backend"""
        backend = SimulationBackend()
        
        # Test all Bell states
        for state_type in ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus']:
            state = backend.create_bell_state(state_type)
            self.assertEqual(state.shape, (4,))
            self.assertAlmostEqual(np.linalg.norm(state), 1.0, places=5)
    
    def test_simulation_backend_measurement(self):
        """Test measurement on simulation backend"""
        backend = SimulationBackend()
        backend.create_bell_state('phi_plus')
        
        # Test all bases
        for basis in ['Z', 'X', 'Y']:
            result = backend.measure(0, basis)
            self.assertIn(result, [0, 1])
        
        # Test invalid basis
        with self.assertRaises(MeasurementError):
            backend.measure(0, 'W')
    
    def test_simulation_backend_gates(self):
        """Test gate application on simulation backend"""
        backend = SimulationBackend()
        
        # Apply Hadamard
        backend.apply_gate('H', 0)
        state = backend.get_state()
        self.assertIsNotNone(state)
        
        # Test invalid gate
        with self.assertRaises(QuantumStateError):
            backend.apply_gate('INVALID', 0)
    
    def test_hardware_interface(self):
        """Test hardware interface wrapper"""
        backend = SimulationBackend()
        hardware = HardwareInterface(backend=backend)
        
        # Generate EPR pairs
        epr_pairs = hardware.generate_epr_pairs(num_pairs=10)
        self.assertEqual(len(epr_pairs), 10)
        
        # Measure particles
        result = hardware.measure_particle(0, 'Z')
        self.assertIn(result, [0, 1])
        
        # Get backend info
        info = hardware.get_backend_info()
        self.assertEqual(info['backend_type'], 'SimulationBackend')
        self.assertTrue(info['is_simulation'])
    
    def test_hardware_qezk(self):
        """Test hardware-integrated QE-ZK"""
        qezk = HardwareQEZK(num_epr_pairs=100)
        
        statement = "I know the secret"
        witness = "11010110"
        
        proof = qezk.prove_with_hardware(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), 100)
        self.assertEqual(len(proof.verifier_results), 100)
        self.assertGreaterEqual(proof.chsh_value, 0)
        self.assertLessEqual(proof.chsh_value, 3.0)
    
    def test_backend_reset(self):
        """Test backend reset functionality"""
        backend = SimulationBackend()
        backend.create_bell_state('phi_plus')
        
        # Reset
        backend.reset()
        state = backend.get_state()
        
        # Should be |00⟩
        expected = np.array([1, 0, 0, 0], dtype=complex)
        np.testing.assert_array_almost_equal(state, expected)


if __name__ == '__main__':
    unittest.main()

