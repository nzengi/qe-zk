"""
Multi-Party Protocol Tests

Tests for multi-party QE-ZK protocol.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, Party, PartyRole,
    ThresholdVerifier, MultiProverProtocol,
    ConsensusProtocol, GroupProtocol, MultiPartyQEZK
)
from qezk.exceptions import ConfigurationError, ProtocolError


class TestMultiParty(unittest.TestCase):
    """Test cases for multi-party protocol"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    def test_party_creation(self):
        """Test party creation"""
        party = Party("test_party", PartyRole.PROVER, self.qezk)
        
        self.assertEqual(party.party_id, "test_party")
        self.assertEqual(party.role, PartyRole.PROVER)
        self.assertEqual(party.weight, 1.0)
    
    def test_threshold_verifier(self):
        """Test threshold verification"""
        verifiers = [
            Party(f"verifier{i}", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
            for i in range(5)
        ]
        
        threshold_verifier = ThresholdVerifier(threshold=3, verifiers=verifiers)
        
        self.assertEqual(threshold_verifier.threshold, 3)
        self.assertEqual(len(threshold_verifier.verifiers), 5)
    
    def test_threshold_verifier_invalid(self):
        """Test invalid threshold"""
        verifiers = [
            Party("v1", PartyRole.VERIFIER, self.qezk),
            Party("v2", PartyRole.VERIFIER, self.qezk)
        ]
        
        with self.assertRaises(ConfigurationError):
            ThresholdVerifier(threshold=5, verifiers=verifiers)
    
    def test_threshold_verification(self):
        """Test threshold verification execution"""
        verifiers = [
            Party(f"v{i}", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
            for i in range(3)
        ]
        
        threshold_verifier = ThresholdVerifier(threshold=2, verifiers=verifiers)
        
        statement = "I know the secret"
        witness = "11010110"
        
        is_valid, details = threshold_verifier.verify(statement, witness, seed=42)
        
        self.assertIn('valid_count', details)
        self.assertIn('threshold', details)
        self.assertIn('consensus', details)
    
    def test_multi_prover_protocol(self):
        """Test multi-prover protocol"""
        provers = [
            Party("p1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("p2", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100))
        ]
        
        multi_prover = MultiProverProtocol(provers)
        
        statement = "I know the secret"
        witness = "11010110"
        
        proofs = multi_prover.prove(statement, witness, seed=42)
        
        self.assertEqual(len(proofs), 2)
        self.assertIn("p1", proofs)
        self.assertIn("p2", proofs)
    
    def test_multi_prover_aggregation(self):
        """Test proof aggregation"""
        provers = [
            Party("p1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("p2", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100))
        ]
        
        multi_prover = MultiProverProtocol(provers)
        
        statement = "I know the secret"
        witness = "11010110"
        
        proofs = multi_prover.prove(statement, witness, seed=42)
        aggregated = multi_prover.aggregate_proofs(proofs)
        
        self.assertIn('num_provers', aggregated)
        self.assertIn('valid_count', aggregated)
        self.assertIn('avg_chsh', aggregated)
    
    def test_consensus_protocol(self):
        """Test consensus protocol"""
        parties = [
            Party("p1", PartyRole.VERIFIER, self.qezk),
            Party("p2", PartyRole.VERIFIER, self.qezk),
            Party("p3", PartyRole.VERIFIER, self.qezk)
        ]
        
        consensus = ConsensusProtocol(parties, voting_threshold=0.5)
        
        consensus.vote("p1", True)
        consensus.vote("p2", True)
        consensus.vote("p3", False)
        
        self.assertTrue(consensus.has_consensus())
        self.assertTrue(consensus.get_consensus_result())
    
    def test_consensus_reset(self):
        """Test consensus reset"""
        parties = [Party("p1", PartyRole.VERIFIER, self.qezk)]
        consensus = ConsensusProtocol(parties)
        
        consensus.vote("p1", True)
        self.assertEqual(len(consensus.votes), 1)
        
        consensus.reset()
        self.assertEqual(len(consensus.votes), 0)
    
    def test_group_protocol(self):
        """Test group protocol"""
        parties = [
            Party("p1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
        ]
        
        group = GroupProtocol(parties)
        
        statement = "I know the secret"
        witness = "11010110"
        
        results = group.execute_group_protocol(statement, witness, seed=42)
        
        self.assertIn('prover_proofs', results)
        self.assertIn('verification_results', results)
        self.assertIn('consensus', results)
    
    def test_multi_party_qezk(self):
        """Test multi-party QE-ZK"""
        parties = [
            Party("p1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
        ]
        
        multi_party = MultiPartyQEZK(parties, threshold=2)
        
        self.assertEqual(len(multi_party.provers), 1)
        self.assertEqual(len(multi_party.verifiers), 2)
        self.assertIsNotNone(multi_party.threshold_verifier)
    
    def test_multi_party_prove(self):
        """Test multi-party proof generation"""
        parties = [
            Party("p1", PartyRole.PROVER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v1", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100)),
            Party("v2", PartyRole.VERIFIER, QuantumEntanglementZK(num_epr_pairs=100))
        ]
        
        multi_party = MultiPartyQEZK(parties)
        
        statement = "I know the secret"
        witness = "11010110"
        
        results = multi_party.prove_with_multi_party(statement, witness, seed=42)
        
        self.assertIn('prover_proofs', results)
        self.assertIn('verification_results', results)
        self.assertIn('consensus', results)


if __name__ == '__main__':
    unittest.main()


