"""
Batch Verification Optimization

Optimized batch verification system for multiple proofs.
Includes parallel verification, caching, and performance optimizations.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .protocol import QuantumEntanglementZK, QEZKProof
from .exceptions import ProtocolError, VerificationError


@dataclass
class BatchVerificationResult:
    """Result of batch verification"""
    results: List[Tuple[QEZKProof, bool, float]]  # (proof, is_valid, chsh_value)
    statistics: Dict[str, Any]
    performance: Dict[str, float]
    metadata: Dict[str, Any]


class VerificationCache:
    """Cache for verification results"""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize verification cache
        
        Args:
            max_size: Maximum cache size
        """
        self.cache: Dict[str, Tuple[bool, float]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _cache_key(self, proof: QEZKProof) -> str:
        """Generate cache key from proof"""
        # Use statement and first few results as key
        key_parts = [
            proof.statement,
            str(proof.prover_results[:10]),
            str(proof.verifier_results[:10]),
            str(proof.measurement_bases[:10])
        ]
        return hash(tuple(key_parts))
    
    def get(self, proof: QEZKProof) -> Optional[Tuple[bool, float]]:
        """
        Get cached verification result
        
        Args:
            proof: Proof to verify
            
        Returns:
            Cached (is_valid, chsh_value) or None
        """
        key = self._cache_key(proof)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, proof: QEZKProof, is_valid: bool, chsh_value: float):
        """
        Cache verification result
        
        Args:
            proof: Proof that was verified
            is_valid: Verification result
            chsh_value: CHSH value
        """
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            self.cache.pop(next(iter(self.cache)))
        
        key = self._cache_key(proof)
        self.cache[key] = (is_valid, chsh_value)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class BatchVerifier:
    """
    Optimized batch verifier
    
    Verifies multiple proofs efficiently with optimizations.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK, use_cache: bool = True,
                 max_workers: Optional[int] = None):
        """
        Initialize batch verifier
        
        Args:
            qezk: QE-ZK instance
            use_cache: Whether to use verification cache
            max_workers: Maximum parallel workers (None = auto)
        """
        self.qezk = qezk
        self.cache = VerificationCache() if use_cache else None
        self.max_workers = max_workers
        self.verification_history: List[Dict[str, Any]] = []
    
    def verify_single(self, proof: QEZKProof) -> Tuple[bool, float]:
        """
        Verify single proof
        
        Args:
            proof: Proof to verify
            
        Returns:
            Tuple of (is_valid, chsh_value)
        """
        # Check cache
        if self.cache:
            cached = self.cache.get(proof)
            if cached is not None:
                return cached
        
        # Verify
        is_valid, chsh_value = self.qezk.verify(
            proof.prover_results,
            proof.verifier_results,
            proof.measurement_bases
        )
        
        # Cache result
        if self.cache:
            self.cache.set(proof, is_valid, chsh_value)
        
        return is_valid, chsh_value
    
    def verify_batch(self,
                    proofs: List[QEZKProof],
                    parallel: bool = False,
                    verify_all: bool = True) -> BatchVerificationResult:
        """
        Verify batch of proofs
        
        Args:
            proofs: Proofs to verify
            parallel: Whether to verify in parallel
            verify_all: Whether all proofs must be valid
            
        Returns:
            BatchVerificationResult
        """
        if not proofs:
            raise ProtocolError("Cannot verify empty proof list")
        
        start_time = time.time()
        
        # Verify proofs
        if parallel:
            results = self._verify_parallel(proofs)
        else:
            results = self._verify_sequential(proofs)
        
        # Calculate statistics
        statistics = self._calculate_statistics(results)
        
        # Check if all valid if required
        if verify_all:
            invalid_count = sum(1 for _, is_valid, _ in results if not is_valid)
            if invalid_count > 0:
                raise VerificationError(
                    f"Not all proofs are valid: {len(proofs) - invalid_count}/{len(proofs)}"
                )
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        performance = {
            'verification_time': elapsed_time,
            'proofs_per_second': len(proofs) / elapsed_time if elapsed_time > 0 else 0,
            'parallel': parallel,
            'cache_hit_rate': self.cache.get_stats()['hit_rate'] if self.cache else 0
        }
        
        # Metadata
        metadata = {
            'num_proofs': len(proofs),
            'valid_count': sum(1 for _, is_valid, _ in results if is_valid),
            'invalid_count': sum(1 for _, is_valid, _ in results if not is_valid),
            'verify_all': verify_all
        }
        
        # Record in history
        self.verification_history.append({
            'timestamp': time.time(),
            'num_proofs': len(proofs),
            'performance': performance
        })
        
        return BatchVerificationResult(
            results=results,
            statistics=statistics,
            performance=performance,
            metadata=metadata
        )
    
    def _verify_sequential(self, proofs: List[QEZKProof]) -> List[Tuple[QEZKProof, bool, float]]:
        """Verify proofs sequentially"""
        results = []
        for proof in proofs:
            is_valid, chsh_value = self.verify_single(proof)
            results.append((proof, is_valid, chsh_value))
        return results
    
    def _verify_parallel(self, proofs: List[QEZKProof]) -> List[Tuple[QEZKProof, bool, float]]:
        """Verify proofs in parallel"""
        results = []
        max_workers = self.max_workers or min(len(proofs), 4)  # Default to 4 workers
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all verification tasks with index
            future_to_index = {
                executor.submit(self.verify_single, proof): i
                for i, proof in enumerate(proofs)
            }
            
            # Collect results by index
            index_to_result = {}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    is_valid, chsh_value = future.result()
                    index_to_result[index] = (is_valid, chsh_value)
                except Exception as e:
                    raise VerificationError(f"Verification failed for proof at index {index}: {str(e)}") from e
            
            # Maintain original order
            for i, proof in enumerate(proofs):
                is_valid, chsh_value = index_to_result[i]
                results.append((proof, is_valid, chsh_value))
        
        return results
    
    def _calculate_statistics(self, results: List[Tuple[QEZKProof, bool, float]]) -> Dict[str, Any]:
        """Calculate verification statistics"""
        chsh_values = [chsh for _, _, chsh in results]
        is_valid_list = [is_valid for _, is_valid, _ in results]
        
        return {
            'chsh_mean': np.mean(chsh_values),
            'chsh_std': np.std(chsh_values),
            'chsh_min': np.min(chsh_values),
            'chsh_max': np.max(chsh_values),
            'chsh_median': np.median(chsh_values),
            'validity_rate': sum(is_valid_list) / len(is_valid_list) if is_valid_list else 0,
            'valid_count': sum(is_valid_list),
            'invalid_count': len(is_valid_list) - sum(is_valid_list)
        }
    
    def verify_batches(self,
                      proof_batches: List[List[QEZKProof]],
                      parallel: bool = False,
                      verify_all: bool = True) -> List[BatchVerificationResult]:
        """
        Verify multiple batches of proofs
        
        Args:
            proof_batches: List of proof batches
            parallel: Whether to verify in parallel
            verify_all: Whether all proofs must be valid
            
        Returns:
            List of BatchVerificationResult objects
        """
        results = []
        for batch in proof_batches:
            result = self.verify_batch(batch, parallel, verify_all)
            results.append(result)
        return results
    
    def get_verification_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get verification history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of verification records
        """
        if limit:
            return self.verification_history[-limit:]
        return self.verification_history
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get summary statistics from verification history"""
        if not self.verification_history:
            return {}
        
        total_verifications = len(self.verification_history)
        total_proofs = sum(r['num_proofs'] for r in self.verification_history)
        avg_time = np.mean([r['performance']['verification_time']
                           for r in self.verification_history])
        
        return {
            'total_verifications': total_verifications,
            'total_proofs_verified': total_proofs,
            'avg_verification_time': avg_time,
            'avg_proofs_per_verification': total_proofs / total_verifications if total_verifications > 0 else 0,
            'cache_stats': self.cache.get_stats() if self.cache else {}
        }


class OptimizedBatchVerifier:
    """
    Highly optimized batch verifier
    
    Uses advanced optimizations for maximum performance.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK,
                 cache_size: int = 1000,
                 max_workers: Optional[int] = None,
                 enable_vectorization: bool = True):
        """
        Initialize optimized batch verifier
        
        Args:
            qezk: QE-ZK instance
            cache_size: Verification cache size
            max_workers: Maximum parallel workers
            enable_vectorization: Enable vectorized operations
        """
        self.qezk = qezk
        self.cache = VerificationCache(max_size=cache_size)
        self.max_workers = max_workers
        self.enable_vectorization = enable_vectorization
        self.batch_verifier = BatchVerifier(qezk, use_cache=True, max_workers=max_workers)
    
    def verify_batch_optimized(self,
                               proofs: List[QEZKProof],
                               parallel: bool = True,
                               verify_all: bool = True) -> BatchVerificationResult:
        """
        Optimized batch verification
        
        Args:
            proofs: Proofs to verify
            parallel: Whether to verify in parallel
            verify_all: Whether all proofs must be valid
            
        Returns:
            BatchVerificationResult
        """
        # Use batch verifier with optimizations
        return self.batch_verifier.verify_batch(proofs, parallel, verify_all)
    
    def verify_batch_vectorized(self,
                               proofs: List[QEZKProof],
                               verify_all: bool = True) -> BatchVerificationResult:
        """
        Vectorized batch verification (optimized for NumPy)
        
        Args:
            proofs: Proofs to verify
            verify_all: Whether all proofs must be valid
            
        Returns:
            BatchVerificationResult
        """
        if not self.enable_vectorization:
            return self.verify_batch_optimized(proofs, parallel=False, verify_all=verify_all)
        
        start_time = time.time()
        
        # Vectorized CHSH calculation for all proofs
        results = []
        for proof in proofs:
            # Check cache first
            cached = self.cache.get(proof)
            if cached is not None:
                results.append((proof, cached[0], cached[1]))
                continue
            
            # Verify
            is_valid, chsh_value = self.qezk.verify(
                proof.prover_results,
                proof.verifier_results,
                proof.measurement_bases
            )
            
            # Cache
            self.cache.set(proof, is_valid, chsh_value)
            results.append((proof, is_valid, chsh_value))
        
        # Calculate statistics
        statistics = self._calculate_statistics_vectorized(results)
        
        # Check if all valid if required
        if verify_all:
            invalid_count = sum(1 for _, is_valid, _ in results if not is_valid)
            if invalid_count > 0:
                raise VerificationError(
                    f"Not all proofs are valid: {len(proofs) - invalid_count}/{len(proofs)}"
                )
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        performance = {
            'verification_time': elapsed_time,
            'proofs_per_second': len(proofs) / elapsed_time if elapsed_time > 0 else 0,
            'vectorized': True,
            'cache_hit_rate': self.cache.get_stats()['hit_rate']
        }
        
        # Metadata
        metadata = {
            'num_proofs': len(proofs),
            'valid_count': sum(1 for _, is_valid, _ in results if is_valid),
            'invalid_count': sum(1 for _, is_valid, _ in results if not is_valid),
            'verify_all': verify_all
        }
        
        return BatchVerificationResult(
            results=results,
            statistics=statistics,
            performance=performance,
            metadata=metadata
        )
    
    def _calculate_statistics_vectorized(self,
                                        results: List[Tuple[QEZKProof, bool, float]]) -> Dict[str, Any]:
        """Calculate statistics using vectorized operations"""
        chsh_values = np.array([chsh for _, _, chsh in results])
        is_valid_list = np.array([is_valid for _, is_valid, _ in results])
        
        return {
            'chsh_mean': float(np.mean(chsh_values)),
            'chsh_std': float(np.std(chsh_values)),
            'chsh_min': float(np.min(chsh_values)),
            'chsh_max': float(np.max(chsh_values)),
            'chsh_median': float(np.median(chsh_values)),
            'validity_rate': float(np.mean(is_valid_list)),
            'valid_count': int(np.sum(is_valid_list)),
            'invalid_count': int(len(is_valid_list) - np.sum(is_valid_list))
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Clear verification cache"""
        self.cache.clear()

