"""
Physical Measurement Apparatus

Implementation for physical quantum measurement apparatus on real hardware.
Provides calibration, error correction, and hardware-specific measurement interfaces.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from .exceptions import MeasurementError, QuantumStateError
from .hardware_interface import QuantumHardwareBackend


class MeasurementApparatus(ABC):
    """
    Abstract base class for physical measurement apparatus
    
    Represents a physical quantum measurement device that can measure
    qubits in different bases (Z, X, Y).
    """
    
    @abstractmethod
    def measure(self, qubit_index: int, basis: str) -> int:
        """
        Perform physical measurement
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis ('Z', 'X', or 'Y')
            
        Returns:
            Measurement result (0 or 1)
        """
        pass
    
    @abstractmethod
    def calibrate(self) -> Dict[str, Any]:
        """
        Calibrate measurement apparatus
        
        Returns:
            Calibration results and parameters
        """
        pass
    
    @abstractmethod
    def get_measurement_error_rate(self) -> float:
        """
        Get current measurement error rate
        
        Returns:
            Error rate (0-1)
        """
        pass


class StandardMeasurementApparatus(MeasurementApparatus):
    """
    Standard measurement apparatus with calibration and error correction
    
    Provides physical measurement with error handling and calibration.
    """
    
    def __init__(self, backend: QuantumHardwareBackend,
                 measurement_error: float = 0.02,
                 auto_calibrate: bool = True):
        """
        Initialize measurement apparatus
        
        Args:
            backend: Quantum hardware backend
            measurement_error: Initial measurement error rate (default: 2%)
            auto_calibrate: Whether to auto-calibrate on initialization
        """
        self.backend = backend
        self.measurement_error = measurement_error
        self.calibration_data = {}
        self.is_calibrated = False
        
        # Measurement statistics
        self.measurement_count = 0
        self.error_count = 0
        
        if auto_calibrate:
            self.calibrate()
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """
        Perform physical measurement with error correction
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis ('Z', 'X', or 'Y')
            
        Returns:
            Measurement result (0 or 1)
            
        Raises:
            MeasurementError: If measurement fails
        """
        try:
            # Validate inputs
            if basis not in ['Z', 'X', 'Y']:
                raise MeasurementError(f"Invalid basis: {basis}. Must be 'Z', 'X', or 'Y'")
            
            # Perform measurement on hardware
            raw_result = self.backend.measure(qubit_index, basis)
            
            # Apply error correction if calibrated
            if self.is_calibrated and basis in self.calibration_data:
                corrected_result = self._apply_error_correction(raw_result, basis)
            else:
                corrected_result = raw_result
            
            # Update statistics
            self.measurement_count += 1
            
            # Check for errors (simplified - in real hardware would use known states)
            if not self._is_result_valid(corrected_result):
                self.error_count += 1
                raise MeasurementError("Invalid measurement result")
            
            return corrected_result
            
        except Exception as e:
            if isinstance(e, MeasurementError):
                raise
            raise MeasurementError(f"Measurement failed: {str(e)}") from e
    
    def _apply_error_correction(self, raw_result: int, basis: str) -> int:
        """
        Apply error correction based on calibration data
        
        Args:
            raw_result: Raw measurement result
            basis: Measurement basis
            
        Returns:
            Corrected measurement result
        """
        calibration = self.calibration_data.get(basis, {})
        error_rate = calibration.get('error_rate', self.measurement_error)
        
        # Simple error correction: flip result with probability based on error rate
        if np.random.random() < error_rate:
            return 1 - raw_result
        
        return raw_result
    
    def _is_result_valid(self, result: int) -> bool:
        """Check if measurement result is valid"""
        return result in [0, 1]
    
    def calibrate(self) -> Dict[str, Any]:
        """
        Calibrate measurement apparatus
        
        Performs measurements on known states to determine error rates
        and calibration parameters for each basis.
        
        Returns:
            Dictionary with calibration results
        """
        calibration_results = {
            'calibration_time': None,
            'bases_calibrated': [],
            'error_rates': {},
            'fidelity': {},
            'success': False
        }
        
        try:
            # Calibrate each basis
            for basis in ['Z', 'X', 'Y']:
                basis_calibration = self._calibrate_basis(basis)
                self.calibration_data[basis] = basis_calibration
                calibration_results['bases_calibrated'].append(basis)
                calibration_results['error_rates'][basis] = basis_calibration['error_rate']
                calibration_results['fidelity'][basis] = basis_calibration['fidelity']
            
            self.is_calibrated = True
            calibration_results['success'] = True
            
            # Update measurement error from calibration
            avg_error = np.mean(list(calibration_results['error_rates'].values()))
            self.measurement_error = avg_error
            
        except Exception as e:
            calibration_results['error'] = str(e)
        
        return calibration_results
    
    def _calibrate_basis(self, basis: str, num_tests: int = 100) -> Dict[str, Any]:
        """
        Calibrate a specific measurement basis
        
        Args:
            basis: Basis to calibrate ('Z', 'X', or 'Y')
            num_tests: Number of calibration measurements
            
        Returns:
            Calibration data for the basis
        """
        # Prepare known states for calibration
        # In real hardware, this would use prepared test states
        test_results = []
        
        for _ in range(num_tests):
            # Reset to known state
            self.backend.reset()
            
            # Prepare state in the basis
            if basis == 'Z':
                # |0⟩ state
                pass  # Already in |0⟩ after reset
            elif basis == 'X':
                # |+⟩ state
                self.backend.apply_gate('H', 0)
            elif basis == 'Y':
                # |+i⟩ state
                self.backend.apply_gate('S', 0)
                self.backend.apply_gate('H', 0)
            
            # Measure
            result = self.backend.measure(0, basis)
            test_results.append(result)
        
        # Calculate error rate
        # For |0⟩ or |+⟩, we expect mostly 0 results
        expected_result = 0
        error_count = sum(1 for r in test_results if r != expected_result)
        error_rate = error_count / num_tests
        
        # Calculate fidelity (1 - error_rate)
        fidelity = 1.0 - error_rate
        
        return {
            'basis': basis,
            'error_rate': error_rate,
            'fidelity': fidelity,
            'num_tests': num_tests,
            'error_count': error_count
        }
    
    def get_measurement_error_rate(self) -> float:
        """Get current measurement error rate"""
        if self.measurement_count > 0:
            return self.error_count / self.measurement_count
        return self.measurement_error
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get measurement statistics
        
        Returns:
            Dictionary with measurement statistics
        """
        return {
            'total_measurements': self.measurement_count,
            'error_count': self.error_count,
            'error_rate': self.get_measurement_error_rate(),
            'is_calibrated': self.is_calibrated,
            'calibration_data': self.calibration_data.copy()
        }


class HighPrecisionMeasurementApparatus(StandardMeasurementApparatus):
    """
    High-precision measurement apparatus with multiple measurement shots
    
    Uses multiple measurements and majority voting for higher accuracy.
    """
    
    def __init__(self, backend: QuantumHardwareBackend,
                 shots: int = 5,
                 measurement_error: float = 0.02):
        """
        Initialize high-precision apparatus
        
        Args:
            backend: Quantum hardware backend
            shots: Number of measurement shots per measurement
            measurement_error: Initial measurement error rate
        """
        super().__init__(backend, measurement_error, auto_calibrate=True)
        self.shots = shots
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """
        Perform high-precision measurement with multiple shots
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis
            
        Returns:
            Measurement result (0 or 1) using majority voting
        """
        # Perform multiple measurements
        results = []
        for _ in range(self.shots):
            result = super().measure(qubit_index, basis)
            results.append(result)
        
        # Majority voting
        result_counts = {0: results.count(0), 1: results.count(1)}
        final_result = max(result_counts, key=result_counts.get)
        
        return final_result
    
    def get_measurement_confidence(self, qubit_index: int, basis: str) -> float:
        """
        Get confidence level for a measurement
        
        Performs multiple shots and returns confidence based on agreement.
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis
            
        Returns:
            Confidence level (0-1)
        """
        results = []
        for _ in range(self.shots):
            result = super().measure(qubit_index, basis)
            results.append(result)
        
        # Calculate agreement
        result_counts = {0: results.count(0), 1: results.count(1)}
        max_count = max(result_counts.values())
        confidence = max_count / self.shots
        
        return confidence


class AdaptiveMeasurementApparatus(StandardMeasurementApparatus):
    """
    Adaptive measurement apparatus that adjusts based on conditions
    
    Automatically adjusts measurement parameters based on environmental
    conditions and measurement history.
    """
    
    def __init__(self, backend: QuantumHardwareBackend,
                 measurement_error: float = 0.02,
                 adaptive_threshold: float = 0.05):
        """
        Initialize adaptive apparatus
        
        Args:
            backend: Quantum hardware backend
            measurement_error: Initial measurement error rate
            adaptive_threshold: Error rate threshold for re-calibration
        """
        super().__init__(backend, measurement_error, auto_calibrate=True)
        self.adaptive_threshold = adaptive_threshold
        self.last_calibration_time = 0
        self.measurements_since_calibration = 0
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """
        Perform adaptive measurement with automatic re-calibration
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis
            
        Returns:
            Measurement result (0 or 1)
        """
        # Check if re-calibration is needed
        if self._should_recalibrate():
            self.calibrate()
            self.measurements_since_calibration = 0
        
        # Perform measurement
        result = super().measure(qubit_index, basis)
        self.measurements_since_calibration += 1
        
        return result
    
    def _should_recalibrate(self) -> bool:
        """
        Determine if re-calibration is needed
        
        Returns:
            True if re-calibration should be performed
        """
        if not self.is_calibrated:
            return True
        
        # Re-calibrate if error rate exceeds threshold
        current_error_rate = self.get_measurement_error_rate()
        if current_error_rate > self.adaptive_threshold:
            return True
        
        # Re-calibrate after many measurements
        if self.measurements_since_calibration > 1000:
            return True
        
        return False


class MeasurementApparatusFactory:
    """
    Factory for creating measurement apparatus instances
    """
    
    @staticmethod
    def create_standard(backend: QuantumHardwareBackend,
                       measurement_error: float = 0.02) -> StandardMeasurementApparatus:
        """Create standard measurement apparatus"""
        return StandardMeasurementApparatus(backend, measurement_error)
    
    @staticmethod
    def create_high_precision(backend: QuantumHardwareBackend,
                             shots: int = 5) -> HighPrecisionMeasurementApparatus:
        """Create high-precision measurement apparatus"""
        return HighPrecisionMeasurementApparatus(backend, shots=shots)
    
    @staticmethod
    def create_adaptive(backend: QuantumHardwareBackend,
                       adaptive_threshold: float = 0.05) -> AdaptiveMeasurementApparatus:
        """Create adaptive measurement apparatus"""
        return AdaptiveMeasurementApparatus(backend, adaptive_threshold=adaptive_threshold)


