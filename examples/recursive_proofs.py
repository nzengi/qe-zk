"""
Recursive Proofs Example

Demonstrates recursive proofs, proof composition, and aggregation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, RecursiveProver, ProofComposer,
    NestedProofBuilder, ProofAggregator, RecursiveQEZK
)


def example_proof_of_proof():
    """Example: Proof of proof"""
    print("=" * 70)
    print("Example 1: Proof of Proof")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    recursive_prover = RecursiveProver(qezk)
    
    # Generate base proof
    statement = "I know the secret password"
    witness = "11010110"
    base_proof = qezk.prove(statement, witness, seed=42)
    
    print(f"Base Proof:")
    print(f"  Statement: {base_proof.statement}")
    print(f"  CHSH Value: {base_proof.chsh_value:.4f}")
    print(f"  Is Valid: {base_proof.is_valid}")
    print()
    
    # Generate proof of proof
    proof_of_proof = recursive_prover.prove_proof(base_proof, seed=43)
    
    print(f"Proof of Proof:")
    print(f"  Statement: {proof_of_proof.statement}")
    print(f"  CHSH Value: {proof_of_proof.chsh_value:.4f}")
    print(f"  Is Valid: {proof_of_proof.is_valid}")
    print()


def example_proof_composition():
    """Example: Proof composition"""
    print("=" * 70)
    print("Example 2: Proof Composition")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    composer = ProofComposer(qezk)
    
    # Generate multiple proofs
    proofs = []
    for i in range(3):
        statement = f"I know secret {i+1}"
        witness = f"110101{i}"
        proof = qezk.prove(statement, witness, seed=42 + i)
        proofs.append(proof)
        print(f"Proof {i+1}: CHSH={proof.chsh_value:.4f}, Valid={proof.is_valid}")
    
    print()
    
    # Compose proofs
    composite = composer.compose_proofs(proofs, statement="Composite proof", seed=50)
    
    print(f"Composite Proof:")
    print(f"  CHSH Value: {composite.chsh_value:.4f}")
    print(f"  Is Valid: {composite.is_valid}")
    print()


def example_nested_proofs():
    """Example: Nested proofs"""
    print("=" * 70)
    print("Example 3: Nested Proofs")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    nested_builder = NestedProofBuilder(qezk)
    
    statement = "I know the secret"
    witness = "11010110"
    
    print(f"Building nested proof (depth 3)...")
    print(f"Statement: {statement}")
    print()
    
    nested_proof = nested_builder.build_nested_proof(
        statement, witness, depth=3, seed=42
    )
    
    print(f"Nested Proof:")
    print(f"  Depth: {nested_proof.recursion_depth}")
    print(f"  Total Proofs: {nested_proof.metadata['total_proofs']}")
    print(f"  Is Valid: {nested_proof.is_valid}")
    print(f"  Inner Proofs: {len(nested_proof.inner_proofs)}")
    print(f"  Outer Proof CHSH: {nested_proof.outer_proof.chsh_value:.4f}")
    print()


def example_proof_aggregation():
    """Example: Proof aggregation"""
    print("=" * 70)
    print("Example 4: Proof Aggregation")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = ProofAggregator(qezk)
    
    # Generate multiple proofs
    proofs = []
    for i in range(5):
        statement = f"Statement {i+1}"
        witness = f"110101{i}"
        proof = qezk.prove(statement, witness, seed=42 + i)
        proofs.append(proof)
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Aggregate
    aggregated, metadata = aggregator.aggregate_proofs(
        proofs, statement="Aggregated proof", seed=100
    )
    
    print("Aggregation Results:")
    print(f"  Number of proofs: {metadata['num_proofs']}")
    print(f"  All valid: {metadata['all_valid']}")
    print(f"  Valid count: {metadata['valid_count']}")
    print(f"  Average CHSH: {metadata['avg_chsh']:.4f}")
    print(f"  Aggregated CHSH: {metadata['aggregated_chsh']:.4f}")
    print(f"  Aggregated valid: {metadata['aggregated_valid']}")
    print()


def example_recursive_qezk():
    """Example: Complete recursive QE-ZK"""
    print("=" * 70)
    print("Example 5: Recursive QE-ZK")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    recursive_qezk = RecursiveQEZK(qezk)
    
    statement = "I know the secret password"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print()
    
    # Recursive proof
    recursive_proof = recursive_qezk.prove_recursively(
        statement, witness, depth=2, seed=42
    )
    
    print(f"Recursive Proof:")
    print(f"  Depth: {recursive_proof.recursion_depth}")
    print(f"  Is Valid: {recursive_proof.is_valid}")
    print()
    
    # Proof of proof
    base_proof = qezk.prove(statement, witness, seed=42)
    proof_of_proof = recursive_qezk.prove_proof_of_proof(base_proof, seed=43)
    
    print(f"Proof of Proof:")
    print(f"  CHSH Value: {proof_of_proof.chsh_value:.4f}")
    print(f"  Is Valid: {proof_of_proof.is_valid}")
    print()


def main():
    """Run all examples"""
    example_proof_of_proof()
    example_proof_composition()
    example_nested_proofs()
    example_proof_aggregation()
    example_recursive_qezk()
    
    print("=" * 70)
    print("Recursive Proofs Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


