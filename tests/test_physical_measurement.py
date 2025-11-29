"""
Physical Measurement Apparatus Tests

Tests for physical quantum measurement apparatus.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    StandardMeasurementApparatus, HighPrecisionMeasurementApparatus,
    AdaptiveMeasurementApparatus, MeasurementApparatusFactory,
    PhysicalQEZK, SimulationBackend
)
from qezk.exceptions import MeasurementError


class TestPhysicalMeasurement(unittest.TestCase):
    """Test cases for physical measurement apparatus"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.backend = SimulationBackend()
    
    def test_standard_apparatus_creation(self):
        """Test standard apparatus creation"""
        apparatus = StandardMeasurementApparatus(self.backend)
        self.assertIsNotNone(apparatus)
        self.assertIsNotNone(apparatus.backend)
    
    def test_calibration(self):
        """Test measurement apparatus calibration"""
        apparatus = StandardMeasurementApparatus(self.backend, auto_calibrate=False)
        calibration = apparatus.calibrate()
        
        self.assertTrue(calibration['success'])
        self.assertEqual(len(calibration['bases_calibrated']), 3)
        self.assertIn('Z', calibration['bases_calibrated'])
        self.assertIn('X', calibration['bases_calibrated'])
        self.assertIn('Y', calibration['bases_calibrated'])
    
    def test_measurement(self):
        """Test physical measurement"""
        apparatus = StandardMeasurementApparatus(self.backend)
        
        for basis in ['Z', 'X', 'Y']:
            result = apparatus.measure(0, basis)
            self.assertIn(result, [0, 1])
    
    def test_invalid_basis(self):
        """Test error handling for invalid basis"""
        apparatus = StandardMeasurementApparatus(self.backend)
        
        with self.assertRaises(MeasurementError):
            apparatus.measure(0, 'W')
    
    def test_measurement_statistics(self):
        """Test measurement statistics"""
        apparatus = StandardMeasurementApparatus(self.backend)
        
        # Perform some measurements
        for _ in range(10):
            apparatus.measure(0, 'Z')
        
        stats = apparatus.get_statistics()
        self.assertEqual(stats['total_measurements'], 10)
        self.assertGreaterEqual(stats['error_rate'], 0)
        self.assertLessEqual(stats['error_rate'], 1)
    
    def test_high_precision_apparatus(self):
        """Test high-precision measurement apparatus"""
        apparatus = HighPrecisionMeasurementApparatus(self.backend, shots=5)
        
        result = apparatus.measure(0, 'Z')
        self.assertIn(result, [0, 1])
        
        confidence = apparatus.get_measurement_confidence(0, 'Z')
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
    
    def test_adaptive_apparatus(self):
        """Test adaptive measurement apparatus"""
        apparatus = AdaptiveMeasurementApparatus(self.backend)
        
        # Perform measurements
        for _ in range(5):
            result = apparatus.measure(0, 'Z')
            self.assertIn(result, [0, 1])
        
        # Check that calibration occurred
        self.assertTrue(apparatus.is_calibrated)
    
    def test_factory_standard(self):
        """Test factory creation of standard apparatus"""
        apparatus = MeasurementApparatusFactory.create_standard(self.backend)
        self.assertIsInstance(apparatus, StandardMeasurementApparatus)
    
    def test_factory_high_precision(self):
        """Test factory creation of high-precision apparatus"""
        apparatus = MeasurementApparatusFactory.create_high_precision(self.backend, shots=7)
        self.assertIsInstance(apparatus, HighPrecisionMeasurementApparatus)
        self.assertEqual(apparatus.shots, 7)
    
    def test_factory_adaptive(self):
        """Test factory creation of adaptive apparatus"""
        apparatus = MeasurementApparatusFactory.create_adaptive(self.backend)
        self.assertIsInstance(apparatus, AdaptiveMeasurementApparatus)
    
    def test_physical_qezk(self):
        """Test physical QE-ZK protocol"""
        apparatus = StandardMeasurementApparatus(self.backend)
        qezk = PhysicalQEZK(
            hardware_backend=self.backend,
            measurement_apparatus=apparatus,
            num_epr_pairs=100
        )
        
        statement = "I know the secret"
        witness = "11010110"
        
        proof = qezk.prove_with_physical_measurement(statement, witness, seed=42)
        
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.prover_results), 100)
        self.assertEqual(len(proof.verifier_results), 100)
    
    def test_measurement_statistics_integration(self):
        """Test measurement statistics in physical protocol"""
        apparatus = StandardMeasurementApparatus(self.backend)
        qezk = PhysicalQEZK(
            hardware_backend=self.backend,
            measurement_apparatus=apparatus,
            num_epr_pairs=50
        )
        
        statement = "Test"
        witness = "1010"
        
        proof = qezk.prove_with_physical_measurement(statement, witness)
        
        stats = qezk.get_measurement_statistics()
        self.assertIn('total_measurements', stats)
        self.assertGreater(stats['total_measurements'], 0)


if __name__ == '__main__':
    unittest.main()


