"""
QE-ZK Protocol Standardization

Protocol specification, versioning, and standardization for QE-ZK.
Includes RFC-style specification, message format standards, and compliance testing.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from .protocol import QEZKProof
from .exceptions import ProtocolError, ConfigurationError


class ProtocolVersion(Enum):
    """QE-ZK protocol versions"""
    V1_0 = "1.0"
    V1_1 = "1.1"  # Future version
    V2_0 = "2.0"  # Future version


@dataclass
class ProtocolSpecification:
    """QE-ZK protocol specification"""
    version: str
    name: str
    description: str
    message_formats: Dict[str, Dict[str, Any]]
    protocol_steps: List[str]
    security_parameters: Dict[str, Any]
    compliance_requirements: List[str]
    
    def to_json(self) -> str:
        """Serialize specification to JSON"""
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProtocolSpecification':
        """Deserialize specification from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class StandardMessageFormat:
    """
    Standard message format for QE-ZK protocol
    
    Ensures interoperability between different implementations.
    """
    
    @staticmethod
    def create_setup_request(statement: str, seed: Optional[int] = None,
                           version: str = "1.0") -> Dict[str, Any]:
        """
        Create standard setup request message
        
        Args:
            statement: Statement to prove
            seed: Optional random seed
            version: Protocol version
            
        Returns:
            Standardized message dictionary
        """
        return {
            'protocol': 'QE-ZK',
            'version': version,
            'message_type': 'setup_request',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'statement': statement,
                'seed': seed
            },
            'metadata': {
                'message_id': hashlib.sha256(
                    f"{statement}{seed}{datetime.utcnow().isoformat()}".encode()
                ).hexdigest()[:16]
            }
        }
    
    @staticmethod
    def create_prover_results(prover_results: List[int],
                             measurement_bases: List[str],
                             statement: str,
                             version: str = "1.0") -> Dict[str, Any]:
        """
        Create standard prover results message
        
        Args:
            prover_results: Prover's measurement results
            measurement_bases: Measurement bases used
            statement: Statement being proved
            version: Protocol version
            
        Returns:
            Standardized message dictionary
        """
        return {
            'protocol': 'QE-ZK',
            'version': version,
            'message_type': 'prover_results',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'prover_results': prover_results,
                'measurement_bases': measurement_bases,
                'statement': statement
            },
            'metadata': {
                'num_measurements': len(prover_results),
                'bases_distribution': {
                    'Z': measurement_bases.count('Z'),
                    'X': measurement_bases.count('X'),
                    'Y': measurement_bases.count('Y')
                }
            }
        }
    
    @staticmethod
    def create_verification_request(prover_results: List[int],
                                   verifier_results: List[int],
                                   measurement_bases: List[str],
                                   version: str = "1.0") -> Dict[str, Any]:
        """
        Create standard verification request message
        
        Args:
            prover_results: Prover's measurement results
            verifier_results: Verifier's measurement results
            measurement_bases: Measurement bases used
            version: Protocol version
            
        Returns:
            Standardized message dictionary
        """
        return {
            'protocol': 'QE-ZK',
            'version': version,
            'message_type': 'verification_request',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'prover_results': prover_results,
                'verifier_results': verifier_results,
                'measurement_bases': measurement_bases
            },
            'metadata': {
                'num_measurements': len(prover_results),
                'results_match': sum(
                    1 for p, v in zip(prover_results, verifier_results) if p == v
                )
            }
        }
    
    @staticmethod
    def create_verification_response(is_valid: bool,
                                    chsh_value: float,
                                    statement: str,
                                    version: str = "1.0") -> Dict[str, Any]:
        """
        Create standard verification response message
        
        Args:
            is_valid: Whether proof is valid
            chsh_value: CHSH inequality value
            statement: Statement that was verified
            version: Protocol version
            
        Returns:
            Standardized message dictionary
        """
        return {
            'protocol': 'QE-ZK',
            'version': version,
            'message_type': 'verification_response',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'is_valid': is_valid,
                'chsh_value': chsh_value,
                'statement': statement
            },
            'metadata': {
                'verification_timestamp': datetime.utcnow().isoformat(),
                'chsh_threshold': 2.2,
                'classical_bound': 2.0,
                'quantum_bound': 2.828
            }
        }
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate message format
        
        Args:
            message: Message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['protocol', 'version', 'message_type', 'timestamp', 'data']
        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"
        
        # Check protocol name
        if message['protocol'] != 'QE-ZK':
            return False, f"Invalid protocol: {message['protocol']}"
        
        # Check version
        if message['version'] not in [v.value for v in ProtocolVersion]:
            return False, f"Unsupported version: {message['version']}"
        
        # Check message type
        valid_types = [
            'setup_request', 'setup_response', 'prover_results',
            'verifier_results', 'verification_request', 'verification_response',
            'error', 'heartbeat'
        ]
        if message['message_type'] not in valid_types:
            return False, f"Invalid message type: {message['message_type']}"
        
        return True, None


class ProtocolCompliance:
    """
    Protocol compliance checker
    
    Verifies that implementations comply with QE-ZK protocol standard.
    """
    
    def __init__(self, version: str = "1.0"):
        """
        Initialize compliance checker
        
        Args:
            version: Protocol version to check against
        """
        self.version = version
        self.specification = self._load_specification(version)
    
    def _load_specification(self, version: str) -> ProtocolSpecification:
        """Load protocol specification for version"""
        # Default specification for v1.0
        return ProtocolSpecification(
            version=version,
            name="Quantum Entanglement Zero-Knowledge Protocol",
            description="Information-theoretic perfect zero-knowledge protocol using quantum entanglement",
            message_formats={
                'setup_request': {
                    'required_fields': ['statement'],
                    'optional_fields': ['seed']
                },
                'prover_results': {
                    'required_fields': ['prover_results', 'measurement_bases', 'statement'],
                    'optional_fields': []
                },
                'verification_request': {
                    'required_fields': ['prover_results', 'verifier_results', 'measurement_bases'],
                    'optional_fields': []
                },
                'verification_response': {
                    'required_fields': ['is_valid', 'chsh_value', 'statement'],
                    'optional_fields': []
                }
            },
            protocol_steps=[
                '1. Setup: Generate and distribute EPR pairs',
                '2. Prover Phase: Encode witness, apply operations, measure',
                '3. Verifier Phase: Measure particles in same bases',
                '4. Verification: Calculate CHSH inequality'
            ],
            security_parameters={
                'chsh_threshold': 2.2,
                'classical_bound': 2.0,
                'quantum_bound': 2.828,
                'correlation_threshold': 0.7,
                'min_epr_pairs': 1,
                'max_epr_pairs': 1000000
            },
            compliance_requirements=[
                'Message format compliance',
                'Protocol step compliance',
                'Security parameter compliance',
                'CHSH calculation compliance',
                'Measurement basis compliance'
            ]
        )
    
    def check_message_compliance(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check message format compliance
        
        Args:
            message: Message to check
            
        Returns:
            Compliance report
        """
        is_valid, error = StandardMessageFormat.validate_message(message)
        
        report = {
            'compliant': is_valid,
            'version': self.version,
            'errors': [],
            'warnings': []
        }
        
        if not is_valid:
            report['errors'].append(error)
            return report
        
        # Check message type specific requirements
        message_type = message['message_type']
        if message_type in self.specification.message_formats:
            format_spec = self.specification.message_formats[message_type]
            
            # Check required fields
            data = message.get('data', {})
            for field in format_spec['required_fields']:
                if field not in data:
                    report['errors'].append(f"Missing required field in data: {field}")
                    report['compliant'] = False
        
        return report
    
    def check_proof_compliance(self, proof: QEZKProof) -> Dict[str, Any]:
        """
        Check proof compliance with protocol standard
        
        Args:
            proof: QEZKProof to check
            
        Returns:
            Compliance report
        """
        report = {
            'compliant': True,
            'errors': [],
            'warnings': []
        }
        
        # Check proof structure
        required_fields = ['prover_results', 'verifier_results', 'measurement_bases',
                          'chsh_value', 'is_valid', 'statement']
        for field in required_fields:
            if not hasattr(proof, field):
                report['errors'].append(f"Missing proof field: {field}")
                report['compliant'] = False
        
        # Check measurement results
        if hasattr(proof, 'prover_results'):
            for result in proof.prover_results:
                if result not in [0, 1]:
                    report['errors'].append(f"Invalid prover result: {result}")
                    report['compliant'] = False
        
        if hasattr(proof, 'verifier_results'):
            for result in proof.verifier_results:
                if result not in [0, 1]:
                    report['errors'].append(f"Invalid verifier result: {result}")
                    report['compliant'] = False
        
        # Check measurement bases
        if hasattr(proof, 'measurement_bases'):
            valid_bases = {'Z', 'X', 'Y'}
            for basis in proof.measurement_bases:
                if basis not in valid_bases:
                    report['errors'].append(f"Invalid measurement basis: {basis}")
                    report['compliant'] = False
        
        # Check CHSH value range
        if hasattr(proof, 'chsh_value'):
            if not (0 <= proof.chsh_value <= 3.0):
                report['warnings'].append(f"CHSH value out of expected range: {proof.chsh_value}")
        
        return report
    
    def get_specification(self) -> ProtocolSpecification:
        """Get protocol specification"""
        return self.specification


class ProtocolVersionManager:
    """
    Protocol version manager
    
    Handles protocol versioning and compatibility.
    """
    
    def __init__(self):
        """Initialize version manager"""
        self.supported_versions = [v.value for v in ProtocolVersion]
        self.current_version = ProtocolVersion.V1_0.value
    
    def is_version_supported(self, version: str) -> bool:
        """
        Check if version is supported
        
        Args:
            version: Version to check
            
        Returns:
            True if supported
        """
        return version in self.supported_versions
    
    def get_latest_version(self) -> str:
        """Get latest protocol version"""
        return max(self.supported_versions)
    
    def check_compatibility(self, version1: str, version2: str) -> bool:
        """
        Check compatibility between versions
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            True if compatible
        """
        # For now, all v1.x versions are compatible
        major1 = version1.split('.')[0]
        major2 = version2.split('.')[0]
        return major1 == major2
    
    def upgrade_message(self, message: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """
        Upgrade message to target version
        
        Args:
            message: Message to upgrade
            target_version: Target version
            
        Returns:
            Upgraded message
        """
        if not self.is_version_supported(target_version):
            raise ConfigurationError(f"Unsupported target version: {target_version}")
        
        upgraded = message.copy()
        upgraded['version'] = target_version
        
        # Version-specific upgrades would go here
        # For now, just update version field
        
        return upgraded


class StandardProtocolImplementation:
    """
    Standard protocol implementation
    
    Reference implementation following protocol standard.
    """
    
    def __init__(self, version: str = "1.0"):
        """
        Initialize standard implementation
        
        Args:
            version: Protocol version
        """
        self.version = version
        self.compliance = ProtocolCompliance(version)
        self.version_manager = ProtocolVersionManager()
    
    def create_standard_proof_message(self, proof: QEZKProof) -> Dict[str, Any]:
        """
        Create standard proof message
        
        Args:
            proof: QEZKProof to convert
            
        Returns:
            Standardized proof message
        """
        return {
            'protocol': 'QE-ZK',
            'version': self.version,
            'message_type': 'proof',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'prover_results': proof.prover_results,
                'verifier_results': proof.verifier_results,
                'measurement_bases': proof.measurement_bases,
                'chsh_value': proof.chsh_value,
                'is_valid': proof.is_valid,
                'statement': proof.statement
            },
            'metadata': {
                'num_measurements': len(proof.prover_results),
                'protocol_version': self.version
            }
        }
    
    def validate_implementation(self) -> Dict[str, Any]:
        """
        Validate implementation compliance
        
        Returns:
            Validation report
        """
        report = {
            'compliant': True,
            'version': self.version,
            'checks': [],
            'errors': []
        }
        
        # Check version support
        if not self.version_manager.is_version_supported(self.version):
            report['compliant'] = False
            report['errors'].append(f"Unsupported version: {self.version}")
        
        # Check specification availability
        spec = self.compliance.get_specification()
        if spec.version != self.version:
            report['compliant'] = False
            report['errors'].append("Specification version mismatch")
        
        report['checks'].append('Version support: ✓')
        report['checks'].append('Specification: ✓')
        
        return report

