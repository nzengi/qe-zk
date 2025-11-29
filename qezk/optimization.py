"""
Performance and Memory Optimizations

Optimization utilities for production use.
"""

import numpy as np
from typing import List, Optional
import gc


class MemoryOptimizer:
    """
    Memory optimization utilities
    """
    
    @staticmethod
    def optimize_array_memory(arrays: List[np.ndarray]) -> List[np.ndarray]:
        """
        Optimize memory usage of arrays by using appropriate dtypes
        
        Args:
            arrays: List of numpy arrays
            
        Returns:
            List of optimized arrays
        """
        optimized = []
        for arr in arrays:
            # Use float32 instead of complex128 if precision allows
            if arr.dtype == np.complex128:
                # Check if we can use float32
                if np.allclose(arr.imag, 0):
                    optimized.append(arr.real.astype(np.float32))
                else:
                    optimized.append(arr.astype(np.complex64))  # Use complex64 instead
            else:
                optimized.append(arr)
        
        return optimized
    
    @staticmethod
    def clear_memory():
        """Force garbage collection"""
        gc.collect()
    
    @staticmethod
    def batch_process(items: List, batch_size: int = 1000):
        """
        Process items in batches to reduce memory usage
        
        Args:
            items: List of items to process
            batch_size: Size of each batch
            
        Yields:
            Batches of items
        """
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
            gc.collect()


class PerformanceOptimizer:
    """
    Performance optimization utilities
    """
    
    @staticmethod
    def vectorize_operations(operations: List[callable], inputs: List) -> np.ndarray:
        """
        Vectorize operations for better performance
        
        Args:
            operations: List of operation functions
            inputs: List of inputs
            
        Returns:
            Vectorized results
        """
        # Use numpy vectorization where possible
        return np.array([op(inp) for op, inp in zip(operations, inputs)])
    
    @staticmethod
    def precompute_gates():
        """
        Precompute common quantum gates for faster access
        """
        gates = {
            'H': np.array([[1, 1], [1, -1]], dtype=np.complex64) / np.sqrt(2),
            'X': np.array([[0, 1], [1, 0]], dtype=np.complex64),
            'Y': np.array([[0, -1j], [1j, 0]], dtype=np.complex64),
            'Z': np.array([[1, 0], [0, -1]], dtype=np.complex64),
            'I': np.eye(2, dtype=np.complex64)
        }
        return gates
    
    @staticmethod
    def cache_bell_states():
        """
        Precompute and cache Bell states
        """
        bell_states = {}
        quantum_prep = __import__('qezk.quantum_state', fromlist=['QuantumStatePreparation']).QuantumStatePreparation()
        prep = quantum_prep
        
        for state_type in ['phi_plus', 'phi_minus', 'psi_plus', 'psi_minus']:
            bell_states[state_type] = prep.create_bell_state(state_type).astype(np.complex64)
        
        return bell_states

