"""
QE-ZK Protocol Implementation

This module provides the complete Quantum Entanglement Zero-Knowledge protocol.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from .quantum_state import QuantumStatePreparation
from .entanglement import EntanglementSource
from .measurement import BellMeasurement
from .witness_encoder import WitnessEncoder


@dataclass
class QEZKProof:
    """
    QE-ZK proof data structure
    
    Contains all information about a generated proof.
    """
    prover_results: List[int]
    verifier_results: List[int]
    measurement_bases: List[str]
    chsh_value: float
    is_valid: bool
    statement: str


class QuantumEntanglementZK:
    """
    Complete Quantum Entanglement Zero-Knowledge System
    
    Implements the full QE-ZK protocol including setup, prover phase,
    verifier phase, and verification.
    """
    
    def __init__(self, num_epr_pairs: int = 10000, chsh_threshold: float = 2.2):
        """
        Initialize QE-ZK system
        
        Args:
            num_epr_pairs: Number of EPR pairs to use (default: 10000)
            chsh_threshold: CHSH value threshold for verification (default: 2.2)
                           Classical bound: 2.0, Quantum bound: 2.828
        """
        self.num_epr_pairs = num_epr_pairs
        self.chsh_threshold = chsh_threshold
        
        # Initialize components
        self.quantum_prep = QuantumStatePreparation()
        self.entanglement = EntanglementSource(self.quantum_prep)
        self.measurement = BellMeasurement()
        self.encoder = WitnessEncoder(self.quantum_prep)
    
    def setup(self, seed: Optional[int] = None) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Protocol setup phase
        
        Generates EPR pairs and distributes them between Prover and Verifier.
        
        Args:
            seed: Optional random seed for reproducibility
            
        Returns:
            Tuple of (prover_particles, verifier_particles)
        """
        if seed is not None:
            self.entanglement.set_seed(seed)
        
        # Generate EPR pairs
        epr_pairs = self.entanglement.generate_epr_pairs(self.num_epr_pairs)
        
        # Split between Prover and Verifier
        prover_particles, verifier_particles = self.entanglement.split_epr_pairs(epr_pairs)
        
        return prover_particles, verifier_particles
    
    def prover_phase(self, statement: str, witness: str, 
                    prover_particles: List[np.ndarray]) -> Tuple[List[int], List[str]]:
        """
        Prover's computation phase
        
        Prover encodes witness into quantum operations, applies them to particles,
        and measures in bases determined by the statement.
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information) as bit string
            prover_particles: Prover's share of EPR pairs
            
        Returns:
            Tuple of (measurement_results, measurement_bases)
        """
        # Convert witness to quantum circuit
        gate_sequence = self.encoder.witness_to_quantum_circuit(witness)
        
        # Get measurement bases from statement
        measurement_bases = self.encoder.statement_to_bases(statement, len(prover_particles))
        
        # Apply quantum operations and measure
        measurement_results = []
        for particle, basis in zip(prover_particles, measurement_bases):
            # Apply witness-encoded operations
            transformed_particle = self.encoder.apply_circuit(particle, gate_sequence)
            
            # Measure in specified basis
            result = self.measurement.measure(transformed_particle, basis)
            measurement_results.append(result)
        
        return measurement_results, measurement_bases
    
    def verifier_phase(self, statement: str, verifier_particles: List[np.ndarray], 
                      measurement_bases: List[str]) -> List[int]:
        """
        Verifier's computation phase
        
        Verifier measures particles in the same bases as Prover.
        
        Args:
            statement: Statement being proved
            verifier_particles: Verifier's share of EPR pairs
            measurement_bases: Bases used by Prover (must match)
            
        Returns:
            List of measurement results
        """
        # Measure in same bases as prover
        measurement_results = []
        for particle, basis in zip(verifier_particles, measurement_bases):
            result = self.measurement.measure(particle, basis)
            measurement_results.append(result)
        
        return measurement_results
    
    def verify(self, prover_results: List[int], verifier_results: List[int],
              measurement_bases: List[str]) -> Tuple[bool, float]:
        """
        Verification using CHSH inequality
        
        Verifies that entanglement was preserved and measurements are consistent.
        
        Args:
            prover_results: Prover's measurement results
            verifier_results: Verifier's measurement results
            measurement_bases: Measurement bases used
            
        Returns:
            Tuple of (is_valid, chsh_value)
        """
        # Convert bases to format for CHSH test
        alice_bases = measurement_bases
        bob_bases = measurement_bases  # Same bases
        
        # Calculate CHSH value
        chsh_value, correlation_matrix = self.measurement.chsh_inequality_test(
            prover_results, verifier_results, alice_bases, bob_bases
        )
        
        # Check if CHSH value exceeds classical bound (2.0)
        # Quantum bound is 2√2 ≈ 2.828
        is_entangled = chsh_value > self.chsh_threshold
        
        # Additional consistency check
        correlation = np.mean(np.array(prover_results) == np.array(verifier_results))
        consistency = correlation > 0.7  # 70% correlation threshold
        
        is_valid = is_entangled and consistency
        
        return is_valid, chsh_value
    
    def prove(self, statement: str, witness: str, seed: Optional[int] = None) -> QEZKProof:
        """
        Complete QE-ZK proof generation
        
        Executes the full protocol: setup, prover phase, verifier phase, and verification.
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information) as bit string
            seed: Optional random seed for reproducibility
            
        Returns:
            QEZKProof object containing all proof data
        """
        # Setup
        prover_particles, verifier_particles = self.setup(seed)
        
        # Prover phase
        prover_results, measurement_bases = self.prover_phase(statement, witness, prover_particles)
        
        # Verifier phase
        verifier_results = self.verifier_phase(statement, verifier_particles, measurement_bases)
        
        # Verification
        is_valid, chsh_value = self.verify(prover_results, verifier_results, measurement_bases)
        
        return QEZKProof(
            prover_results=prover_results,
            verifier_results=verifier_results,
            measurement_bases=measurement_bases,
            chsh_value=chsh_value,
            is_valid=is_valid,
            statement=statement
        )

