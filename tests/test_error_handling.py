"""
Error Handling Tests

Tests for error handling and input validation in production scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, ConfigurationError, ProtocolError,
    EntanglementError, VerificationError, MeasurementError
)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling"""
    
    def test_invalid_epr_pairs(self):
        """Test invalid EPR pair count"""
        with self.assertRaises(ConfigurationError):
            QuantumEntanglementZK(num_epr_pairs=0)
        
        with self.assertRaises(ConfigurationError):
            QuantumEntanglementZK(num_epr_pairs=-1)
        
        with self.assertRaises(ConfigurationError):
            QuantumEntanglementZK(num_epr_pairs=2000000)  # Too large
    
    def test_invalid_chsh_threshold(self):
        """Test invalid CHSH threshold"""
        with self.assertRaises(ConfigurationError):
            QuantumEntanglementZK(chsh_threshold=-1)
        
        with self.assertRaises(ConfigurationError):
            QuantumEntanglementZK(chsh_threshold=5.0)  # Too large
    
    def test_invalid_statement(self):
        """Test invalid statement"""
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        witness = "11010110"
        
        with self.assertRaises(ProtocolError):
            qezk.prove("", witness)  # Empty statement
        
        with self.assertRaises(ProtocolError):
            qezk.prove(None, witness)  # None statement
    
    def test_invalid_witness(self):
        """Test invalid witness"""
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        statement = "I know the secret"
        
        # None witness should raise error
        with self.assertRaises(ProtocolError):
            qezk.prove(statement, None)
    
    def test_verification_errors(self):
        """Test verification error handling"""
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        
        # Mismatched lengths
        with self.assertRaises(VerificationError):
            qezk.verify([0, 1], [0], ['Z'])
        
        # Invalid results
        with self.assertRaises(VerificationError):
            qezk.verify([0, 2], [0, 1], ['Z', 'X'])  # Invalid result: 2
        
        # Invalid bases
        with self.assertRaises(VerificationError):
            qezk.verify([0, 1], [0, 1], ['Z', 'W'])  # Invalid basis: W
    
    def test_error_messages(self):
        """Test that error messages are informative"""
        try:
            QuantumEntanglementZK(num_epr_pairs=0)
        except ConfigurationError as e:
            self.assertIn("num_epr_pairs", str(e))
            self.assertIn("must be", str(e).lower())


if __name__ == '__main__':
    unittest.main()


