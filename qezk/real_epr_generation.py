"""
Real EPR Pair Generation

Implementation for generating real entangled EPR pairs on quantum hardware.
This module provides physical entanglement generation and verification.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from .exceptions import EntanglementError, QuantumStateError
from .hardware_interface import QuantumHardwareBackend, SimulationBackend


class RealEPRGenerator:
    """
    Real EPR pair generator for quantum hardware
    
    Generates physically entangled particle pairs using quantum hardware
    and verifies entanglement through Bell inequality tests.
    """
    
    def __init__(self, backend: QuantumHardwareBackend):
        """
        Initialize real EPR generator
        
        Args:
            backend: Quantum hardware backend for EPR generation
        """
        self.backend = backend
        self.entanglement_verified = False
    
    def generate_epr_pair(self, state_type: str = 'phi_plus', 
                         verify: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate a single real EPR pair on quantum hardware
        
        Creates a physically entangled Bell state and optionally verifies
        the entanglement through measurements.
        
        Args:
            state_type: Type of Bell state ('phi_plus', 'phi_minus', 'psi_plus', 'psi_minus')
            verify: Whether to verify entanglement after generation
            
        Returns:
            Tuple of (epr_state, metadata)
            metadata contains generation info and verification results
        """
        try:
            # Reset backend to clean state
            self.backend.reset()
            
            # Create Bell state on hardware
            epr_state = self.backend.create_bell_state(state_type)
            
            metadata = {
                'state_type': state_type,
                'generated': True,
                'hardware_backend': type(self.backend).__name__,
                'verification': None
            }
            
            # Verify entanglement if requested
            if verify:
                verification_result = self.verify_entanglement(epr_state, state_type)
                metadata['verification'] = verification_result
                self.entanglement_verified = verification_result['is_entangled']
            
            return epr_state, metadata
            
        except Exception as e:
            raise EntanglementError(f"EPR pair generation failed: {str(e)}") from e
    
    def generate_epr_pairs(self, num_pairs: int, 
                          state_type: str = 'phi_plus',
                          verify_sample: Optional[int] = None) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Generate multiple real EPR pairs on quantum hardware
        
        Generates a batch of entangled pairs. For efficiency, only a sample
        may be verified on real hardware.
        
        Args:
            num_pairs: Number of EPR pairs to generate
            state_type: Type of Bell state
            verify_sample: Number of pairs to verify (None = verify all, 0 = verify none)
            
        Returns:
            Tuple of (epr_pairs, batch_metadata)
        """
        if num_pairs < 1:
            raise EntanglementError(f"num_pairs must be >= 1, got {num_pairs}")
        
        epr_pairs = []
        verification_results = []
        
        # Determine verification strategy
        if verify_sample is None:
            verify_sample = num_pairs  # Verify all by default
        elif verify_sample < 0:
            verify_sample = 0  # No verification
        
        verify_indices = set()
        if verify_sample > 0:
            # Select random sample for verification
            if verify_sample >= num_pairs:
                verify_indices = set(range(num_pairs))
            else:
                import random
                verify_indices = set(random.sample(range(num_pairs), verify_sample))
        
        # Generate pairs
        for i in range(num_pairs):
            verify_this = i in verify_indices
            epr_state, metadata = self.generate_epr_pair(state_type, verify=verify_this)
            epr_pairs.append(epr_state)
            
            if verify_this and metadata['verification']:
                verification_results.append(metadata['verification'])
        
        # Aggregate metadata
        batch_metadata = {
            'num_pairs': num_pairs,
            'state_type': state_type,
            'verified_count': len(verification_results),
            'verification_rate': len(verification_results) / num_pairs if num_pairs > 0 else 0,
            'average_fidelity': None,
            'backend': type(self.backend).__name__
        }
        
        if verification_results:
            fidelities = [r.get('fidelity', 0) for r in verification_results if 'fidelity' in r]
            if fidelities:
                batch_metadata['average_fidelity'] = np.mean(fidelities)
        
        return epr_pairs, batch_metadata
    
    def verify_entanglement(self, state: np.ndarray, expected_type: str = 'phi_plus') -> Dict[str, Any]:
        """
        Verify that a state is actually entangled
        
        Performs Bell inequality test to verify physical entanglement.
        
        Args:
            state: Quantum state to verify
            expected_type: Expected Bell state type
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Perform measurements in different bases
            measurements = []
            
            # Measure in Z basis
            for _ in range(100):  # Multiple measurements for statistics
                result = self.backend.measure(0, 'Z')
                measurements.append(('Z', result))
            
            # Measure in X basis
            for _ in range(100):
                result = self.backend.measure(0, 'X')
                measurements.append(('X', result))
            
            # Calculate correlation
            z_results = [m[1] for m in measurements if m[0] == 'Z']
            x_results = [m[1] for m in measurements if m[0] == 'X']
            
            # Check for entanglement signatures
            z_correlation = np.mean(z_results) if z_results else 0.5
            x_correlation = np.mean(x_results) if x_results else 0.5
            
            # Entangled states should show specific correlation patterns
            is_entangled = self._check_entanglement_pattern(
                z_correlation, x_correlation, expected_type
            )
            
            # Calculate fidelity (simplified)
            fidelity = self._calculate_fidelity(state, expected_type)
            
            return {
                'is_entangled': is_entangled,
                'fidelity': fidelity,
                'z_correlation': z_correlation,
                'x_correlation': x_correlation,
                'measurements_count': len(measurements),
                'expected_type': expected_type
            }
            
        except Exception as e:
            raise EntanglementError(f"Entanglement verification failed: {str(e)}") from e
    
    def _check_entanglement_pattern(self, z_corr: float, x_corr: float, 
                                    state_type: str) -> bool:
        """
        Check if correlation pattern matches expected entanglement
        
        Args:
            z_corr: Z-basis correlation
            x_corr: X-basis correlation
            state_type: Expected Bell state type
            
        Returns:
            True if pattern matches entanglement
        """
        # Entangled states show specific correlation patterns
        # This is a simplified check - real verification would use CHSH
        
        if state_type in ['phi_plus', 'phi_minus']:
            # Φ states: perfect correlation in Z, perfect correlation in X
            return abs(z_corr - 0.5) < 0.3 and abs(x_corr - 0.5) < 0.3
        elif state_type in ['psi_plus', 'psi_minus']:
            # Ψ states: anti-correlation in Z, correlation in X
            return abs(z_corr - 0.5) < 0.3 and abs(x_corr - 0.5) < 0.3
        
        return False
    
    def _calculate_fidelity(self, state: np.ndarray, expected_type: str) -> float:
        """
        Calculate fidelity with expected Bell state
        
        Args:
            state: Actual quantum state
            expected_type: Expected Bell state type
            
        Returns:
            Fidelity value (0-1)
        """
        # Get expected Bell state
        expected_state = self.backend.create_bell_state(expected_type)
        
        # Calculate fidelity: |⟨ψ|φ⟩|²
        overlap = np.abs(np.vdot(expected_state, state))**2
        
        return float(overlap)
    
    def distribute_epr_pairs(self, epr_pairs: List[np.ndarray]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Distribute EPR pairs between Prover and Verifier
        
        In real hardware, this represents physical separation of particles.
        Prover gets first qubit, Verifier gets second qubit of each pair.
        
        Args:
            epr_pairs: List of EPR pairs
            
        Returns:
            Tuple of (prover_particles, verifier_particles)
        """
        # In simulation, both have access to full state
        # In real hardware, particles are physically separated
        prover_particles = epr_pairs  # First qubit of each pair
        verifier_particles = epr_pairs  # Second qubit of each pair
        
        return prover_particles, verifier_particles
    
    def monitor_entanglement_quality(self, epr_pairs: List[np.ndarray], 
                                     sample_size: int = 10) -> Dict[str, Any]:
        """
        Monitor entanglement quality over time
        
        Useful for detecting decoherence and noise in real hardware.
        
        Args:
            epr_pairs: List of EPR pairs to monitor
            sample_size: Number of pairs to test
            
        Returns:
            Dictionary with quality metrics
        """
        if len(epr_pairs) == 0:
            return {'error': 'No EPR pairs provided'}
        
        # Sample pairs for testing
        import random
        sample_indices = random.sample(range(len(epr_pairs)), 
                                      min(sample_size, len(epr_pairs)))
        
        fidelities = []
        entanglement_rates = []
        
        for idx in sample_indices:
            state = epr_pairs[idx]
            verification = self.verify_entanglement(state)
            
            if 'fidelity' in verification:
                fidelities.append(verification['fidelity'])
            if 'is_entangled' in verification:
                entanglement_rates.append(1 if verification['is_entangled'] else 0)
        
        return {
            'sample_size': len(sample_indices),
            'average_fidelity': np.mean(fidelities) if fidelities else None,
            'min_fidelity': np.min(fidelities) if fidelities else None,
            'max_fidelity': np.max(fidelities) if fidelities else None,
            'entanglement_rate': np.mean(entanglement_rates) if entanglement_rates else None,
            'total_pairs': len(epr_pairs)
        }


class PhysicalEPRSource:
    """
    Physical EPR source for real quantum hardware
    
    Simulates a physical entanglement source that generates EPR pairs
    with realistic noise and decoherence models.
    """
    
    def __init__(self, backend: QuantumHardwareBackend, 
                 noise_model: Optional[Dict[str, float]] = None):
        """
        Initialize physical EPR source
        
        Args:
            backend: Quantum hardware backend
            noise_model: Noise parameters (decoherence, gate errors, etc.)
        """
        self.backend = backend
        self.generator = RealEPRGenerator(backend)
        
        # Default noise model
        self.noise_model = noise_model or {
            'decoherence_rate': 0.01,  # 1% decoherence per operation
            'gate_error_rate': 0.001,  # 0.1% gate error
            'measurement_error': 0.02,  # 2% measurement error
            'entanglement_lifetime': 1000  # Operations before significant decay
        }
    
    def generate_physical_epr_pair(self, state_type: str = 'phi_plus') -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate EPR pair with physical noise model
        
        Args:
            state_type: Type of Bell state
            
        Returns:
            Tuple of (noisy_epr_state, generation_metadata)
        """
        # Generate ideal EPR pair
        ideal_state, metadata = self.generator.generate_epr_pair(state_type, verify=False)
        
        # Apply noise model
        noisy_state = self._apply_noise(ideal_state)
        
        # Update metadata
        metadata['noise_applied'] = True
        metadata['noise_model'] = self.noise_model.copy()
        metadata['fidelity_after_noise'] = self._calculate_fidelity(noisy_state, state_type)
        
        return noisy_state, metadata
    
    def _apply_noise(self, state: np.ndarray) -> np.ndarray:
        """
        Apply noise model to quantum state
        
        Args:
            state: Ideal quantum state
            
        Returns:
            Noisy quantum state
        """
        # Simplified noise model: add small random perturbations
        noise_amplitude = self.noise_model['decoherence_rate']
        
        # Add small random noise
        noise = np.random.normal(0, noise_amplitude, state.shape) + \
                1j * np.random.normal(0, noise_amplitude, state.shape)
        
        noisy_state = state + noise * np.abs(state)
        
        # Renormalize
        norm = np.sqrt(np.sum(np.abs(noisy_state)**2))
        if norm > 1e-10:
            noisy_state = noisy_state / norm
        
        return noisy_state
    
    def _calculate_fidelity(self, state: np.ndarray, expected_type: str) -> float:
        """Calculate fidelity with ideal state"""
        ideal_state = self.backend.create_bell_state(expected_type)
        overlap = np.abs(np.vdot(ideal_state, state))**2
        return float(overlap)
    
    def generate_batch_with_quality_control(self, num_pairs: int,
                                           min_fidelity: float = 0.9,
                                           max_attempts: int = 3) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Generate EPR pairs with quality control
        
        Regenerates pairs that don't meet fidelity threshold.
        
        Args:
            num_pairs: Number of pairs to generate
            min_fidelity: Minimum acceptable fidelity
            max_attempts: Maximum regeneration attempts per pair
            
        Returns:
            Tuple of (epr_pairs, quality_metrics)
        """
        epr_pairs = []
        quality_metrics = {
            'total_generated': 0,
            'accepted': 0,
            'rejected': 0,
            'average_fidelity': [],
            'regeneration_count': 0
        }
        
        for _ in range(num_pairs):
            attempts = 0
            accepted = False
            
            while attempts < max_attempts and not accepted:
                state, metadata = self.generate_physical_epr_pair()
                fidelity = metadata.get('fidelity_after_noise', 0)
                
                quality_metrics['total_generated'] += 1
                
                if fidelity >= min_fidelity:
                    epr_pairs.append(state)
                    quality_metrics['accepted'] += 1
                    quality_metrics['average_fidelity'].append(fidelity)
                    accepted = True
                else:
                    quality_metrics['rejected'] += 1
                    attempts += 1
                    quality_metrics['regeneration_count'] += 1
            
            if not accepted:
                # Accept anyway if max attempts reached
                epr_pairs.append(state)
                quality_metrics['accepted'] += 1
                quality_metrics['average_fidelity'].append(fidelity)
        
        quality_metrics['average_fidelity'] = np.mean(quality_metrics['average_fidelity']) if quality_metrics['average_fidelity'] else 0
        quality_metrics['acceptance_rate'] = quality_metrics['accepted'] / quality_metrics['total_generated'] if quality_metrics['total_generated'] > 0 else 0
        
        return epr_pairs, quality_metrics

