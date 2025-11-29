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
]

