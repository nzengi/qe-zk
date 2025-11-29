"""
Quantum Entanglement Zero-Knowledge (QE-ZK) System

A complete implementation of quantum entanglement-based zero-knowledge proofs.
"""

from .quantum_state import QuantumStatePreparation
from .entanglement import EntanglementSource
from .measurement import BellMeasurement
from .witness_encoder import WitnessEncoder
from .protocol import QuantumEntanglementZK, QEZKProof
from .security import QEZKSecurity
from .simulation import QEZKSimulation
from .exceptions import (
    QEZKError, QuantumStateError, EntanglementError, MeasurementError,
    ProtocolError, VerificationError, WitnessEncodingError,
    SecurityError, ConfigurationError
)
from .optimization import MemoryOptimizer, PerformanceOptimizer
from .security_proofs import SecurityProofFramework, FormalProofGenerator
from .hardware_interface import (
    QuantumHardwareBackend, SimulationBackend, IBMQBackend,
    GoogleQuantumAIBackend, HardwareInterface
)
from .hardware_protocol import HardwareQEZK
from .real_epr_generation import RealEPRGenerator, PhysicalEPRSource
from .physical_measurement import (
    MeasurementApparatus, StandardMeasurementApparatus,
    HighPrecisionMeasurementApparatus, AdaptiveMeasurementApparatus,
    MeasurementApparatusFactory
)
from .physical_protocol import PhysicalQEZK
from .distributed_protocol import (
    DistributedProver, DistributedVerifier, ProtocolMessage, MessageType
)
from .network_communication import (
    SecureConnection, ConnectionManager, MessageQueue,
    NetworkClient, NetworkServer, ConnectionConfig, ConnectionState
)
from .multi_party import (
    Party, PartyRole, MultiPartyProof, ThresholdVerifier,
    MultiProverProtocol, ConsensusProtocol, GroupProtocol, MultiPartyQEZK
)
from .protocol_standard import (
    ProtocolVersion, ProtocolSpecification, StandardMessageFormat,
    ProtocolCompliance, ProtocolVersionManager, StandardProtocolImplementation
)
from .recursive_proofs import (
    RecursiveProof, RecursiveProver, ProofComposer,
    NestedProofBuilder, ProofAggregator, RecursiveQEZK
)
from .proof_aggregation import (
    AggregationResult, AggregationStrategy, SimpleAggregationStrategy,
    WeightedAggregationStrategy, SelectiveAggregationStrategy, AdvancedProofAggregator
)
from .batch_verification import (
    BatchVerificationResult, VerificationCache, BatchVerifier, OptimizedBatchVerifier
)
from .quantum_network import (
    NodeType, ChannelState, QuantumNode, QuantumChannel, NetworkTopology,
    QuantumNetwork, QuantumNetworkProtocol, QuantumNetworkMonitor
)

__version__ = "1.0.0"
__all__ = [
    "QuantumStatePreparation",
    "EntanglementSource",
    "BellMeasurement",
    "WitnessEncoder",
    "QuantumEntanglementZK",
    "QEZKProof",
    "QEZKSecurity",
    "QEZKSimulation",
    "QEZKError",
    "QuantumStateError",
    "EntanglementError",
    "MeasurementError",
    "ProtocolError",
    "VerificationError",
    "WitnessEncodingError",
    "SecurityError",
    "ConfigurationError",
    "MemoryOptimizer",
    "PerformanceOptimizer",
    "SecurityProofFramework",
    "FormalProofGenerator",
    "QuantumHardwareBackend",
    "SimulationBackend",
    "IBMQBackend",
    "GoogleQuantumAIBackend",
    "HardwareInterface",
    "HardwareQEZK",
    "RealEPRGenerator",
    "PhysicalEPRSource",
    "MeasurementApparatus",
    "StandardMeasurementApparatus",
    "HighPrecisionMeasurementApparatus",
    "AdaptiveMeasurementApparatus",
    "MeasurementApparatusFactory",
    "PhysicalQEZK",
    "DistributedProver",
    "DistributedVerifier",
    "ProtocolMessage",
    "MessageType",
    "SecureConnection",
    "ConnectionManager",
    "MessageQueue",
    "NetworkClient",
    "NetworkServer",
    "ConnectionConfig",
    "ConnectionState",
    "Party",
    "PartyRole",
    "MultiPartyProof",
    "ThresholdVerifier",
    "MultiProverProtocol",
    "ConsensusProtocol",
    "GroupProtocol",
    "MultiPartyQEZK",
    "ProtocolVersion",
    "ProtocolSpecification",
    "StandardMessageFormat",
    "ProtocolCompliance",
    "ProtocolVersionManager",
    "StandardProtocolImplementation",
    "RecursiveProof",
    "RecursiveProver",
    "ProofComposer",
    "NestedProofBuilder",
    "ProofAggregator",
    "RecursiveQEZK",
    "AggregationResult",
    "AggregationStrategy",
    "SimpleAggregationStrategy",
    "WeightedAggregationStrategy",
    "SelectiveAggregationStrategy",
    "AdvancedProofAggregator",
    "BatchVerificationResult",
    "VerificationCache",
    "BatchVerifier",
    "OptimizedBatchVerifier",
    "NodeType",
    "ChannelState",
    "QuantumNode",
    "QuantumChannel",
    "NetworkTopology",
    "QuantumNetwork",
    "QuantumNetworkProtocol",
    "QuantumNetworkMonitor",
]

