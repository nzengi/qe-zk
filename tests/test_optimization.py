"""
Optimization Tests

Tests for performance and memory optimizations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from qezk import MemoryOptimizer, PerformanceOptimizer


class TestOptimization(unittest.TestCase):
    """Test cases for optimization utilities"""
    
    def test_memory_optimization(self):
        """Test memory optimization"""
        # Create test arrays
        arrays = [
            np.array([1, 2, 3, 4], dtype=np.complex128),
            np.array([1+1j, 2+2j, 3+3j, 4+4j], dtype=np.complex128)
        ]
        
        optimized = MemoryOptimizer.optimize_array_memory(arrays)
        
        # First array should be float32 (real only)
        self.assertEqual(optimized[0].dtype, np.float32)
        
        # Second array should be complex64
        self.assertEqual(optimized[1].dtype, np.complex64)
    
    def test_batch_processing(self):
        """Test batch processing"""
        items = list(range(2500))
        batch_size = 1000
        
        batches = list(MemoryOptimizer.batch_process(items, batch_size))
        
        self.assertEqual(len(batches), 3)  # 1000, 1000, 500
        self.assertEqual(len(batches[0]), 1000)
        self.assertEqual(len(batches[1]), 1000)
        self.assertEqual(len(batches[2]), 500)
    
    def test_precompute_gates(self):
        """Test gate precomputation"""
        gates = PerformanceOptimizer.precompute_gates()
        
        self.assertIn('H', gates)
        self.assertIn('X', gates)
        self.assertIn('Y', gates)
        self.assertIn('Z', gates)
        self.assertIn('I', gates)
        
        # Check dtype is complex64 (optimized)
        self.assertEqual(gates['H'].dtype, np.complex64)


if __name__ == '__main__':
    unittest.main()


