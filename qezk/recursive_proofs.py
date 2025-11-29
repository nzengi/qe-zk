"""
Recursive Proofs

Support for recursive proofs where a proof can verify another proof.
Includes proof composition, nested proofs, and proof aggregation.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from .protocol import QuantumEntanglementZK, QEZKProof
from .exceptions import ProtocolError, VerificationError


@dataclass
class RecursiveProof:
    """
    Recursive proof structure
    
    Contains a proof that verifies another proof or set of proofs.
    """
    inner_proofs: List[QEZKProof]  # Proofs being verified
    outer_proof: QEZKProof  # Proof that verifies inner proofs
    recursion_depth: int  # Depth of recursion
    is_valid: bool  # Overall validity
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecursiveProver:
    """
    Recursive proof generator
    
    Generates proofs that verify other proofs.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK):
        """
        Initialize recursive prover
        
        Args:
            qezk: QE-ZK instance
        """
        self.qezk = qezk
    
    def prove_proof(self, inner_proof: QEZKProof, 
                   statement: Optional[str] = None,
                   seed: Optional[int] = None) -> QEZKProof:
        """
        Generate proof that verifies another proof
        
        The witness encodes the inner proof's validity and key properties.
        
        Args:
            inner_proof: Proof to verify
            statement: Optional statement (default: proof of inner proof validity)
            seed: Optional random seed
            
        Returns:
            QEZKProof that verifies the inner proof
        """
        # Create statement from inner proof
        if statement is None:
            statement = f"Proof of validity: {inner_proof.statement}"
        
        # Encode inner proof properties into witness
        witness = self._proof_to_witness(inner_proof)
        
        # Generate proof
        outer_proof = self.qezk.prove(statement, witness, seed)
        
        return outer_proof
    
    def _proof_to_witness(self, proof: QEZKProof) -> str:
        """
        Convert proof properties to witness string
        
        Args:
            proof: Proof to encode
            
        Returns:
            Witness string encoding proof properties
        """
        # Encode proof validity, CHSH value, and key properties
        is_valid_bit = '1' if proof.is_valid else '0'
        chsh_bits = self._float_to_bits(proof.chsh_value, num_bits=8)
        results_hash = self._hash_results(proof.prover_results[:16])  # First 16 results
        
        witness = is_valid_bit + chsh_bits + results_hash
        return witness
    
    def _float_to_bits(self, value: float, num_bits: int = 8) -> str:
        """Convert float to bit string"""
        # Normalize to 0-1 range and convert to bits
        normalized = max(0, min(1, value / 3.0))  # CHSH max is ~3.0
        int_value = int(normalized * (2**num_bits - 1))
        return format(int_value, f'0{num_bits}b')
    
    def _hash_results(self, results: List[int]) -> str:
        """Hash results to bit string"""
        import hashlib
        results_str = ''.join(str(r) for r in results)
        hash_bytes = hashlib.sha256(results_str.encode()).digest()
        return ''.join(format(b, '08b') for b in hash_bytes[:4])  # 32 bits


class ProofComposer:
    """
    Proof composer for combining multiple proofs
    
    Combines multiple proofs into a single composite proof.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK):
        """
        Initialize proof composer
        
        Args:
            qezk: QE-ZK instance
        """
        self.qezk = qezk
    
    def compose_proofs(self, proofs: List[QEZKProof],
                      statement: str = "Composite proof",
                      seed: Optional[int] = None) -> QEZKProof:
        """
        Compose multiple proofs into one
        
        Args:
            proofs: List of proofs to compose
            statement: Statement for composite proof
            seed: Optional random seed
            
        Returns:
            Composite proof
        """
        if not proofs:
            raise ProtocolError("Cannot compose empty proof list")
        
        # Aggregate proof properties
        aggregated_witness = self._aggregate_proofs_to_witness(proofs)
        
        # Generate composite proof
        composite_proof = self.qezk.prove(statement, aggregated_witness, seed)
        
        return composite_proof
    
    def _aggregate_proofs_to_witness(self, proofs: List[QEZKProof]) -> str:
        """
        Aggregate multiple proofs into witness string
        
        Args:
            proofs: Proofs to aggregate
            
        Returns:
            Aggregated witness string
        """
        # Combine proof properties
        validity_bits = ''.join('1' if p.is_valid else '0' for p in proofs)
        chsh_bits = ''.join(self._float_to_bits(p.chsh_value, 4) for p in proofs)
        
        # Hash all proofs
        import hashlib
        all_results = ''.join(
            ''.join(str(r) for r in p.prover_results[:8]) for p in proofs
        )
        hash_bits = ''.join(
            format(b, '08b') for b in hashlib.sha256(all_results.encode()).digest()[:4]
        )
        
        return validity_bits + chsh_bits + hash_bits
    
    def _float_to_bits(self, value: float, num_bits: int = 4) -> str:
        """Convert float to bit string"""
        normalized = max(0, min(1, value / 3.0))
        int_value = int(normalized * (2**num_bits - 1))
        return format(int_value, f'0{num_bits}b')


class NestedProofBuilder:
    """
    Nested proof builder
    
    Builds proofs with multiple levels of nesting.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK):
        """
        Initialize nested proof builder
        
        Args:
            qezk: QE-ZK instance
        """
        self.qezk = qezk
        self.recursive_prover = RecursiveProver(qezk)
    
    def build_nested_proof(self, 
                          base_statement: str,
                          base_witness: str,
                          depth: int = 2,
                          seed: Optional[int] = None) -> RecursiveProof:
        """
        Build nested proof with specified depth
        
        Args:
            base_statement: Base statement to prove
            base_witness: Base witness
            depth: Recursion depth
            seed: Optional random seed
            
        Returns:
            RecursiveProof with nested structure
        """
        if depth < 1:
            raise ProtocolError("Depth must be >= 1")
        
        inner_proofs = []
        current_statement = base_statement
        current_witness = base_witness
        
        # Build proofs layer by layer
        for level in range(depth):
            proof = self.qezk.prove(current_statement, current_witness, 
                                   seed=seed + level if seed is not None else None)
            inner_proofs.append(proof)
            
            # Next level proves the current proof
            if level < depth - 1:
                current_statement = f"Proof level {level + 1}: {current_statement}"
                current_witness = self.recursive_prover._proof_to_witness(proof)
        
        # Outer proof verifies the innermost proof
        outer_proof = self.recursive_prover.prove_proof(
            inner_proofs[-1],
            statement=f"Nested proof (depth {depth})",
            seed=seed
        )
        
        # Check overall validity
        is_valid = all(p.is_valid for p in inner_proofs) and outer_proof.is_valid
        
        return RecursiveProof(
            inner_proofs=inner_proofs,
            outer_proof=outer_proof,
            recursion_depth=depth,
            is_valid=is_valid,
            metadata={
                'base_statement': base_statement,
                'total_proofs': len(inner_proofs) + 1
            }
        )


class ProofAggregator:
    """
    Proof aggregator
    
    Aggregates multiple proofs into a single proof with verification.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK):
        """
        Initialize proof aggregator
        
        Args:
            qezk: QE-ZK instance
        """
        self.qezk = qezk
        self.composer = ProofComposer(qezk)
    
    def aggregate_proofs(self, 
                        proofs: List[QEZKProof],
                        statement: str = "Aggregated proof",
                        verify_all: bool = True,
                        seed: Optional[int] = None) -> Tuple[QEZKProof, Dict[str, Any]]:
        """
        Aggregate multiple proofs with verification
        
        Args:
            proofs: Proofs to aggregate
            statement: Statement for aggregated proof
            verify_all: Whether to verify all proofs
            seed: Optional random seed
            
        Returns:
            Tuple of (aggregated_proof, aggregation_metadata)
        """
        if not proofs:
            raise ProtocolError("Cannot aggregate empty proof list")
        
        # Verify all proofs if requested
        if verify_all:
            valid_count = sum(1 for p in proofs if p.is_valid)
            if valid_count != len(proofs):
                raise VerificationError(
                    f"Not all proofs are valid: {valid_count}/{len(proofs)}"
                )
        
        # Aggregate
        aggregated_proof = self.composer.compose_proofs(proofs, statement, seed)
        
        metadata = {
            'num_proofs': len(proofs),
            'all_valid': all(p.is_valid for p in proofs),
            'valid_count': sum(1 for p in proofs if p.is_valid),
            'avg_chsh': np.mean([p.chsh_value for p in proofs]),
            'aggregated_chsh': aggregated_proof.chsh_value,
            'aggregated_valid': aggregated_proof.is_valid
        }
        
        return aggregated_proof, metadata
    
    def batch_aggregate(self, 
                       proof_batches: List[List[QEZKProof]],
                       statements: Optional[List[str]] = None,
                       verify_all: bool = False,
                       seed: Optional[int] = None) -> List[QEZKProof]:
        """
        Aggregate multiple batches of proofs
        
        Args:
            proof_batches: List of proof batches
            statements: Optional statements for each batch
            seed: Optional random seed
            
        Returns:
            List of aggregated proofs
        """
        aggregated = []
        
        for i, batch in enumerate(proof_batches):
            statement = statements[i] if statements and i < len(statements) else f"Batch {i+1}"
            aggregated_proof, _ = self.aggregate_proofs(batch, statement, verify_all=verify_all, seed=seed)
            aggregated.append(aggregated_proof)
        
        return aggregated


class RecursiveQEZK:
    """
    QE-ZK with recursive proof support
    
    Extends QE-ZK with recursive proof capabilities.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK):
        """
        Initialize recursive QE-ZK
        
        Args:
            qezk: Base QE-ZK instance
        """
        self.qezk = qezk
        self.recursive_prover = RecursiveProver(qezk)
        self.composer = ProofComposer(qezk)
        self.nested_builder = NestedProofBuilder(qezk)
        self.aggregator = ProofAggregator(qezk)
    
    def prove_recursively(self,
                         statement: str,
                         witness: str,
                         depth: int = 2,
                         seed: Optional[int] = None) -> RecursiveProof:
        """
        Generate recursive proof
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information)
            depth: Recursion depth
            seed: Optional random seed
            
        Returns:
            RecursiveProof with nested structure
        """
        return self.nested_builder.build_nested_proof(statement, witness, depth, seed)
    
    def prove_proof_of_proof(self,
                            inner_proof: QEZKProof,
                            seed: Optional[int] = None) -> QEZKProof:
        """
        Generate proof of proof
        
        Args:
            inner_proof: Proof to verify
            seed: Optional random seed
            
        Returns:
            Proof that verifies inner proof
        """
        return self.recursive_prover.prove_proof(inner_proof, seed=seed)
    
    def compose_multiple_proofs(self,
                               proofs: List[QEZKProof],
                               statement: str = "Composite proof",
                               seed: Optional[int] = None) -> QEZKProof:
        """
        Compose multiple proofs
        
        Args:
            proofs: Proofs to compose
            statement: Statement for composite proof
            seed: Optional random seed
            
        Returns:
            Composite proof
        """
        return self.composer.compose_proofs(proofs, statement, seed)
    
    def aggregate_proofs(self,
                        proofs: List[QEZKProof],
                        statement: str = "Aggregated proof",
                        seed: Optional[int] = None) -> Tuple[QEZKProof, Dict[str, Any]]:
        """
        Aggregate proofs
        
        Args:
            proofs: Proofs to aggregate
            statement: Statement for aggregated proof
            seed: Optional random seed
            
        Returns:
            Tuple of (aggregated_proof, metadata)
        """
        return self.aggregator.aggregate_proofs(proofs, statement, seed=seed)

