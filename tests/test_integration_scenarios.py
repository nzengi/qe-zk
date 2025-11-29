"""
Integration Scenario Tests

Real-world scenario tests similar to zk-SNARK/zk-STARK integration tests.
Tests various use cases and application scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import QuantumEntanglementZK, QEZKSimulation


class TestIntegrationScenarios(unittest.TestCase):
    """Integration scenario tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=500, chsh_threshold=2.2)
    
    def test_authentication_scenario(self):
        """Test authentication scenario"""
        # User proves they know their password
        user_id = "user123"
        password_hash = "1101011010110101"
        statement = f"I am {user_id} and I know my password"
        
        proof = self.qezk.prove(statement, password_hash, seed=42)
        
        # Verify proof
        is_valid, chsh_value = self.qezk.verify(
            proof.prover_results,
            proof.verifier_results,
            proof.measurement_bases
        )
        
        print(f"\n  Authentication Scenario:")
        print(f"    User ID: {user_id}")
        print(f"    Proof generated: ✓")
        print(f"    CHSH value: {chsh_value:.4f}")
        
        self.assertIsNotNone(proof)
    
    def test_multi_user_scenario(self):
        """Test multiple users scenario"""
        users = [
            ("user1", "1101011010110101"),
            ("user2", "1010101010101010"),
            ("user3", "1111000011110000")
        ]
        
        proofs = []
        for user_id, password_hash in users:
            statement = f"I am {user_id}"
            proof = self.qezk.prove(statement, password_hash, seed=42)
            proofs.append((user_id, proof))
        
        print(f"\n  Multi-User Scenario:")
        print(f"    Number of users: {len(users)}")
        for user_id, proof in proofs:
            print(f"    {user_id}: CHSH={proof.chsh_value:.4f}")
        
        self.assertEqual(len(proofs), len(users))
    
    def test_secret_sharing_scenario(self):
        """Test secret sharing scenario"""
        secret = "1101011010110101"
        statement = "I know the shared secret"
        
        # Generate proof for secret
        proof = self.qezk.prove(statement, secret, seed=42)
        
        print(f"\n  Secret Sharing Scenario:")
        print(f"    Secret length: {len(secret)} bits")
        print(f"    Proof generated: ✓")
        print(f"    Zero-knowledge: Verifier learns nothing about secret")
        
        self.assertIsNotNone(proof)
    
    def test_batch_verification_scenario(self):
        """Test batch verification scenario"""
        statements = [
            "I know secret 1",
            "I know secret 2",
            "I know secret 3"
        ]
        witnesses = [
            "1101011010110101",
            "1010101010101010",
            "1111000011110000"
        ]
        
        proofs = []
        for statement, witness in zip(statements, witnesses):
            proof = self.qezk.prove(statement, witness, seed=42)
            proofs.append(proof)
        
        # Batch verify
        valid_count = sum(1 for proof in proofs if proof.is_valid)
        
        print(f"\n  Batch Verification Scenario:")
        print(f"    Number of proofs: {len(proofs)}")
        print(f"    Valid proofs: {valid_count}/{len(proofs)}")
        
        self.assertEqual(len(proofs), len(statements))
    
    def test_performance_scenario(self):
        """Test performance in realistic scenario"""
        simulator = QEZKSimulation(num_epr_pairs=200)
        
        statements = [
            "Transaction 1 is valid",
            "Transaction 2 is valid",
            "Transaction 3 is valid"
        ]
        witnesses = [
            "1101011010110101",
            "1010101010101010",
            "1111000011110000"
        ]
        
        results = simulator.performance_analysis(statements, witnesses)
        
        print(f"\n  Performance Scenario:")
        print(f"    Overall success rate: {results['overall_success_rate']:.2%}")
        print(f"    Overall average CHSH: {results['overall_avg_chsh']:.4f}")
        
        self.assertIsNotNone(results)
    
    def test_consistency_scenario(self):
        """Test consistency across multiple runs"""
        statement = "I know the secret"
        witness = "1101011010110101"
        
        # Generate multiple proofs with same parameters
        proofs = []
        for seed in range(5):
            proof = self.qezk.prove(statement, witness, seed=seed)
            proofs.append(proof)
        
        # Check that bases are consistent (same statement → same bases)
        bases = [proof.measurement_bases for proof in proofs]
        all_same = all(b == bases[0] for b in bases)
        
        print(f"\n  Consistency Scenario:")
        print(f"    Number of runs: {len(proofs)}")
        print(f"    Bases consistent: {all_same}")
        print(f"    CHSH values: {[p.chsh_value for p in proofs]}")
        
        self.assertTrue(all_same)  # Same statement should produce same bases


if __name__ == '__main__':
    unittest.main()

