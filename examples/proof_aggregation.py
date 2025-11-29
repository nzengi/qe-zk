"""
Advanced Proof Aggregation Example

Demonstrates advanced proof aggregation with multiple strategies and analytics.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, AdvancedProofAggregator,
    SimpleAggregationStrategy, WeightedAggregationStrategy, SelectiveAggregationStrategy
)


def example_simple_aggregation():
    """Example: Simple aggregation strategy"""
    print("=" * 70)
    print("Example 1: Simple Aggregation")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Generate multiple proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(5)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print()
    
    # Aggregate with simple strategy
    result = aggregator.aggregate(proofs, "Simple aggregated proof", 
                                 strategy='simple', seed=100)
    
    print("Aggregation Result:")
    print(f"  Strategy: {result.metadata['strategy']}")
    print(f"  Number of proofs: {result.metadata['num_proofs']}")
    print(f"  Average CHSH: {result.metadata['avg_chsh']:.4f}")
    print(f"  Aggregated CHSH: {result.metadata['aggregated_chsh']:.4f}")
    print(f"  Aggregation time: {result.performance['aggregation_time']:.4f}s")
    print()


def example_weighted_aggregation():
    """Example: Weighted aggregation strategy"""
    print("=" * 70)
    print("Example 2: Weighted Aggregation")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Generate proofs with varying CHSH values
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(5)
    ]
    
    print("Individual Proof CHSH Values:")
    for i, proof in enumerate(proofs):
        print(f"  Proof {i+1}: {proof.chsh_value:.4f}")
    print()
    
    # Aggregate with weighted strategy
    result = aggregator.aggregate(proofs, "Weighted aggregated proof",
                                 strategy='weighted', seed=100)
    
    print("Weighted Aggregation Result:")
    print(f"  Aggregated CHSH: {result.metadata['aggregated_chsh']:.4f}")
    print(f"  CHSH Improvement: {result.statistics['chsh_improvement']:.4f}")
    print()


def example_selective_aggregation():
    """Example: Selective aggregation strategy"""
    print("=" * 70)
    print("Example 3: Selective Aggregation")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Generate proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(5)
    ]
    
    print(f"Generated {len(proofs)} proofs")
    print(f"Valid proofs: {sum(1 for p in proofs if p.is_valid)}")
    print()
    
    # Aggregate with selective strategy (min CHSH = 2.0)
    result = aggregator.aggregate(proofs, "Selective aggregated proof",
                                 strategy='selective', seed=100)
    
    print("Selective Aggregation Result:")
    print(f"  Strategy: {result.metadata['strategy']}")
    print(f"  Aggregated CHSH: {result.metadata['aggregated_chsh']:.4f}")
    print()


def example_batch_aggregation():
    """Example: Batch aggregation"""
    print("=" * 70)
    print("Example 4: Batch Aggregation")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Create batches
    batch1 = [
        qezk.prove(f"Batch1 Statement {i}", "11010110", seed=42 + i)
        for i in range(3)
    ]
    batch2 = [
        qezk.prove(f"Batch2 Statement {i}", "10101010", seed=50 + i)
        for i in range(2)
    ]
    
    batches = [batch1, batch2]
    statements = ["Batch 1 aggregated", "Batch 2 aggregated"]
    
    # Aggregate batches
    results = aggregator.batch_aggregate(batches, statements, strategy='simple', seed=100)
    
    print(f"Aggregated {len(results)} batches:")
    for i, result in enumerate(results):
        print(f"  Batch {i+1}: {result.metadata['num_proofs']} proofs, "
              f"CHSH={result.metadata['aggregated_chsh']:.4f}")
    print()


def example_aggregation_statistics():
    """Example: Aggregation statistics and analytics"""
    print("=" * 70)
    print("Example 5: Aggregation Statistics")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Perform multiple aggregations
    for i in range(3):
        proofs = [
            qezk.prove(f"Statement {j}", "11010110", seed=42 + i * 10 + j)
            for j in range(3)
        ]
        aggregator.aggregate(proofs, f"Aggregation {i+1}", seed=100 + i)
    
    # Get statistics summary
    summary = aggregator.get_statistics_summary()
    
    print("Aggregation Statistics Summary:")
    print(f"  Total aggregations: {summary['total_aggregations']}")
    print(f"  Total proofs aggregated: {summary['total_proofs_aggregated']}")
    print(f"  Average aggregation time: {summary['avg_aggregation_time']:.4f}s")
    print(f"  Average proofs per aggregation: {summary['avg_proofs_per_aggregation']:.2f}")
    print(f"  Strategy usage: {summary['strategy_usage']}")
    print()


def example_custom_strategy():
    """Example: Custom aggregation strategy"""
    print("=" * 70)
    print("Example 6: Custom Aggregation Strategy")
    print("=" * 70)
    print()
    
    qezk = QuantumEntanglementZK(num_epr_pairs=100)
    aggregator = AdvancedProofAggregator(qezk)
    
    # Create custom strategy (using simple as base)
    class CustomStrategy(SimpleAggregationStrategy):
        def aggregate(self, proofs, qezk, statement, seed=None):
            # Custom logic: prioritize proofs with higher CHSH
            sorted_proofs = sorted(proofs, key=lambda p: p.chsh_value, reverse=True)
            return super().aggregate(sorted_proofs[:3], qezk, statement, seed)
    
    # Register custom strategy
    aggregator.register_strategy('custom', CustomStrategy())
    
    # Generate proofs
    proofs = [
        qezk.prove(f"Statement {i}", "11010110", seed=42 + i)
        for i in range(5)
    ]
    
    # Use custom strategy
    result = aggregator.aggregate(proofs, "Custom aggregated proof",
                                 strategy='custom', seed=100)
    
    print("Custom Strategy Result:")
    print(f"  Strategy: {result.metadata['strategy']}")
    print(f"  Aggregated CHSH: {result.metadata['aggregated_chsh']:.4f}")
    print()


def main():
    """Run all examples"""
    example_simple_aggregation()
    example_weighted_aggregation()
    example_selective_aggregation()
    example_batch_aggregation()
    example_aggregation_statistics()
    example_custom_strategy()
    
    print("=" * 70)
    print("Advanced Proof Aggregation Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


