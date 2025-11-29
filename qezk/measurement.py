"""
Bell Measurement Apparatus

This module provides quantum measurement operations and CHSH inequality testing
for entanglement verification in the QE-ZK protocol.
"""

import numpy as np
from typing import List, Tuple


class BellMeasurement:
    """
    Bell state measurement apparatus
    
    Provides quantum measurements in different bases and CHSH inequality
    testing for entanglement verification.
    """
    
    def __init__(self):
        """Initialize measurement bases"""
        # Measurement bases
        self.z_basis = np.array([[1, 0], [0, 1]], dtype=complex)  # Computational basis
        self.x_basis = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Hadamard basis
        self.y_basis = np.array([[1, 1j], [1, -1j]], dtype=complex) / np.sqrt(2)  # Circular basis
    
    def measure(self, state: np.ndarray, basis: str) -> int:
        """
        Quantum measurement in specified basis
        
        Args:
            state: 4-element array representing 2-qubit state
            basis: Measurement basis ('Z', 'X', or 'Y')
            
        Returns:
            Measurement outcome: 0 or 1
        """
        if basis == 'Z':
            # Computational basis measurement
            # Probability of |0⟩ is sum of |00⟩ and |01⟩ amplitudes squared
            prob_0 = np.abs(state[0])**2 + np.abs(state[2])**2
            outcome = 0 if np.random.random() < prob_0 else 1
            
        elif basis == 'X':
            # Hadamard basis measurement
            # Transform to X-basis
            x_basis_full = np.kron(self.x_basis, np.eye(2))
            transformed = x_basis_full @ state
            prob_0 = np.abs(transformed[0])**2 + np.abs(transformed[2])**2
            outcome = 0 if np.random.random() < prob_0 else 1
            
        elif basis == 'Y':
            # Circular basis measurement
            # Transform to Y-basis
            y_basis_full = np.kron(self.y_basis, np.eye(2))
            transformed = y_basis_full @ state
            prob_0 = np.abs(transformed[0])**2 + np.abs(transformed[2])**2
            outcome = 0 if np.random.random() < prob_0 else 1
            
        else:
            raise ValueError(f"Unknown basis: {basis}. Must be 'Z', 'X', or 'Y'")
        
        return outcome
    
    def bell_state_measurement(self, state: np.ndarray) -> Tuple[str, float]:
        """
        Complete Bell state measurement
        
        Determines which Bell state the given state is closest to.
        
        Args:
            state: 4-element array representing 2-qubit state
            
        Returns:
            Tuple of (Bell state name, probability)
        """
        # Bell state projectors
        bell_states = {
            'Φ⁺': np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2),
            'Φ⁻': np.array([1, 0, 0, -1], dtype=complex) / np.sqrt(2),
            'Ψ⁺': np.array([0, 1, 1, 0], dtype=complex) / np.sqrt(2),
            'Ψ⁻': np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
        }
        
        # Calculate overlaps (fidelity) with each Bell state
        overlaps = {}
        for name, bell_state in bell_states.items():
            overlap = np.abs(np.vdot(bell_state, state))**2
            overlaps[name] = overlap
        
        # Find most probable Bell state
        max_name = max(overlaps, key=overlaps.get)
        max_prob = overlaps[max_name]
        
        return max_name, max_prob
    
    def chsh_inequality_test(self, alice_results: List[int], bob_results: List[int],
                            alice_bases: List[str], bob_bases: List[str]) -> Tuple[float, np.ndarray]:
        """
        CHSH inequality test for entanglement verification
        
        The CHSH inequality is: S = E(0,0) - E(0,1) + E(1,0) + E(1,1)
        Classical bound: |S| ≤ 2
        Quantum bound: |S| ≤ 2√2 ≈ 2.828
        
        Args:
            alice_results: List of Alice's measurement results (0 or 1)
            bob_results: List of Bob's measurement results (0 or 1)
            alice_bases: List of Alice's measurement bases ('Z', 'X', 'Y')
            bob_bases: List of Bob's measurement bases ('Z', 'X', 'Y')
            
        Returns:
            Tuple of (CHSH value, 2x2 correlation matrix E)
        """
        # Convert bases to indices for correlation calculation
        basis_map = {'Z': 0, 'X': 1, 'Y': 2}
        
        # Calculate correlation coefficients E(a,b)
        E = np.zeros((2, 2))
        counts = np.zeros((2, 2))
        
        for a_result, b_result, a_basis, b_basis in zip(
            alice_results, bob_results, alice_bases, bob_bases
        ):
            # Only use Z and X bases for CHSH (standard protocol)
            if a_basis in ['Z', 'X'] and b_basis in ['Z', 'X']:
                a_chsh_idx = 0 if a_basis == 'Z' else 1
                b_chsh_idx = 0 if b_basis == 'Z' else 1
                
                # Correlation: +1 if same, -1 if different
                correlation = 1 if a_result == b_result else -1
                E[a_chsh_idx, b_chsh_idx] += correlation
                counts[a_chsh_idx, b_chsh_idx] += 1
        
        # Normalize by count
        for i in range(2):
            for j in range(2):
                if counts[i, j] > 0:
                    E[i, j] /= counts[i, j]
        
        # CHSH value: S = E(0,0) - E(0,1) + E(1,0) + E(1,1)
        S = E[0, 0] - E[0, 1] + E[1, 0] + E[1, 1]
        
        return abs(S), E

