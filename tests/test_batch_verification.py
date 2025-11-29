"""
Batch Verification Optimization Tests

Tests for batch verification optimization functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from qezk import (
    QuantumEntanglementZK, BatchVerifier, OptimizedBatchVerifier
)
from qezk.exceptions import ProtocolError, VerificationError


class TestBatchVerification(unittest.TestCase):
    """Test cases for batch verification"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.qezk = QuantumEntanglementZK(num_epr_pairs=100)
        self.verifier = BatchVerifier(self.qezk, use_cache=True)
    
    def test_basic_batch_verification(self):
        """Test basic batch verification"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.verifier.verify_batch(proofs, parallel=False, verify_all=False)
        
        self.assertEqual(len(result.results), 3)
        self.assertEqual(result.metadata['num_proofs'], 3)
        self.assertIn('verification_time', result.performance)
    
    def test_parallel_verification(self):
        """Test parallel batch verification"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(5)
        ]
        
        result = self.verifier.verify_batch(proofs, parallel=True, verify_all=False)
        
        self.assertEqual(len(result.results), 5)
        self.assertTrue(result.performance['parallel'])
    
    def test_verification_cache(self):
        """Test verification cache"""
        proof = self.qezk.prove("I know the secret", "11010110", seed=42)
        
        # First verification (cache miss)
        result1 = self.verifier.verify_batch([proof], parallel=False, verify_all=False)
        
        # Second verification (cache hit)
        result2 = self.verifier.verify_batch([proof], parallel=False, verify_all=False)
        
        # Cache should have hit
        cache_stats = self.verifier.cache.get_stats()
        self.assertGreater(cache_stats['hits'], 0)
    
    def test_verify_all_requirement(self):
        """Test verify_all requirement"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        # Should not raise if verify_all=False
        result = self.verifier.verify_batch(proofs, verify_all=False)
        self.assertIsNotNone(result)
        
        # May raise if verify_all=True and some invalid
        # (depends on proof validity)
    
    def test_empty_proof_list(self):
        """Test verification with empty list"""
        with self.assertRaises(ProtocolError):
            self.verifier.verify_batch([], verify_all=False)
    
    def test_verification_statistics(self):
        """Test verification statistics"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = self.verifier.verify_batch(proofs, parallel=False, verify_all=False)
        
        self.assertIn('chsh_mean', result.statistics)
        self.assertIn('chsh_std', result.statistics)
        self.assertIn('validity_rate', result.statistics)
    
    def test_verification_history(self):
        """Test verification history"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        self.verifier.verify_batch(proofs, parallel=False, verify_all=False)
        self.verifier.verify_batch(proofs, parallel=False, verify_all=False)
        
        history = self.verifier.get_verification_history()
        self.assertGreaterEqual(len(history), 2)
    
    def test_statistics_summary(self):
        """Test statistics summary"""
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        self.verifier.verify_batch(proofs, parallel=False, verify_all=False)
        
        summary = self.verifier.get_statistics_summary()
        
        self.assertIn('total_verifications', summary)
        self.assertIn('total_proofs_verified', summary)
        self.assertGreaterEqual(summary['total_verifications'], 1)
    
    def test_optimized_verifier(self):
        """Test optimized batch verifier"""
        optimized_verifier = OptimizedBatchVerifier(self.qezk, cache_size=1000)
        
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = optimized_verifier.verify_batch_optimized(proofs, parallel=True, verify_all=False)
        
        self.assertEqual(len(result.results), 3)
    
    def test_vectorized_verification(self):
        """Test vectorized batch verification"""
        optimized_verifier = OptimizedBatchVerifier(self.qezk, enable_vectorization=True)
        
        proofs = [
            self.qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
            for i in range(3)
        ]
        
        result = optimized_verifier.verify_batch_vectorized(proofs, verify_all=False)
        
        self.assertEqual(len(result.results), 3)
        self.assertTrue(result.performance['vectorized'])
    
    def test_cache_clear(self):
        """Test cache clearing"""
        proof = self.qezk.prove("I know the secret", "11010110", seed=42)
        
        self.verifier.verify_batch([proof], parallel=False, verify_all=False)
        
        # Clear cache
        self.verifier.cache.clear()
        
        cache_stats = self.verifier.cache.get_stats()
        self.assertEqual(cache_stats['size'], 0)
        self.assertEqual(cache_stats['hits'], 0)
        self.assertEqual(cache_stats['misses'], 0)
    
    def test_batch_verification_batches(self):
        """Test verifying multiple batches"""
        batch1 = [
            self.qezk.prove("Statement 1", "11010110", seed=42),
            self.qezk.prove("Statement 2", "10101010", seed=43)
        ]
        batch2 = [
            self.qezk.prove("Statement 3", "11111111", seed=44)
        ]
        
        batches = [batch1, batch2]
        results = self.verifier.verify_batches(batches, parallel=False, verify_all=False)
        
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main()

