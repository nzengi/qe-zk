"""
Quantum State Preparation and Manipulation

This module provides quantum state preparation, gate operations, and Bell state generation.
"""

import numpy as np
from typing import Literal
from .exceptions import QuantumStateError


class QuantumStatePreparation:
    """
    Quantum state preparation and manipulation
    
    Provides quantum gates and operations for creating and manipulating
    quantum states, particularly Bell states for entanglement.
    """
    
    def __init__(self):
        """Initialize quantum gates"""
        # Single-qubit gates
        self.H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Hadamard
        self.X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X
        self.Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y
        self.Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
        self.I = np.eye(2, dtype=complex)  # Identity
        
        # Two-qubit CNOT gate
        self.CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
    
    def create_bell_state(self, state_type: Literal['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus'] = 'phi_plus') -> np.ndarray:
        """
        Create Bell states: |Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩
        
        Args:
            state_type: Type of Bell state to create
            
        Returns:
            4-element complex array representing the 2-qubit Bell state
        """
        # Start with |00⟩ = [1, 0, 0, 0]
        state = np.array([1, 0, 0, 0], dtype=complex)
        
        # Apply Hadamard to first qubit: (H ⊗ I)|00⟩
        H_full = np.kron(self.H, self.I)
        state = H_full @ state
        
        # Apply CNOT: CNOT(H ⊗ I)|00⟩ = |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
        state = self.CNOT @ state
        
        # Apply additional gates for other Bell states
        if state_type == 'phi_minus':
            # |Φ⁻⟩ = (|00⟩ - |11⟩)/√2
            Z_full = np.kron(self.Z, self.I)
            state = Z_full @ state
        elif state_type == 'psi_plus':
            # |Ψ⁺⟩ = (|01⟩ + |10⟩)/√2
            X_full = np.kron(self.X, self.I)
            state = X_full @ state
        elif state_type == 'psi_minus':
            # |Ψ⁻⟩ = (|01⟩ - |10⟩)/√2
            Y_full = np.kron(self.Y, self.I)
            state = Y_full @ state
        
        return state
    
    def apply_gate(self, state: np.ndarray, gate: np.ndarray, qubit: int = 0) -> np.ndarray:
        """
        Apply single-qubit gate to 2-qubit state
        
        Args:
            state: 4-element array representing 2-qubit state
            gate: 2x2 matrix representing single-qubit gate
            qubit: Which qubit to apply gate to (0 or 1)
            
        Returns:
            Transformed quantum state
            
        Raises:
            QuantumStateError: If gate application fails
        """
        try:
            # Input validation
            if state.shape != (4,):
                raise QuantumStateError(f"State must be 4-element array, got shape {state.shape}")
            if gate.shape != (2, 2):
                raise QuantumStateError(f"Gate must be 2x2 matrix, got shape {gate.shape}")
            if qubit not in [0, 1]:
                raise QuantumStateError(f"Qubit must be 0 or 1, got {qubit}")
            
            if qubit == 0:
                # Apply gate to first qubit: gate ⊗ I
                gate_full = np.kron(gate, self.I)
            else:
                # Apply gate to second qubit: I ⊗ gate
                gate_full = np.kron(self.I, gate)
            
            result = gate_full @ state
            
            # Validate result
            if result.shape != (4,):
                raise QuantumStateError(f"Result shape mismatch: {result.shape}")
            
            return result
            
        except QuantumStateError:
            raise
        except Exception as e:
            raise QuantumStateError(f"Gate application failed: {str(e)}") from e
    
    def normalize_state(self, state: np.ndarray) -> np.ndarray:
        """
        Normalize quantum state to unit length
        
        Args:
            state: Quantum state vector
            
        Returns:
            Normalized quantum state
        """
        norm = np.sqrt(np.sum(np.abs(state)**2))
        if norm > 1e-10:
            return state / norm
        return state

