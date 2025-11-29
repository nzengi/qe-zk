"""
Integration tests for QE-ZK system
"""

import unittest
from qezk.protocol import QuantumEntanglementZK
from qezk.security import QEZKSecurity
from qezk.simulation import QEZKSimulation


class TestIntegration(unittest.TestCase):
    """Integration tests for complete QE-ZK system"""
    
    def test_full_system_workflow(self):
        """Test complete system workflow"""
        # Initialize system
        qezk = QuantumEntanglementZK(num_epr_pairs=500)
        
        # Generate proof
        statement = "I know the secret"
        witness = "1101011010110101"
        proof = qezk.prove(statement, witness, seed=42)
        
        # Verify proof structure
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, statement)
        self.assertGreater(proof.chsh_value, 0.0)
    
    def test_security_properties(self):
        """Test security property reporting"""
        security_props = QEZKSecurity.information_theoretic_security()
        
        self.assertTrue(security_props['perfect_zero_knowledge'])
        self.assertTrue(security_props['information_theoretic'])
        self.assertTrue(security_props['quantum_secure'])
    
    def test_simulation(self):
        """Test simulation framework"""
        simulator = QEZKSimulation(num_epr_pairs=200)
        
        statement = "Test statement"
        witness = "11010110"
        
        results = simulator.simulate_protocol(statement, witness, num_trials=5, seed=42)
        
        self.assertEqual(results['total_trials'], 5)
        self.assertGreaterEqual(results['success_rate'], 0.0)
        self.assertLessEqual(results['success_rate'], 1.0)
        self.assertGreater(results['avg_chsh'], 0.0)
    
    def test_performance_analysis(self):
        """Test performance analysis across multiple statements"""
        simulator = QEZKSimulation(num_epr_pairs=100)
        
        statements = ["Statement 1", "Statement 2"]
        witnesses = ["11010110", "10101010"]
        
        results = simulator.performance_analysis(statements, witnesses)
        
        self.assertEqual(len(results['individual_results']), 2)
        self.assertGreaterEqual(results['overall_success_rate'], 0.0)
        self.assertLessEqual(results['overall_success_rate'], 1.0)


if __name__ == '__main__':
    unittest.main()

