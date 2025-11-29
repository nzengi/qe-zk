"""
Simulation Framework

This module provides simulation and testing capabilities for the QE-ZK protocol.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .protocol import QuantumEntanglementZK
from .exceptions import ProtocolError


class QEZKSimulation:
    """
    Simulation framework for testing QE-ZK
    
    Provides methods for running multiple protocol trials and
    analyzing performance across different statements and witnesses.
    """
    
    def __init__(self, num_epr_pairs: int = 1000):
        """
        Initialize simulation framework
        
        Args:
            num_epr_pairs: Number of EPR pairs to use in simulations
        """
        self.qezk = QuantumEntanglementZK(num_epr_pairs=num_epr_pairs)
    
    def simulate_protocol(self, statement: str, witness: str, 
                         num_trials: int = 10, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate QE-ZK protocol multiple times
        
        Runs the protocol multiple times and collects statistics.
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information) as bit string
            num_trials: Number of simulation trials
            seed: Optional random seed for reproducibility
            
        Returns:
            Dictionary containing simulation results and statistics
        """
        results = {
            'success_count': 0,
            'chsh_values': [],
            'valid_proofs': 0,
            'total_trials': num_trials
        }
        
        for trial in range(num_trials):
            trial_seed = seed + trial if seed is not None else None
            proof = self.qezk.prove(statement, witness, seed=trial_seed)
            
            results['chsh_values'].append(proof.chsh_value)
            if proof.is_valid:
                results['success_count'] += 1
                results['valid_proofs'] += 1
        
        results['success_rate'] = results['success_count'] / num_trials
        results['avg_chsh'] = np.mean(results['chsh_values'])
        results['std_chsh'] = np.std(results['chsh_values'])
        
        return results
    
    def performance_analysis(self, statements: List[str], witnesses: List[str]) -> Dict[str, Any]:
        """
        Performance analysis across different statements and witnesses
        
        Runs simulations for multiple statement-witness pairs and aggregates results.
        
        Args:
            statements: List of statements to prove
            witnesses: List of corresponding witnesses (must match length)
            
        Returns:
            Dictionary containing aggregated performance metrics
        """
        if len(statements) != len(witnesses):
            raise ProtocolError("statements and witnesses must have the same length")
        
        all_results = []
        
        for statement, witness in zip(statements, witnesses):
            result = self.simulate_protocol(statement, witness)
            all_results.append(result)
        
        return {
            'individual_results': all_results,
            'overall_success_rate': np.mean([r['success_rate'] for r in all_results]),
            'overall_avg_chsh': np.mean([r['avg_chsh'] for r in all_results])
        }

