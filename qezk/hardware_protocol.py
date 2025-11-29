"""
Hardware-Integrated QE-ZK Protocol

Protocol implementation that uses real quantum hardware backends.
"""

from typing import Optional
from .protocol import QuantumEntanglementZK, QEZKProof
from .hardware_interface import HardwareInterface, QuantumHardwareBackend
from .exceptions import ProtocolError


class HardwareQEZK(QuantumEntanglementZK):
    """
    QE-ZK protocol with quantum hardware integration
    
    Extends the base QuantumEntanglementZK to work with real quantum hardware.
    """
    
    def __init__(self, 
                 hardware_backend: Optional[QuantumHardwareBackend] = None,
                 num_epr_pairs: int = 10000,
                 chsh_threshold: float = 2.2):
        """
        Initialize hardware-integrated QE-ZK system
        
        Args:
            hardware_backend: Quantum hardware backend (default: SimulationBackend)
            num_epr_pairs: Number of EPR pairs to use
            chsh_threshold: CHSH value threshold for verification
        """
        # Initialize base class with simulation (for compatibility)
        super().__init__(num_epr_pairs=num_epr_pairs, chsh_threshold=chsh_threshold)
        
        # Initialize hardware interface
        self.hardware = HardwareInterface(backend=hardware_backend)
        
        # Check if using real hardware
        backend_info = self.hardware.get_backend_info()
        self.is_real_hardware = not backend_info['is_simulation']
    
    def prove_with_hardware(self, 
                           statement: str, 
                           witness: str, 
                           seed: Optional[int] = None) -> QEZKProof:
        """
        Generate proof using quantum hardware
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information) as bit string
            seed: Optional random seed (may be ignored on real hardware)
            
        Returns:
            QEZKProof object containing all proof data
        """
        try:
            # Generate EPR pairs using hardware
            epr_pairs = self.hardware.generate_epr_pairs(self.num_epr_pairs)
            
            # Split pairs (in real hardware, particles are physically separated)
            prover_particles = epr_pairs
            verifier_particles = epr_pairs  # In simulation, same reference
            
            # Prover phase with hardware
            prover_results, measurement_bases = self._prover_phase_hardware(
                statement, witness, prover_particles
            )
            
            # Verifier phase with hardware
            verifier_results = self._verifier_phase_hardware(
                verifier_particles, measurement_bases
            )
            
            # Verification (same as base class)
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
            raise ProtocolError(f"Hardware proof generation failed: {str(e)}") from e
    
    def _prover_phase_hardware(self, statement: str, witness: str,
                               prover_particles) -> tuple:
        """Prover phase using hardware"""
        # Encode witness to gates
        gate_sequence = self.encoder.witness_to_quantum_circuit(witness)
        
        # Get measurement bases
        measurement_bases = self.encoder.statement_to_bases(statement, len(prover_particles))
        
        # Apply gates and measure using hardware
        measurement_results = []
        for i, (particle, basis) in enumerate(zip(prover_particles, measurement_bases)):
            # Apply witness-encoded gates
            for gate_name in gate_sequence:
                self.hardware.apply_quantum_gate(gate_name, 0)  # Apply to first qubit
            
            # Measure using hardware
            result = self.hardware.measure_particle(0, basis)
            measurement_results.append(result)
            
            # Reset for next particle (if needed)
            if i < len(prover_particles) - 1:
                self.hardware.backend.reset()
        
        return measurement_results, measurement_bases
    
    def _verifier_phase_hardware(self, verifier_particles, measurement_bases) -> list:
        """Verifier phase using hardware"""
        measurement_results = []
        
        for i, (particle, basis) in enumerate(zip(verifier_particles, measurement_bases)):
            # Measure using hardware (second qubit)
            result = self.hardware.measure_particle(1, basis)
            measurement_results.append(result)
            
            # Reset for next particle (if needed)
            if i < len(verifier_particles) - 1:
                self.hardware.backend.reset()
        
        return measurement_results

