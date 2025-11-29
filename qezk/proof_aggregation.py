"""
Advanced Proof Aggregation

Advanced proof aggregation system with optimization, batching, and analytics.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import time

from .protocol import QuantumEntanglementZK, QEZKProof
from .exceptions import ProtocolError, VerificationError


@dataclass
class AggregationResult:
    """Result of proof aggregation"""
    aggregated_proof: QEZKProof
    metadata: Dict[str, Any]
    statistics: Dict[str, Any]
    performance: Dict[str, float]


class AggregationStrategy:
    """Base class for aggregation strategies"""
    
    def aggregate(self, proofs: List[QEZKProof], qezk: QuantumEntanglementZK,
                 statement: str, seed: Optional[int] = None) -> QEZKProof:
        """
        Aggregate proofs using this strategy
        
        Args:
            proofs: Proofs to aggregate
            qezk: QE-ZK instance
            statement: Statement for aggregated proof
            seed: Optional random seed
            
        Returns:
            Aggregated proof
        """
        raise NotImplementedError


class SimpleAggregationStrategy(AggregationStrategy):
    """Simple aggregation: combine all proofs"""
    
    def aggregate(self, proofs: List[QEZKProof], qezk: QuantumEntanglementZK,
                 statement: str, seed: Optional[int] = None) -> QEZKProof:
        """Simple aggregation strategy"""
        # Combine validity bits and CHSH values
        validity_bits = ''.join('1' if p.is_valid else '0' for p in proofs)
        chsh_bits = ''.join(self._float_to_bits(p.chsh_value, 4) for p in proofs)
        
        # Hash all results
        import hashlib
        all_results = ''.join(
            ''.join(str(r) for r in p.prover_results[:8]) for p in proofs
        )
        hash_bits = ''.join(
            format(b, '08b') for b in hashlib.sha256(all_results.encode()).digest()[:4]
        )
        
        witness = validity_bits + chsh_bits + hash_bits
        return qezk.prove(statement, witness, seed)
    
    def _float_to_bits(self, value: float, num_bits: int = 4) -> str:
        """Convert float to bit string"""
        normalized = max(0, min(1, value / 3.0))
        int_value = int(normalized * (2**num_bits - 1))
        return format(int_value, f'0{num_bits}b')


class WeightedAggregationStrategy(AggregationStrategy):
    """Weighted aggregation: weight proofs by CHSH value"""
    
    def aggregate(self, proofs: List[QEZKProof], qezk: QuantumEntanglementZK,
                 statement: str, seed: Optional[int] = None) -> QEZKProof:
        """Weighted aggregation strategy"""
        # Calculate weights based on CHSH values
        weights = [p.chsh_value / 3.0 for p in proofs]  # Normalize to 0-1
        total_weight = sum(weights)
        
        if total_weight == 0:
            weights = [1.0 / len(proofs)] * len(proofs)
        else:
            weights = [w / total_weight for w in weights]
        
        # Weighted combination
        weighted_bits = []
        for proof, weight in zip(proofs, weights):
            validity_bit = '1' if proof.is_valid else '0'
            chsh_bits = self._float_to_bits(proof.chsh_value, 4)
            weight_bits = self._float_to_bits(weight, 4)
            weighted_bits.append(validity_bit + chsh_bits + weight_bits)
        
        witness = ''.join(weighted_bits)
        return qezk.prove(statement, witness, seed)
    
    def _float_to_bits(self, value: float, num_bits: int = 4) -> str:
        """Convert float to bit string"""
        normalized = max(0, min(1, value))
        int_value = int(normalized * (2**num_bits - 1))
        return format(int_value, f'0{num_bits}b')


class SelectiveAggregationStrategy(AggregationStrategy):
    """Selective aggregation: only aggregate valid proofs"""
    
    def __init__(self, min_chsh: float = 2.0):
        """
        Initialize selective aggregation
        
        Args:
            min_chsh: Minimum CHSH value for inclusion
        """
        self.min_chsh = min_chsh
    
    def aggregate(self, proofs: List[QEZKProof], qezk: QuantumEntanglementZK,
                 statement: str, seed: Optional[int] = None) -> QEZKProof:
        """Selective aggregation strategy"""
        # Filter proofs
        valid_proofs = [p for p in proofs if p.is_valid and p.chsh_value >= self.min_chsh]
        
        if not valid_proofs:
            # If no valid proofs, use all proofs
            valid_proofs = proofs
        
        # Aggregate only valid proofs
        validity_bits = ''.join('1' if p.is_valid else '0' for p in valid_proofs)
        chsh_bits = ''.join(self._float_to_bits(p.chsh_value, 4) for p in valid_proofs)
        
        import hashlib
        all_results = ''.join(
            ''.join(str(r) for r in p.prover_results[:8]) for p in valid_proofs
        )
        hash_bits = ''.join(
            format(b, '08b') for b in hashlib.sha256(all_results.encode()).digest()[:4]
        )
        
        witness = validity_bits + chsh_bits + hash_bits
        return qezk.prove(statement, witness, seed)
    
    def _float_to_bits(self, value: float, num_bits: int = 4) -> str:
        """Convert float to bit string"""
        normalized = max(0, min(1, value / 3.0))
        int_value = int(normalized * (2**num_bits - 1))
        return format(int_value, f'0{num_bits}b')


class AdvancedProofAggregator:
    """
    Advanced proof aggregation system
    
    Provides multiple aggregation strategies, batching, and analytics.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK,
                 default_strategy: Optional[AggregationStrategy] = None):
        """
        Initialize advanced aggregator
        
        Args:
            qezk: QE-ZK instance
            default_strategy: Default aggregation strategy
        """
        self.qezk = qezk
        self.default_strategy = default_strategy or SimpleAggregationStrategy()
        self.strategies = {
            'simple': SimpleAggregationStrategy(),
            'weighted': WeightedAggregationStrategy(),
            'selective': SelectiveAggregationStrategy()
        }
        self.aggregation_history: List[Dict[str, Any]] = []
    
    def aggregate(self,
                 proofs: List[QEZKProof],
                 statement: str = "Aggregated proof",
                 strategy: str = 'simple',
                 verify_all: bool = False,
                 seed: Optional[int] = None) -> AggregationResult:
        """
        Aggregate proofs with advanced features
        
        Args:
            proofs: Proofs to aggregate
            statement: Statement for aggregated proof
            strategy: Aggregation strategy ('simple', 'weighted', 'selective')
            verify_all: Whether to verify all proofs before aggregation
            seed: Optional random seed
            
        Returns:
            AggregationResult with proof, metadata, statistics, and performance
        """
        if not proofs:
            raise ProtocolError("Cannot aggregate empty proof list")
        
        start_time = time.time()
        
        # Verify all proofs if requested
        if verify_all:
            valid_count = sum(1 for p in proofs if p.is_valid)
            if valid_count != len(proofs):
                raise VerificationError(
                    f"Not all proofs are valid: {valid_count}/{len(proofs)}"
                )
        
        # Get strategy
        aggregation_strategy = self.strategies.get(strategy, self.default_strategy)
        
        # Aggregate
        aggregated_proof = aggregation_strategy.aggregate(
            proofs, self.qezk, statement, seed
        )
        
        # Calculate statistics
        statistics = self._calculate_statistics(proofs, aggregated_proof)
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        performance = {
            'aggregation_time': elapsed_time,
            'proofs_per_second': len(proofs) / elapsed_time if elapsed_time > 0 else 0
        }
        
        # Metadata
        metadata = {
            'num_proofs': len(proofs),
            'strategy': strategy,
            'all_valid': all(p.is_valid for p in proofs),
            'valid_count': sum(1 for p in proofs if p.is_valid),
            'avg_chsh': np.mean([p.chsh_value for p in proofs]),
            'aggregated_chsh': aggregated_proof.chsh_value,
            'aggregated_valid': aggregated_proof.is_valid
        }
        
        # Record in history
        self.aggregation_history.append({
            'timestamp': time.time(),
            'num_proofs': len(proofs),
            'strategy': strategy,
            'performance': performance
        })
        
        return AggregationResult(
            aggregated_proof=aggregated_proof,
            metadata=metadata,
            statistics=statistics,
            performance=performance
        )
    
    def _calculate_statistics(self, proofs: List[QEZKProof],
                             aggregated: QEZKProof) -> Dict[str, Any]:
        """Calculate aggregation statistics"""
        chsh_values = [p.chsh_value for p in proofs]
        
        return {
            'chsh_mean': np.mean(chsh_values),
            'chsh_std': np.std(chsh_values),
            'chsh_min': np.min(chsh_values),
            'chsh_max': np.max(chsh_values),
            'chsh_median': np.median(chsh_values),
            'validity_rate': sum(1 for p in proofs if p.is_valid) / len(proofs),
            'chsh_improvement': aggregated.chsh_value - np.mean(chsh_values),
            'aggregated_chsh': aggregated.chsh_value
        }
    
    def batch_aggregate(self,
                       proof_batches: List[List[QEZKProof]],
                       statements: Optional[List[str]] = None,
                       strategy: str = 'simple',
                       verify_all: bool = False,
                       seed: Optional[int] = None) -> List[AggregationResult]:
        """
        Aggregate multiple batches of proofs
        
        Args:
            proof_batches: List of proof batches
            statements: Optional statements for each batch
            strategy: Aggregation strategy
            verify_all: Whether to verify all proofs
            seed: Optional random seed
            
        Returns:
            List of AggregationResult objects
        """
        results = []
        
        for i, batch in enumerate(proof_batches):
            statement = statements[i] if statements and i < len(statements) else f"Batch {i+1}"
            result = self.aggregate(batch, statement, strategy, verify_all, seed)
            results.append(result)
        
        return results
    
    def parallel_aggregate(self,
                          proof_batches: List[List[QEZKProof]],
                          statements: Optional[List[str]] = None,
                          strategy: str = 'simple',
                          verify_all: bool = False,
                          seed: Optional[int] = None) -> List[AggregationResult]:
        """
        Parallel aggregation (simulated - actual parallelization would require threading)
        
        Args:
            proof_batches: List of proof batches
            statements: Optional statements for each batch
            strategy: Aggregation strategy
            verify_all: Whether to verify all proofs
            seed: Optional random seed
            
        Returns:
            List of AggregationResult objects
        """
        # For now, sequential (can be extended with threading/multiprocessing)
        return self.batch_aggregate(proof_batches, statements, strategy, verify_all, seed)
    
    def get_aggregation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get aggregation history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of aggregation records
        """
        if limit:
            return self.aggregation_history[-limit:]
        return self.aggregation_history
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get summary statistics from aggregation history"""
        if not self.aggregation_history:
            return {}
        
        total_aggregations = len(self.aggregation_history)
        total_proofs = sum(r['num_proofs'] for r in self.aggregation_history)
        avg_time = np.mean([r['performance']['aggregation_time'] 
                           for r in self.aggregation_history])
        
        strategy_counts = defaultdict(int)
        for r in self.aggregation_history:
            strategy_counts[r['strategy']] += 1
        
        return {
            'total_aggregations': total_aggregations,
            'total_proofs_aggregated': total_proofs,
            'avg_aggregation_time': avg_time,
            'strategy_usage': dict(strategy_counts),
            'avg_proofs_per_aggregation': total_proofs / total_aggregations if total_aggregations > 0 else 0
        }
    
    def register_strategy(self, name: str, strategy: AggregationStrategy):
        """
        Register custom aggregation strategy
        
        Args:
            name: Strategy name
            strategy: Strategy instance
        """
        self.strategies[name] = strategy
    
    def optimize_batch_size(self, 
                           proofs: List[QEZKProof],
                           min_batch_size: int = 10,
                           max_batch_size: int = 100) -> int:
        """
        Optimize batch size for aggregation
        
        Args:
            proofs: Proofs to optimize for
            min_batch_size: Minimum batch size
            max_batch_size: Maximum batch size
            
        Returns:
            Optimal batch size
        """
        # Simple heuristic: use batch size that balances performance
        num_proofs = len(proofs)
        
        if num_proofs <= min_batch_size:
            return num_proofs
        
        # Optimal batch size based on number of proofs
        optimal = min(max_batch_size, max(min_batch_size, num_proofs // 10))
        return optimal


