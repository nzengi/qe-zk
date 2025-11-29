"""
Real EPR Generation Tests

Tests for real EPR pair generation on quantum hardware.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from qezk import (
    RealEPRGenerator, PhysicalEPRSource, SimulationBackend
)
from qezk.exceptions import EntanglementError


class TestRealEPRGeneration(unittest.TestCase):
    """Test cases for real EPR generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.backend = SimulationBackend()
        self.generator = RealEPRGenerator(self.backend)
    
    def test_single_epr_generation(self):
        """Test single EPR pair generation"""
        state, metadata = self.generator.generate_epr_pair('phi_plus', verify=True)
        
        self.assertEqual(state.shape, (4,))
        self.assertEqual(metadata['state_type'], 'phi_plus')
        self.assertTrue(metadata['generated'])
        self.assertIsNotNone(metadata['verification'])
    
    def test_epr_verification(self):
        """Test entanglement verification"""
        state, metadata = self.generator.generate_epr_pair('phi_plus', verify=True)
        
        verification = metadata['verification']
        self.assertIn('is_entangled', verification)
        self.assertIn('fidelity', verification)
        self.assertIn('z_correlation', verification)
        self.assertIn('x_correlation', verification)
    
    def test_batch_epr_generation(self):
        """Test batch EPR pair generation"""
        epr_pairs, batch_metadata = self.generator.generate_epr_pairs(
            num_pairs=10,
            verify_sample=3
        )
        
        self.assertEqual(len(epr_pairs), 10)
        self.assertEqual(batch_metadata['num_pairs'], 10)
        self.assertLessEqual(batch_metadata['verified_count'], 10)
        self.assertGreaterEqual(batch_metadata['verified_count'], 0)
    
    def test_all_bell_states(self):
        """Test generation of all Bell state types"""
        for state_type in ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus']:
            state, metadata = self.generator.generate_epr_pair(state_type, verify=False)
            self.assertEqual(metadata['state_type'], state_type)
            self.assertEqual(state.shape, (4,))
    
    def test_epr_distribution(self):
        """Test EPR pair distribution"""
        epr_pairs, _ = self.generator.generate_epr_pairs(num_pairs=5)
        prover_particles, verifier_particles = self.generator.distribute_epr_pairs(epr_pairs)
        
        self.assertEqual(len(prover_particles), 5)
        self.assertEqual(len(verifier_particles), 5)
    
    def test_entanglement_monitoring(self):
        """Test entanglement quality monitoring"""
        epr_pairs, _ = self.generator.generate_epr_pairs(num_pairs=10)
        quality_report = self.generator.monitor_entanglement_quality(epr_pairs, sample_size=5)
        
        self.assertIn('sample_size', quality_report)
        self.assertIn('total_pairs', quality_report)
        self.assertLessEqual(quality_report['sample_size'], 10)
    
    def test_physical_epr_source(self):
        """Test physical EPR source with noise"""
        source = PhysicalEPRSource(self.backend)
        state, metadata = source.generate_physical_epr_pair('phi_plus')
        
        self.assertEqual(state.shape, (4,))
        self.assertTrue(metadata.get('noise_applied', False))
        self.assertIn('fidelity_after_noise', metadata)
    
    def test_quality_control(self):
        """Test quality-controlled generation"""
        source = PhysicalEPRSource(self.backend)
        epr_pairs, quality_metrics = source.generate_batch_with_quality_control(
            num_pairs=5,
            min_fidelity=0.8,
            max_attempts=3
        )
        
        self.assertEqual(len(epr_pairs), 5)
        self.assertIn('total_generated', quality_metrics)
        self.assertIn('accepted', quality_metrics)
        self.assertIn('average_fidelity', quality_metrics)
    
    def test_invalid_num_pairs(self):
        """Test error handling for invalid parameters"""
        with self.assertRaises(EntanglementError):
            self.generator.generate_epr_pairs(num_pairs=0)
        
        with self.assertRaises(EntanglementError):
            self.generator.generate_epr_pairs(num_pairs=-1)
    
    def test_fidelity_calculation(self):
        """Test fidelity calculation"""
        state, metadata = self.generator.generate_epr_pair('phi_plus', verify=True)
        verification = metadata['verification']
        
        fidelity = verification['fidelity']
        self.assertGreaterEqual(fidelity, 0)
        self.assertLessEqual(fidelity, 1)


if __name__ == '__main__':
    unittest.main()


