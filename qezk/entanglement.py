"""
Quantum Entanglement Source

This module provides EPR pair generation and distribution for the QE-ZK protocol.
"""

import numpy as np
from typing import List, Tuple, Optional
from .quantum_state import QuantumStatePreparation


class EntanglementSource:
    """
    Quantum entanglement source - generates EPR pairs
    
    Creates entangled particle pairs (Bell states) and distributes them
    between Prover and Verifier for the QE-ZK protocol.
    """
    
    def __init__(self, quantum_prep: QuantumStatePreparation):
        """
        Initialize entanglement source
        
        Args:
            quantum_prep: QuantumStatePreparation instance for state creation
        """
        self.quantum_prep = quantum_prep
        self.random_seed = None
    
    def set_seed(self, seed: int):
        """
        Set random seed for reproducibility
        
        Args:
            seed: Random seed value
        """
        self.random_seed = seed
        np.random.seed(seed)
        import random
        random.seed(seed)
    
    def generate_epr_pairs(self, num_pairs: int, state_type: str = 'phi_plus') -> List[np.ndarray]:
        """
        Generate multiple EPR pairs (Bell states)
        
        Args:
            num_pairs: Number of EPR pairs to generate
            state_type: Type of Bell state ('phi_plus', 'phi_minus', 'psi_plus', 'psi_minus')
            
        Returns:
            List of 4-element arrays, each representing an entangled pair
        """
        epr_pairs = []
        for _ in range(num_pairs):
            bell_state = self.quantum_prep.create_bell_state(state_type)
            epr_pairs.append(bell_state)
        
        return epr_pairs
    
    def split_epr_pairs(self, epr_pairs: List[np.ndarray]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Split EPR pairs between Prover and Verifier
        
        In a real implementation, particles would be physically separated.
        Here we simulate by keeping track of which qubit belongs to whom.
        Prover gets first qubit, Verifier gets second qubit of each pair.
        
        Args:
            epr_pairs: List of EPR pairs (Bell states)
            
        Returns:
            Tuple of (prover_particles, verifier_particles)
            Both contain the same states, but represent different qubits
        """
        # In simulation, both parties have access to the full state
        # In real implementation, particles would be physically separated
        prover_particles = epr_pairs  # Prover has first qubit of each pair
        verifier_particles = epr_pairs  # Verifier has second qubit of each pair
        
        return prover_particles, verifier_particles

