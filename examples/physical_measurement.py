"""
Physical Measurement Apparatus Example

Demonstrates physical quantum measurement apparatus usage.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    StandardMeasurementApparatus, HighPrecisionMeasurementApparatus,
    AdaptiveMeasurementApparatus, MeasurementApparatusFactory,
    PhysicalQEZK, SimulationBackend
)


def example_standard_apparatus():
    """Example: Standard measurement apparatus"""
    print("=" * 70)
    print("Example 1: Standard Measurement Apparatus")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    apparatus = StandardMeasurementApparatus(backend, measurement_error=0.02)
    
    # Calibrate
    print("Calibrating measurement apparatus...")
    calibration = apparatus.calibrate()
    print(f"Calibration success: {calibration['success']}")
    print(f"Bases calibrated: {calibration['bases_calibrated']}")
    print(f"Error rates: {calibration['error_rates']}")
    print()
    
    # Perform measurements
    print("Performing measurements...")
    for basis in ['Z', 'X', 'Y']:
        result = apparatus.measure(0, basis)
        print(f"  {basis} basis: {result}")
    print()
    
    # Get statistics
    stats = apparatus.get_statistics()
    print(f"Total measurements: {stats['total_measurements']}")
    print(f"Error rate: {stats['error_rate']:.4f}")
    print()


def example_high_precision():
    """Example: High-precision measurement apparatus"""
    print("=" * 70)
    print("Example 2: High-Precision Measurement Apparatus")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    apparatus = HighPrecisionMeasurementApparatus(backend, shots=5)
    
    print("Performing high-precision measurements (5 shots)...")
    for basis in ['Z', 'X', 'Y']:
        result = apparatus.measure(0, basis)
        confidence = apparatus.get_measurement_confidence(0, basis)
        print(f"  {basis} basis: {result} (confidence: {confidence:.2f})")
    print()


def example_adaptive():
    """Example: Adaptive measurement apparatus"""
    print("=" * 70)
    print("Example 3: Adaptive Measurement Apparatus")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    apparatus = AdaptiveMeasurementApparatus(backend, adaptive_threshold=0.05)
    
    print("Performing adaptive measurements...")
    print("(Apparatus will auto-recalibrate if error rate exceeds threshold)")
    print()
    
    for i in range(10):
        result = apparatus.measure(0, 'Z')
        stats = apparatus.get_statistics()
        print(f"Measurement {i+1}: {result}, Error rate: {stats['error_rate']:.4f}")
    print()


def example_factory():
    """Example: Using measurement apparatus factory"""
    print("=" * 70)
    print("Example 4: Measurement Apparatus Factory")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    
    # Create standard apparatus
    standard = MeasurementApparatusFactory.create_standard(backend)
    print("Standard apparatus created")
    
    # Create high-precision apparatus
    high_precision = MeasurementApparatusFactory.create_high_precision(backend, shots=7)
    print("High-precision apparatus created (7 shots)")
    
    # Create adaptive apparatus
    adaptive = MeasurementApparatusFactory.create_adaptive(backend)
    print("Adaptive apparatus created")
    print()


def example_physical_protocol():
    """Example: Physical QE-ZK protocol"""
    print("=" * 70)
    print("Example 5: Physical QE-ZK Protocol")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    apparatus = StandardMeasurementApparatus(backend)
    
    # Create physical QE-ZK system
    qezk = PhysicalQEZK(
        hardware_backend=backend,
        measurement_apparatus=apparatus,
        num_epr_pairs=100
    )
    
    statement = "I know the secret password"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print(f"Witness: {witness}")
    print()
    
    # Generate proof with physical measurement
    proof = qezk.prove_with_physical_measurement(statement, witness, seed=42)
    
    print(f"CHSH Value: {proof.chsh_value:.4f}")
    print(f"Is Valid: {proof.is_valid}")
    print()
    
    # Get measurement statistics
    stats = qezk.get_measurement_statistics()
    print("Measurement Statistics:")
    print(f"  Total measurements: {stats.get('total_measurements', 0)}")
    print(f"  Error rate: {stats.get('error_rate', 0):.4f}")
    print(f"  Is calibrated: {stats.get('is_calibrated', False)}")
    print()


def main():
    """Run all examples"""
    example_standard_apparatus()
    example_high_precision()
    example_adaptive()
    example_factory()
    example_physical_protocol()
    
    print("=" * 70)
    print("Physical Measurement Apparatus Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


