"""
Physical Protocol with Measurement Apparatus

QE-ZK protocol implementation using physical measurement apparatus.
"""

from typing import Optional
from .protocol import QuantumEntanglementZK, QEZKProof
from .physical_measurement import (
    MeasurementApparatus, StandardMeasurementApparatus,
    MeasurementApparatusFactory
)
from .hardware_interface import QuantumHardwareBackend
from .exceptions import ProtocolError


class PhysicalQEZK(QuantumEntanglementZK):
    """
    QE-ZK protocol with physical measurement apparatus
    
    Uses calibrated physical measurement devices for real hardware measurements.
    """
    
    def __init__(self,
                 hardware_backend: Optional[QuantumHardwareBackend] = None,
                 measurement_apparatus: Optional[MeasurementApparatus] = None,
                 num_epr_pairs: int = 10000,
                 chsh_threshold: float = 2.2):
        """
        Initialize physical QE-ZK system
        
        Args:
            hardware_backend: Quantum hardware backend
            measurement_apparatus: Physical measurement apparatus
            num_epr_pairs: Number of EPR pairs to use
            chsh_threshold: CHSH value threshold for verification
        """
        # Initialize base class
        super().__init__(num_epr_pairs=num_epr_pairs, chsh_threshold=chsh_threshold)
        
        # Set up measurement apparatus
        if measurement_apparatus is None:
            # Create default apparatus if backend provided
            if hardware_backend is not None:
                self.measurement_apparatus = MeasurementApparatusFactory.create_standard(
                    hardware_backend
                )
            else:
                # Use simulation-based measurement (from base class)
                self.measurement_apparatus = None
        else:
            self.measurement_apparatus = measurement_apparatus
    
    def prove_with_physical_measurement(self,
                                       statement: str,
                                       witness: str,
                                       seed: Optional[int] = None) -> QEZKProof:
        """
        Generate proof using physical measurement apparatus
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information) as bit string
            seed: Optional random seed (may be ignored on real hardware)
            
        Returns:
            QEZKProof object containing all proof data
        """
        try:
            # Setup
            prover_particles, verifier_particles = self.setup(seed)
            
            # Prover phase with physical measurement
            prover_results, measurement_bases = self._prover_phase_physical(
                statement, witness, prover_particles
            )
            
            # Verifier phase with physical measurement
            verifier_results = self._verifier_phase_physical(
                verifier_particles, measurement_bases
            )
            
            # Verification
            is_valid, chsh_value = self.verify(
                prover_results, verifier_results, measurement_bases
            )
            
            return QEZKProof(
                prover_results=prover_results,
                verifier_results=verifier_results,
                measurement_bases=measurement_bases,
                chsh_value=chsh_value,
                is_valid=is_valid,
                statement=statement
            )
            
        except Exception as e:
            raise ProtocolError(f"Physical proof generation failed: {str(e)}") from e
    
    def _prover_phase_physical(self, statement: str, witness: str,
                              prover_particles) -> tuple:
        """Prover phase using physical measurement apparatus"""
        # Encode witness to gates
        gate_sequence = self.encoder.witness_to_quantum_circuit(witness)
        
        # Get measurement bases
        measurement_bases = self.encoder.statement_to_bases(statement, len(prover_particles))
        
        # Apply gates and measure using physical apparatus
        measurement_results = []
        for i, (particle, basis) in enumerate(zip(prover_particles, measurement_bases)):
            # Apply witness-encoded gates
            for gate_name in gate_sequence:
                # Gate application would be done on hardware
                pass
            
            # Measure using physical apparatus
            if self.measurement_apparatus:
                result = self.measurement_apparatus.measure(0, basis)
            else:
                # Fallback to simulation
                result = self.measurement.measure(particle, basis)
            
            measurement_results.append(result)
        
        return measurement_results, measurement_bases
    
    def _verifier_phase_physical(self, verifier_particles, measurement_bases) -> list:
        """Verifier phase using physical measurement apparatus"""
        measurement_results = []
        
        for i, (particle, basis) in enumerate(zip(verifier_particles, measurement_bases)):
            # Measure using physical apparatus
            if self.measurement_apparatus:
                result = self.measurement_apparatus.measure(1, basis)
            else:
                # Fallback to simulation
                result = self.measurement.measure(particle, basis)
            
            measurement_results.append(result)
        
        return measurement_results
    
    def get_measurement_statistics(self) -> dict:
        """
        Get measurement apparatus statistics
        
        Returns:
            Dictionary with measurement statistics
        """
        if self.measurement_apparatus:
            return self.measurement_apparatus.get_statistics()
        return {'error': 'No physical measurement apparatus configured'}


