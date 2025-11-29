"""
Multi-Party Protocol Example

Demonstrates multi-party QE-ZK protocol with multiple provers and verifiers.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, Party, PartyRole,
    ThresholdVerifier, MultiProverProtocol,
    ConsensusProtocol, GroupProtocol, MultiPartyQEZK
)


def example_threshold_verification():
    """Example: Threshold verification"""
    print("=" * 70)
    print("Example 1: Threshold Verification")
    print("=" * 70)
    print()
    
    # Create multiple verifiers
    verifiers = [
        Party("verifier1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier3", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier4", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier5", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
    ]
    
    # Threshold: need 3 out of 5 verifiers to agree
    threshold_verifier = ThresholdVerifier(threshold=3, verifiers=verifiers)
    
    statement = "I know the secret password"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print(f"Threshold: 3 out of {len(verifiers)} verifiers")
    print()
    
    is_valid, details = threshold_verifier.verify(statement, witness, seed=42)
    
    print(f"Consensus reached: {is_valid}")
    print(f"Valid verifications: {details['valid_count']}/{details['total_verifiers']}")
    print(f"Threshold: {details['threshold']}")
    print()


def example_multi_prover():
    """Example: Multiple provers"""
    print("=" * 70)
    print("Example 2: Multiple Provers")
    print("=" * 70)
    print()
    
    # Create multiple provers
    provers = [
        Party("prover1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("prover2", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("prover3", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100))
    ]
    
    multi_prover = MultiProverProtocol(provers)
    
    statement = "I know the secret"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print(f"Number of provers: {len(provers)}")
    print()
    
    proofs = multi_prover.prove(statement, witness, seed=42)
    
    print("Proofs from each prover:")
    for prover_id, proof in proofs.items():
        print(f"  {prover_id}: CHSH={proof.chsh_value:.4f}, Valid={proof.is_valid}")
    
    # Aggregate
    aggregated = multi_prover.aggregate_proofs(proofs)
    print()
    print("Aggregated statistics:")
    print(f"  Valid count: {aggregated['valid_count']}/{aggregated['num_provers']}")
    print(f"  Valid rate: {aggregated['valid_rate']:.2%}")
    print(f"  Average CHSH: {aggregated['avg_chsh']:.4f}")
    print()


def example_consensus():
    """Example: Consensus protocol"""
    print("=" * 70)
    print("Example 3: Consensus Protocol")
    print("=" * 70)
    print()
    
    # Create parties with different weights
    parties = [
        Party("party1", PartyRole.VERIFIER, QuantumEntanglementZK(), weight=1.0),
        Party("party2", PartyRole.VERIFIER, QuantumEntanglementZK(), weight=1.0),
        Party("party3", PartyRole.VERIFIER, QuantumEntanglementZK(), weight=2.0),  # Higher weight
        Party("party4", PartyRole.VERIFIER, QuantumEntanglementZK(), weight=1.0)
    ]
    
    consensus = ConsensusProtocol(parties, voting_threshold=0.5)
    
    print("Voting on proof validity...")
    print()
    
    # Simulate votes
    consensus.vote("party1", True)
    consensus.vote("party2", True)
    consensus.vote("party3", False)  # Higher weight
    consensus.vote("party4", True)
    
    print(f"Consensus reached: {consensus.has_consensus()}")
    print(f"Consensus result: {consensus.get_consensus_result()}")
    print()


def example_group_protocol():
    """Example: Group protocol"""
    print("=" * 70)
    print("Example 4: Group Protocol")
    print("=" * 70)
    print()
    
    # Create mixed group
    parties = [
        Party("prover1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("prover2", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier3", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
    ]
    
    group = GroupProtocol(parties)
    
    statement = "I know the secret password"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print(f"Group size: {len(parties)} parties")
    print(f"  Provers: {sum(1 for p in parties if p.role == PartyRole.PROVER)}")
    print(f"  Verifiers: {sum(1 for p in parties if p.role == PartyRole.VERIFIER)}")
    print()
    
    results = group.execute_group_protocol(statement, witness, seed=42)
    
    print("Group Protocol Results:")
    print(f"  Consensus reached: {results['consensus_reached']}")
    print(f"  Consensus result: {results['consensus']}")
    print(f"  Valid verifications: {sum(1 for r in results['verification_results'].values() if r.get('is_valid', False))}")
    print()


def example_multi_party_qezk():
    """Example: Complete multi-party QE-ZK"""
    print("=" * 70)
    print("Example 5: Multi-Party QE-ZK")
    print("=" * 70)
    print()
    
    # Create parties
    parties = [
        Party("prover1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
        Party("verifier3", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
    ]
    
    multi_party = MultiPartyQEZK(parties, threshold=2)
    
    statement = "I know the secret password"
    witness = "11010110"
    
    print(f"Statement: {statement}")
    print(f"Parties: {len(parties)}")
    print(f"Threshold: {multi_party.threshold_verifier.threshold if multi_party.threshold_verifier else 'N/A'}")
    print()
    
    results = multi_party.prove_with_multi_party(statement, witness, seed=42)
    
    print("Multi-Party Results:")
    print(f"  Consensus reached: {results.get('consensus_reached', False)}")
    print(f"  Consensus: {results.get('consensus', None)}")
    if 'threshold_verification' in results:
        print(f"  Threshold verification: {results['threshold_verification']}")
    print()


def main():
    """Run all examples"""
    example_threshold_verification()
    example_multi_prover()
    example_consensus()
    example_group_protocol()
    example_multi_party_qezk()
    
    print("=" * 70)
    print("Multi-Party Protocol Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
