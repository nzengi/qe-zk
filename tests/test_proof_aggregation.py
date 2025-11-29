"""
Advanced Proof Aggregation Tests

Tests for advanced proof aggregation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, AdvancedProofAggregator,
    SimpleAggregationStrategy, WeightedAggregationStrategy, SelectiveAggregationStrategy
)
from qezk.exceptions import ProtocolError, VerificationError


class TestProofAggregation(unittest.TestCase):
    """Test cases for advanced proof aggregation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100)
        self.aggregator = AdvancedProofAggregator(self.qezk)
    
    def test_simple_aggregation(self):
        """Test simple aggregation strategy"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", strategy='simple', seed=100)
        
        self.assertIsNotNone(result.aggregated_proof)
        self.assertEqual(result.metadata['strategy'], 'simple')
        self.assertEqual(result.metadata['num_proofs'], 3)
    
    def test_weighted_aggregation(self):
        """Test weighted aggregation strategy"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", strategy='weighted', seed=100)
        
        self.assertIsNotNone(result.aggregated_proof)
        self.assertEqual(result.metadata['strategy'], 'weighted')
    
    def test_selective_aggregation(self):
        """Test selective aggregation strategy"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", strategy='selective', seed=100)
        
        self.assertIsNotNone(result.aggregated_proof)
        self.assertEqual(result.metadata['strategy'], 'selective')
    
    def test_aggregation_empty_list(self):
        """Test aggregation with empty list"""
        with self.assertRaises(ProtocolError):
            self.aggregator.aggregate([], "Test")
    
    def test_aggregation_statistics(self):
        """Test aggregation statistics"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", seed=100)
        
        self.assertIn('chsh_mean', result.statistics)
        self.assertIn('chsh_std', result.statistics)
        self.assertIn('validity_rate', result.statistics)
    
    def test_aggregation_performance(self):
        """Test aggregation performance metrics"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", seed=100)
        
        self.assertIn('aggregation_time', result.performance)
        self.assertIn('proofs_per_second', result.performance)
        self.assertGreaterEqual(result.performance['aggregation_time'], 0)
    
    def test_batch_aggregation(self):
        """Test batch aggregation"""
        batch1 = [
            self.qezk.prove("Statement 1", "11010110", seed=42),
            self.qezk.prove("Statement 2", "10101010", seed=43)
        ]
        batch2 = [
            self.qezk.prove("Statement 3", "11111111", seed=44)
        ]
        
        batches = [batch1, batch2]
        results = self.aggregator.batch_aggregate(batches, seed=100)
        
        self.assertEqual(len(results), 2)
    
    def test_aggregation_history(self):
        """Test aggregation history"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        self.aggregator.aggregate(proofs, "Test 1", seed=100)
        self.aggregator.aggregate(proofs, "Test 2", seed=101)
        
        history = self.aggregator.get_aggregation_history()
        self.assertGreaterEqual(len(history), 2)
    
    def test_statistics_summary(self):
        """Test statistics summary"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        self.aggregator.aggregate(proofs, "Test 1", seed=100)
        self.aggregator.aggregate(proofs, "Test 2", seed=101)
        
        summary = self.aggregator.get_statistics_summary()
        
        self.assertIn('total_aggregations', summary)
        self.assertIn('total_proofs_aggregated', summary)
        self.assertGreaterEqual(summary['total_aggregations'], 2)
    
    def test_custom_strategy(self):
        """Test custom aggregation strategy"""
        class CustomStrategy(SimpleAggregationStrategy):
            pass
        
        custom = CustomStrategy()
        self.aggregator.register_strategy('custom', custom)
        
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.aggregator.aggregate(proofs, "Test", strategy='custom', seed=100)
        
        self.assertIsNotNone(result.aggregated_proof)
    
    def test_optimize_batch_size(self):
        """Test batch size optimization"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(50)
        ]
        
        optimal_size = self.aggregator.optimize_batch_size(proofs)
        
        self.assertGreaterEqual(optimal_size, 10)
        self.assertLessEqual(optimal_size, 100)


if __name__ == '__main__':
    unittest.main()


