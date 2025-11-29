"""
Protocol Standardization Example

Demonstrates QE-ZK protocol standardization features.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, StandardMessageFormat, ProtocolCompliance,
    ProtocolVersionManager, StandardProtocolImplementation, ProtocolVersion
)


def example_standard_message_format():
    """Example: Standard message format"""
    print("=" * 70)
    print("Example 1: Standard Message Format")
    print("=" * 70)
    print()
    
    # Create standard messages
    setup_msg = StandardMessageFormat.create_setup_request(
        statement="I know the secret",
        seed=42
    )
    
    print("Setup Request Message:")
    print(f"  Protocol: {setup_msg['protocol']}")
    print(f"  Version: {setup_msg['version']}")
    print(f"  Message Type: {setup_msg['message_type']}")
    print(f"  Statement: {setup_msg['data']['statement']}")
    print()
    
    # Prover results
    prover_results = [0, 1, 0, 1]
    measurement_bases = ['Z', 'X', 'Z', 'X']
    
    prover_msg = StandardMessageFormat.create_prover_results(
        prover_results=prover_results,
        measurement_bases=measurement_bases,
        statement="I know the secret"
    )
    
    print("Prover Results Message:")
    print(f"  Message Type: {prover_msg['message_type']}")
    print(f"  Num Measurements: {prover_msg['metadata']['num_measurements']}")
    print(f"  Bases Distribution: {prover_msg['metadata']['bases_distribution']}")
    print()


def example_message_validation():
    """Example: Message validation"""
    print("=" * 70)
    print("Example 2: Message Validation")
    print("=" * 70)
    print()
    
    # Valid message
    valid_msg = StandardMessageFormat.create_setup_request("I know the secret")
    is_valid, error = StandardMessageFormat.validate_message(valid_msg)
    
    print(f"Valid message: {is_valid}")
    if error:
        print(f"  Error: {error}")
    print()
    
    # Invalid message
    invalid_msg = {'protocol': 'WRONG', 'version': '1.0'}
    is_valid, error = StandardMessageFormat.validate_message(invalid_msg)
    
    print(f"Invalid message: {is_valid}")
    if error:
        print(f"  Error: {error}")
    print()


def example_protocol_compliance():
    """Example: Protocol compliance checking"""
    print("=" * 70)
    print("Example 3: Protocol Compliance")
    print("=" * 70)
    print()
    
    compliance = ProtocolCompliance(version="1.0")
    spec = compliance.get_specification()
    
    print("Protocol Specification:")
    print(f"  Name: {spec.name}")
    print(f"  Version: {spec.version}")
    print(f"  Description: {spec.description[:60]}...")
    print()
    
    print("Security Parameters:")
    for key, value in spec.security_parameters.items():
        print(f"  {key}: {value}")
    print()
    
    # Check message compliance
    message = StandardMessageFormat.create_setup_request("I know the secret")
    report = compliance.check_message_compliance(message)
    
    print("Message Compliance Check:")
    print(f"  Compliant: {report['compliant']}")
    if report['errors']:
        print(f"  Errors: {report['errors']}")
    print()


def example_proof_compliance():
    """Example: Proof compliance checking"""
    print("=" * 70)
    print("Example 4: Proof Compliance")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    proof = qezk.prove("I know the secret", "11010110", seed=42)
    
    compliance = ProtocolCompliance()
    report = compliance.check_proof_compliance(proof)
    
    print("Proof Compliance Check:")
    print(f"  Compliant: {report['compliant']}")
    if report['errors']:
        print(f"  Errors: {report['errors']}")
    if report['warnings']:
        print(f"  Warnings: {report['warnings']}")
    print()


def example_version_management():
    """Example: Protocol version management"""
    print("=" * 70)
    print("Example 5: Version Management")
    print("=" * 70)
    print()
    
    version_manager = ProtocolVersionManager()
    
    print("Version Management:")
    print(f"  Current version: {version_manager.current_version}")
    print(f"  Latest version: {version_manager.get_latest_version()}")
    print(f"  Supported versions: {version_manager.supported_versions}")
    print()
    
    # Check version support
    print("Version Support:")
    for version in ['1.0', '1.1', '2.0']:
        supported = version_manager.is_version_supported(version)
        print(f"  {version}: {'✓' if supported else '✗'}")
    print()
    
    # Check compatibility
    print("Version Compatibility:")
    compatible = version_manager.check_compatibility('1.0', '1.1')
    print(f"  1.0 <-> 1.1: {'✓ Compatible' if compatible else '✗ Incompatible'}")
    print()


def example_standard_implementation():
    """Example: Standard protocol implementation"""
    print("=" * 70)
    print("Example 6: Standard Implementation")
    print("=" * 70)
    print()
    
    std_impl = StandardProtocolImplementation(version="1.0")
    
    # Validate implementation
    validation = std_impl.validate_implementation()
    
    print("Implementation Validation:")
    print(f"  Compliant: {validation['compliant']}")
    print(f"  Version: {validation['version']}")
    print("  Checks:")
    for check in validation['checks']:
        print(f"    {check}")
    if validation['errors']:
        print("  Errors:")
        for error in validation['errors']:
            print(f"    {error}")
    print()
    
    # Create standard proof message
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    proof = qezk.prove("I know the secret", "11010110", seed=42)
    
    proof_msg = std_impl.create_standard_proof_message(proof)
    
    print("Standard Proof Message:")
    print(f"  Protocol: {proof_msg['protocol']}")
    print(f"  Version: {proof_msg['version']}")
    print(f"  CHSH Value: {proof_msg['data']['chsh_value']:.4f}")
    print(f"  Is Valid: {proof_msg['data']['is_valid']}")
    print()


def main():
    """Run all examples"""
    example_standard_message_format()
    example_message_validation()
    example_protocol_compliance()
    example_proof_compliance()
    example_version_management()
    example_standard_implementation()
    
    print("=" * 70)
    print("Protocol Standardization Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


