"""
QE-ZK Custom Exceptions

Custom exception classes for better error handling in production.
"""


class QEZKError(Exception):
    """Base exception for all QE-ZK errors"""
    pass


class QuantumStateError(QEZKError):
    """Error in quantum state preparation or manipulation"""
    pass


class EntanglementError(QEZKError):
    """Error in entanglement generation or distribution"""
    pass


class MeasurementError(QEZKError):
    """Error in quantum measurement"""
    pass


class ProtocolError(QEZKError):
    """Error in protocol execution"""
    pass


class VerificationError(QEZKError):
    """Error in proof verification"""
    pass


class WitnessEncodingError(QEZKError):
    """Error in witness encoding"""
    pass


class SecurityError(QEZKError):
    """Security-related error"""
    pass


class ConfigurationError(QEZKError):
    """Configuration or parameter error"""
    pass

