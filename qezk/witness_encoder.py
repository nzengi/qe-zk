"""
Witness Encoder

This module converts classical witness (bit strings) into quantum operations
and determines measurement bases from statements.
"""

import hashlib
import numpy as np
from typing import List
from .quantum_state import QuantumStatePreparation
from .exceptions import WitnessEncodingError, ConfigurationError


class WitnessEncoder:
    """
    Encode classical witness into quantum operations
    
    Converts bit strings to quantum gate sequences and determines
    measurement bases from statement hashes.
    """
    
    def __init__(self, quantum_prep: QuantumStatePreparation):
        """
        Initialize witness encoder
        
        Args:
            quantum_prep: QuantumStatePreparation instance
        """
        self.quantum_prep = quantum_prep
        self.gate_library = {
            'I': quantum_prep.I,
            'X': quantum_prep.X,
            'Y': quantum_prep.Y,
            'Z': quantum_prep.Z,
            'H': quantum_prep.H,
            'S': np.array([[1, 0], [0, 1j]], dtype=complex),
            'T': np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex)
        }
        self.gate_names = list(self.gate_library.keys())
    
    def witness_to_quantum_circuit(self, witness: str) -> List[str]:
        """
        Convert classical witness (bit string) to quantum gate sequence
        
        Each 3 bits of the witness select a gate from the library.
        
        Args:
            witness: Binary string representing the witness
            
        Returns:
            List of gate names to apply
        """
        gate_sequence = []
        
        # Each 3 bits select a gate
        for i in range(0, len(witness), 3):
            bits = witness[i:i+3]
            if len(bits) < 3:
                bits = bits + '0' * (3 - len(bits))
            
            # Map bits to gate
            gate_index = int(bits, 2)
            gate_name = self.gate_names[gate_index % len(self.gate_names)]
            gate_sequence.append(gate_name)
        
        return gate_sequence
    
    def statement_to_bases(self, statement: str, num_measurements: int) -> List[str]:
        """
        Convert statement to measurement bases
        
        Uses SHA-256 hash of statement to deterministically select bases.
        This ensures the same statement always produces the same bases.
        
        Args:
            statement: String statement to prove
            num_measurements: Number of measurements needed
            
        Returns:
            List of measurement bases ('Z', 'X', or 'Y')
            
        Raises:
            WitnessEncodingError: If basis generation fails
            ConfigurationError: If parameters are invalid
        """
        try:
            # Input validation
            if not isinstance(statement, str):
                raise ConfigurationError(f"statement must be a string, got {type(statement)}")
            if not isinstance(num_measurements, int) or num_measurements < 1:
                raise ConfigurationError(f"num_measurements must be a positive integer, got {num_measurements}")
            
            # Hash statement
            statement_hash = hashlib.sha256(statement.encode()).digest()
            
            bases = []
            for i in range(num_measurements):
                # Use hash bits to choose basis
                byte_index = i % len(statement_hash)
                bit_shift = 2 * (i % 4)
                basis_index = (statement_hash[byte_index] >> bit_shift) & 0b11
                
                # Map to bases: 0=Z, 1=X, 2=Y, 3=Z (fallback)
                basis_map = {0: 'Z', 1: 'X', 2: 'Y', 3: 'Z'}
                bases.append(basis_map[basis_index])
            
            if len(bases) != num_measurements:
                raise WitnessEncodingError(f"Generated {len(bases)} bases, expected {num_measurements}")
            
            return bases
            
        except (ConfigurationError, WitnessEncodingError):
            raise
        except Exception as e:
            raise WitnessEncodingError(f"Basis generation failed: {str(e)}") from e
    
    def apply_circuit(self, state: np.ndarray, gate_sequence: List[str]) -> np.ndarray:
        """
        Apply gate sequence to quantum state
        
        Args:
            state: 4-element array representing 2-qubit state
            gate_sequence: List of gate names to apply
            
        Returns:
            Transformed quantum state
        """
        current_state = state.copy()
        
        for gate_name in gate_sequence:
            if gate_name in self.gate_library:
                gate = self.gate_library[gate_name]
                # Apply to first qubit (prover's qubit)
                current_state = self.quantum_prep.apply_gate(current_state, gate, qubit=0)
        
        return current_state

