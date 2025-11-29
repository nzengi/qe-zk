"""
Real EPR Generation Example

Demonstrates real EPR pair generation on quantum hardware.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    RealEPRGenerator, PhysicalEPRSource, SimulationBackend
)


def example_basic_epr_generation():
    """Example: Basic EPR pair generation"""
    print("=" * 70)
    print("Example 1: Basic Real EPR Generation")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    generator = RealEPRGenerator(backend)
    
    # Generate single EPR pair with verification
    print("Generating EPR pair (phi_plus) with verification...")
    epr_state, metadata = generator.generate_epr_pair(state_type='phi_plus', verify=True)
    
    print(f"State shape: {epr_state.shape}")
    print(f"State type: {metadata['state_type']}")
    print(f"Backend: {metadata['hardware_backend']}")
    
    if metadata['verification']:
        verification = metadata['verification']
        print(f"Entanglement verified: {verification['is_entangled']}")
        print(f"Fidelity: {verification['fidelity']:.4f}")
        print(f"Z correlation: {verification['z_correlation']:.4f}")
        print(f"X correlation: {verification['x_correlation']:.4f}")
    print()


def example_batch_epr_generation():
    """Example: Batch EPR pair generation"""
    print("=" * 70)
    print("Example 2: Batch EPR Generation")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    generator = RealEPRGenerator(backend)
    
    # Generate multiple EPR pairs
    print("Generating 10 EPR pairs (verifying 3 samples)...")
    epr_pairs, batch_metadata = generator.generate_epr_pairs(
        num_pairs=10,
        state_type='phi_plus',
        verify_sample=3
    )
    
    print(f"Generated: {batch_metadata['num_pairs']} pairs")
    print(f"Verified: {batch_metadata['verified_count']} pairs")
    print(f"Verification rate: {batch_metadata['verification_rate']:.2%}")
    if batch_metadata['average_fidelity']:
        print(f"Average fidelity: {batch_metadata['average_fidelity']:.4f}")
    print()


def example_physical_epr_source():
    """Example: Physical EPR source with noise model"""
    print("=" * 70)
    print("Example 3: Physical EPR Source with Noise")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    
    # Custom noise model
    noise_model = {
        'decoherence_rate': 0.01,
        'gate_error_rate': 0.001,
        'measurement_error': 0.02,
        'entanglement_lifetime': 1000
    }
    
    source = PhysicalEPRSource(backend, noise_model=noise_model)
    
    print("Generating physical EPR pair with noise...")
    state, metadata = source.generate_physical_epr_pair('phi_plus')
    
    print(f"Noise applied: {metadata.get('noise_applied', False)}")
    print(f"Fidelity after noise: {metadata.get('fidelity_after_noise', 0):.4f}")
    print()


def example_quality_control():
    """Example: Quality-controlled EPR generation"""
    print("=" * 70)
    print("Example 4: Quality-Controlled Generation")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    source = PhysicalEPRSource(backend)
    
    print("Generating 5 EPR pairs with quality control (min fidelity: 0.9)...")
    epr_pairs, quality_metrics = source.generate_batch_with_quality_control(
        num_pairs=5,
        min_fidelity=0.9,
        max_attempts=3
    )
    
    print(f"Total generated: {quality_metrics['total_generated']}")
    print(f"Accepted: {quality_metrics['accepted']}")
    print(f"Rejected: {quality_metrics['rejected']}")
    print(f"Regeneration count: {quality_metrics['regeneration_count']}")
    print(f"Acceptance rate: {quality_metrics['acceptance_rate']:.2%}")
    print(f"Average fidelity: {quality_metrics['average_fidelity']:.4f}")
    print()


def example_entanglement_monitoring():
    """Example: Entanglement quality monitoring"""
    print("=" * 70)
    print("Example 5: Entanglement Quality Monitoring")
    print("=" * 70)
    print()
    
    backend = SimulationBackend()
    generator = RealEPRGenerator(backend)
    
    # Generate batch
    epr_pairs, _ = generator.generate_epr_pairs(num_pairs=20, verify_sample=0)
    
    # Monitor quality
    print("Monitoring entanglement quality...")
    quality_report = generator.monitor_entanglement_quality(epr_pairs, sample_size=5)
    
    print(f"Sample size: {quality_report['sample_size']}")
    print(f"Total pairs: {quality_report['total_pairs']}")
    if quality_report['average_fidelity']:
        print(f"Average fidelity: {quality_report['average_fidelity']:.4f}")
        print(f"Min fidelity: {quality_report['min_fidelity']:.4f}")
        print(f"Max fidelity: {quality_report['max_fidelity']:.4f}")
    if quality_report['entanglement_rate']:
        print(f"Entanglement rate: {quality_report['entanglement_rate']:.2%}")
    print()


def main():
    """Run all examples"""
    example_basic_epr_generation()
    example_batch_epr_generation()
    example_physical_epr_source()
    example_quality_control()
    example_entanglement_monitoring()
    
    print("=" * 70)
    print("Real EPR Generation Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


