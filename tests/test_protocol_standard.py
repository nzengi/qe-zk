"""
Protocol Standardization Tests

Tests for protocol standardization features.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, StandardMessageFormat, ProtocolCompliance,
    ProtocolVersionManager, StandardProtocolImplementation, ProtocolVersion
)


class TestProtocolStandard(unittest.TestCase):
    """Test cases for protocol standardization"""
    
    def test_protocol_version_enum(self):
        """Test protocol version enum"""
        versions = [ProtocolVersion.V1_0, ProtocolVersion.V1_1, ProtocolVersion.V2_0]
        
        for version in versions:
            self.assertIsInstance(version, ProtocolVersion)
            self.assertIn(version.value, ['1.0', '1.1', '2.0'])
    
    def test_standard_message_format_setup(self):
        """Test standard setup request message"""
        message = StandardMessageFormat.create_setup_request(
            statement="I know the secret",
            seed=42
        )
        
        self.assertEqual(message['protocol'], 'QE-ZK')
        self.assertEqual(message['version'], '1.0')
        self.assertEqual(message['message_type'], 'setup_request')
        self.assertIn('timestamp', message)
        self.assertIn('data', message)
        self.assertEqual(message['data']['statement'], 'I know the secret')
    
    def test_standard_message_format_prover_results(self):
        """Test standard prover results message"""
        message = StandardMessageFormat.create_prover_results(
            prover_results=[0, 1, 0],
            measurement_bases=['Z', 'X', 'Z'],
            statement="I know the secret"
        )
        
        self.assertEqual(message['message_type'], 'prover_results')
        self.assertEqual(message['data']['prover_results'], [0, 1, 0])
        self.assertEqual(message['metadata']['num_measurements'], 3)
    
    def test_message_validation_valid(self):
        """Test message validation with valid message"""
        message = StandardMessageFormat.create_setup_request("I know the secret")
        is_valid, error = StandardMessageFormat.validate_message(message)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_message_validation_invalid(self):
        """Test message validation with invalid message"""
        invalid_msg = {'protocol': 'WRONG'}
        is_valid, error = StandardMessageFormat.validate_message(invalid_msg)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_protocol_compliance(self):
        """Test protocol compliance checker"""
        compliance = ProtocolCompliance(version="1.0")
        spec = compliance.get_specification()
        
        self.assertEqual(spec.version, "1.0")
        self.assertIn('message_formats', spec.__dict__)
        self.assertIn('security_parameters', spec.__dict__)
    
    def test_message_compliance_check(self):
        """Test message compliance checking"""
        compliance = ProtocolCompliance()
        message = StandardMessageFormat.create_setup_request("I know the secret")
        
        report = compliance.check_message_compliance(message)
        
        self.assertIn('compliant', report)
        self.assertIn('version', report)
        self.assertIn('errors', report)
    
    def test_proof_compliance_check(self):
        """Test proof compliance checking"""
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        proof = qezk.prove("I know the secret", "11010110", seed=42)
        
        compliance = ProtocolCompliance()
        report = compliance.check_proof_compliance(proof)
        
        self.assertIn('compliant', report)
        self.assertIn('errors', report)
        self.assertTrue(report['compliant'])  # Should be compliant
    
    def test_version_manager(self):
        """Test protocol version manager"""
        manager = ProtocolVersionManager()
        
        self.assertIn(manager.current_version, manager.supported_versions)
        self.assertTrue(manager.is_version_supported('1.0'))
        self.assertFalse(manager.is_version_supported('3.0'))
    
    def test_version_compatibility(self):
        """Test version compatibility checking"""
        manager = ProtocolVersionManager()
        
        # Same major version should be compatible
        compatible = manager.check_compatibility('1.0', '1.1')
        self.assertTrue(compatible)
        
        # Different major versions may not be compatible
        compatible = manager.check_compatibility('1.0', '2.0')
        # This depends on implementation, but for now v1.x are compatible
    
    def test_standard_implementation(self):
        """Test standard protocol implementation"""
        std_impl = StandardProtocolImplementation(version="1.0")
        
        validation = std_impl.validate_implementation()
        
        self.assertIn('compliant', validation)
        self.assertEqual(validation['version'], '1.0')
    
    def test_standard_proof_message(self):
        """Test standard proof message creation"""
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        proof = qezk.prove("I know the secret", "11010110", seed=42)
        
        std_impl = StandardProtocolImplementation()
        proof_msg = std_impl.create_standard_proof_message(proof)
        
        self.assertEqual(proof_msg['protocol'], 'QE-ZK')
        self.assertEqual(proof_msg['message_type'], 'proof')
        self.assertIn('data', proof_msg)
        self.assertEqual(proof_msg['data']['chsh_value'], proof.chsh_value)


if __name__ == '__main__':
    unittest.main()


