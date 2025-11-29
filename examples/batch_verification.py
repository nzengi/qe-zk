"""
Batch Verification Optimization Example

Demonstrates optimized batch verification with caching and parallel processing.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, BatchVerifier, OptimizedBatchVerifier
)


def example_basic_batch_verification():
    """Example: Basic batch verification"""
    print("=" * 70)
    print("Example 1: Basic Batch Verification")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier = BatchVerifier(qezk, use_cache=True)
    
    # Generate multiple proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(5)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Verify batch
    result = verifier.verify_batch(proofs, parallel=False, verify_all=False)
    
    print("Batch Verification Result:")
    print(f"  Number of proofs: {result.metadata['num_proofs']}")
    print(f"  Valid count: {result.metadata['valid_count']}")
    print(f"  Invalid count: {result.metadata['invalid_count']}")
    print(f"  Verification time: {result.performance['verification_time']:.4f}s")
    print(f"  Proofs per second: {result.performance['proofs_per_second']:.2f}")
    print()


def example_parallel_verification():
    """Example: Parallel batch verification"""
    print("=" * 70)
    print("Example 2: Parallel Batch Verification")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier = BatchVerifier(qezk, use_cache=True, max_workers=4)
    
    # Generate multiple proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(10)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Verify sequentially
    result_seq = verifier.verify_batch(proofs, parallel=False, verify_all=False)
    
    # Verify in parallel
    result_par = verifier.verify_batch(proofs, parallel=True, verify_all=False)
    
    print("Performance Comparison:")
    print(f"  Sequential time: {result_seq.performance['verification_time']:.4f}s")
    print(f"  Parallel time: {result_par.performance['verification_time']:.4f}s")
    print(f"  Speedup: {result_seq.performance['verification_time'] / result_par.performance['verification_time']:.2f}x")
    print()


def example_verification_cache():
    """Example: Verification cache"""
    print("=" * 70)
    print("Example 3: Verification Cache")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier = BatchVerifier(qezk, use_cache=True)
    
    # Generate proof
    proof = qezk.prove("I know the secret", "11010110", seed=42)
    
    # First verification (cache miss)
    result1 = verifier.verify_batch([proof], parallel=False)
    print("First Verification:")
    print(f"  Cache hit rate: {result1.performance['cache_hit_rate']:.2%}")
    print()
    
    # Second verification (cache hit)
    result2 = verifier.verify_batch([proof], parallel=False)
    print("Second Verification (cached):")
    print(f"  Cache hit rate: {result2.performance['cache_hit_rate']:.2%}")
    print(f"  Time: {result2.performance['verification_time']:.6f}s")
    print()
    
    # Get cache stats
    cache_stats = verifier.cache.get_stats()
    print("Cache Statistics:")
    print(f"  Hits: {cache_stats['hits']}")
    print(f"  Misses: {cache_stats['misses']}")
    print(f"  Hit rate: {cache_stats['hit_rate']:.2%}")
    print()


def example_optimized_verification():
    """Example: Optimized batch verification"""
    print("=" * 70)
    print("Example 4: Optimized Batch Verification")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    optimized_verifier = OptimizedBatchVerifier(qezk, cache_size=1000, max_workers=4)
    
    # Generate multiple proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(10)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Optimized verification
    result = optimized_verifier.verify_batch_optimized(proofs, parallel=True, verify_all=False)
    
    print("Optimized Verification Result:")
    print(f"  Number of proofs: {result.metadata['num_proofs']}")
    print(f"  Verification time: {result.performance['verification_time']:.4f}s")
    print(f"  Proofs per second: {result.performance['proofs_per_second']:.2f}")
    print(f"  Cache hit rate: {result.performance['cache_hit_rate']:.2%}")
    print()


def example_vectorized_verification():
    """Example: Vectorized batch verification"""
    print("=" * 70)
    print("Example 5: Vectorized Batch Verification")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    optimized_verifier = OptimizedBatchVerifier(qezk, enable_vectorization=True)
    
    # Generate multiple proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(10)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Vectorized verification
    result = optimized_verifier.verify_batch_vectorized(proofs, verify_all=False)
    
    print("Vectorized Verification Result:")
    print(f"  Vectorized: {result.performance['vectorized']}")
    print(f"  Verification time: {result.performance['verification_time']:.4f}s")
    print(f"  Proofs per second: {result.performance['proofs_per_second']:.2f}")
    print()


def example_batch_statistics():
    """Example: Batch verification statistics"""
    print("=" * 70)
    print("Example 6: Batch Verification Statistics")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier = BatchVerifier(qezk, use_cache=True)
    
    # Perform multiple verifications
    for i in range(3):
        proofs = [
            qezk.prove(f"Statement {j}", "11010110", seed=42 + i * 10 + j)
            for j in range(5)
        ]
        verifier.verify_batch(proofs, parallel=False, verify_all=False)
    
    # Get statistics summary
    summary = verifier.get_statistics_summary()
    
    print("Verification Statistics Summary:")
    print(f"  Total verifications: {summary['total_verifications']}")
    print(f"  Total proofs verified: {summary['total_proofs_verified']}")
    print(f"  Average verification time: {summary['avg_verification_time']:.4f}s")
    print(f"  Average proofs per verification: {summary['avg_proofs_per_verification']:.2f}")
    print()
    
    if summary.get('cache_stats'):
        cache_stats = summary['cache_stats']
        print("Cache Statistics:")
        print(f"  Hit rate: {cache_stats['hit_rate']:.2%}")
        print(f"  Hits: {cache_stats['hits']}")
        print(f"  Misses: {cache_stats['misses']}")
    print()


def main():
    """Run all examples"""
    example_basic_batch_verification()
    example_parallel_verification()
    example_verification_cache()
    example_optimized_verification()
    example_vectorized_verification()
    example_batch_statistics()
    
    print("=" * 70)
    print("Batch Verification Optimization Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


