"""
Multi-Party QE-ZK Protocol

Support for multiple provers and verifiers in QE-ZK protocol.
Includes threshold verification, group protocols, and consensus mechanisms.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import time

from .protocol import QuantumEntanglementZK, QEZKProof
from .exceptions import ProtocolError, ConfigurationError


class PartyRole(Enum):
    """Party role in multi-party protocol"""
    PROVER = "prover"
    VERIFIER = "verifier"
    COORDINATOR = "coordinator"
    OBSERVER = "observer"


@dataclass
class Party:
    """Party in multi-party protocol"""
    party_id: str
    role: PartyRole
    qezk: QuantumEntanglementZK
    address: Optional[str] = None
    port: Optional[int] = None
    weight: float = 1.0  # Voting weight for consensus


@dataclass
class MultiPartyProof:
    """Multi-party proof result"""
    proof: QEZKProof
    party_id: str
    timestamp: float
    is_valid: bool


class ThresholdVerifier:
    """
    Threshold verifier for multi-party verification
    
    Requires threshold number of verifiers to agree for proof acceptance.
    """
    
    def __init__(self, threshold: int, verifiers: List[Party]):
        """
        Initialize threshold verifier
        
        Args:
            threshold: Minimum number of verifiers needed
            verifiers: List of verifier parties
        """
        if threshold < 1 or threshold > len(verifiers):
            raise ConfigurationError(
                f"Threshold must be between 1 and {len(verifiers)}, got {threshold}"
            )
        
        self.threshold = threshold
        self.verifiers = verifiers
        self.verification_results: Dict[str, bool] = {}
    
    def verify(self, statement: str, witness: str, seed: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify statement with threshold consensus
        
        Args:
            statement: Statement to verify
            witness: Witness (secret information)
            seed: Optional random seed
            
        Returns:
            Tuple of (is_valid, verification_details)
        """
        verification_results = {}
        valid_count = 0
        
        # Each verifier verifies independently
        for verifier in self.verifiers:
            try:
                proof = verifier.qezk.prove(statement, witness, seed)
                is_valid = proof.is_valid
                verification_results[verifier.party_id] = {
                    'is_valid': is_valid,
                    'chsh_value': proof.chsh_value,
                    'proof': proof
                }
                
                if is_valid:
                    valid_count += 1
                    
            except Exception as e:
                verification_results[verifier.party_id] = {
                    'is_valid': False,
                    'error': str(e)
                }
        
        # Threshold consensus
        is_consensus = valid_count >= self.threshold
        
        return is_consensus, {
            'valid_count': valid_count,
            'threshold': self.threshold,
            'total_verifiers': len(self.verifiers),
            'verification_results': verification_results,
            'consensus': is_consensus
        }


class MultiProverProtocol:
    """
    Multi-prover protocol
    
    Multiple provers can collaborate to prove a statement.
    """
    
    def __init__(self, provers: List[Party], coordinator: Optional[Party] = None):
        """
        Initialize multi-prover protocol
        
        Args:
            provers: List of prover parties
            coordinator: Optional coordinator party
        """
        if len(provers) < 1:
            raise ConfigurationError("At least one prover required")
        
        self.provers = provers
        self.coordinator = coordinator
        self.proofs: Dict[str, QEZKProof] = {}
    
    def prove(self, statement: str, witness: str, seed: Optional[int] = None) -> Dict[str, QEZKProof]:
        """
        Generate proofs from all provers
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information)
            seed: Optional random seed
            
        Returns:
            Dictionary mapping party_id to proof
        """
        proofs = {}
        
        for prover in self.provers:
            try:
                proof = prover.qezk.prove(statement, witness, seed)
                proofs[prover.party_id] = proof
            except Exception as e:
                raise ProtocolError(f"Prover {prover.party_id} failed: {str(e)}") from e
        
        self.proofs = proofs
        return proofs
    
    def aggregate_proofs(self, proofs: Dict[str, QEZKProof]) -> Dict[str, Any]:
        """
        Aggregate proofs from multiple provers
        
        Args:
            proofs: Dictionary of proofs from provers
            
        Returns:
            Aggregated proof statistics
        """
        if not proofs:
            return {}
        
        chsh_values = [p.chsh_value for p in proofs.values()]
        valid_count = sum(1 for p in proofs.values() if p.is_valid)
        
        return {
            'num_provers': len(proofs),
            'valid_count': valid_count,
            'valid_rate': valid_count / len(proofs) if proofs else 0,
            'avg_chsh': np.mean(chsh_values) if chsh_values else 0,
            'min_chsh': np.min(chsh_values) if chsh_values else 0,
            'max_chsh': np.max(chsh_values) if chsh_values else 0,
            'std_chsh': np.std(chsh_values) if chsh_values else 0
        }


class ConsensusProtocol:
    """
    Consensus protocol for multi-party verification
    
    Uses voting mechanism to reach consensus on proof validity.
    """
    
    def __init__(self, parties: List[Party], voting_threshold: float = 0.5):
        """
        Initialize consensus protocol
        
        Args:
            parties: List of parties participating in consensus
            voting_threshold: Minimum vote percentage needed (0-1)
        """
        if not 0 <= voting_threshold <= 1:
            raise ConfigurationError(f"Voting threshold must be between 0 and 1, got {voting_threshold}")
        
        self.parties = parties
        self.voting_threshold = voting_threshold
        self.votes: Dict[str, bool] = {}
    
    def vote(self, party_id: str, is_valid: bool) -> bool:
        """
        Record vote from party
        
        Args:
            party_id: ID of voting party
            is_valid: Vote (True = valid, False = invalid)
            
        Returns:
            True if consensus reached
        """
        self.votes[party_id] = is_valid
        return self.has_consensus()
    
    def has_consensus(self) -> bool:
        """
        Check if consensus has been reached
        
        Returns:
            True if consensus reached
        """
        if not self.votes:
            return False
        
        total_weight = sum(p.weight for p in self.parties)
        valid_weight = sum(
            p.weight for p in self.parties 
            if self.votes.get(p.party_id, False)
        )
        
        return (valid_weight / total_weight) >= self.voting_threshold
    
    def get_consensus_result(self) -> Optional[bool]:
        """
        Get consensus result
        
        Returns:
            True if consensus is valid, False if invalid, None if no consensus
        """
        if not self.has_consensus():
            return None
        
        # Return majority vote
        valid_votes = sum(1 for v in self.votes.values() if v)
        return valid_votes > len(self.votes) / 2
    
    def reset(self):
        """Reset votes"""
        self.votes.clear()


class GroupProtocol:
    """
    Group protocol for multiple parties
    
    Coordinates protocol execution among multiple parties.
    """
    
    def __init__(self, parties: List[Party], coordinator: Optional[Party] = None):
        """
        Initialize group protocol
        
        Args:
            parties: List of parties
            coordinator: Optional coordinator party
        """
        self.parties = parties
        self.coordinator = coordinator or parties[0] if parties else None
        self.proofs: Dict[str, QEZKProof] = {}
        self.consensus = ConsensusProtocol(parties)
    
    def execute_group_protocol(self, 
                              statement: str, 
                              witness: str,
                              seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute protocol with group of parties
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information)
            seed: Optional random seed
            
        Returns:
            Group protocol results
        """
        # Separate provers and verifiers
        provers = [p for p in self.parties if p.role == PartyRole.PROVER]
        verifiers = [p for p in self.parties if p.role == PartyRole.VERIFIER]
        
        if not provers:
            raise ProtocolError("No provers in group")
        if not verifiers:
            raise ProtocolError("No verifiers in group")
        
        # Provers generate proofs
        prover_protocol = MultiProverProtocol(provers)
        proofs = prover_protocol.prove(statement, witness, seed)
        
        # Verifiers verify
        verification_results = {}
        for verifier in verifiers:
            try:
                proof = verifier.qezk.prove(statement, witness, seed)
                verification_results[verifier.party_id] = {
                    'is_valid': proof.is_valid,
                    'chsh_value': proof.chsh_value
                }
                
                # Record vote
                self.consensus.vote(verifier.party_id, proof.is_valid)
                
            except Exception as e:
                verification_results[verifier.party_id] = {
                    'is_valid': False,
                    'error': str(e)
                }
                self.consensus.vote(verifier.party_id, False)
        
        # Check consensus
        consensus_result = self.consensus.get_consensus_result()
        
        return {
            'prover_proofs': {pid: {'chsh_value': p.chsh_value, 'is_valid': p.is_valid} 
                             for pid, p in proofs.items()},
            'verification_results': verification_results,
            'consensus': consensus_result,
            'consensus_reached': self.consensus.has_consensus(),
            'statement': statement
        }


class MultiPartyQEZK:
    """
    Multi-party QE-ZK system
    
    Coordinates QE-ZK protocol execution with multiple parties.
    """
    
    def __init__(self, parties: List[Party], threshold: Optional[int] = None):
        """
        Initialize multi-party QE-ZK
        
        Args:
            parties: List of parties
            threshold: Optional threshold for verification (default: majority)
        """
        if not parties:
            raise ConfigurationError("At least one party required")
        
        self.parties = parties
        self.provers = [p for p in parties if p.role == PartyRole.PROVER]
        self.verifiers = [p for p in parties if p.role == PartyRole.VERIFIER]
        
        # Set threshold to majority if not specified
        if threshold is None:
            threshold = (len(self.verifiers) // 2) + 1 if self.verifiers else 1
        
        self.threshold_verifier = ThresholdVerifier(threshold, self.verifiers) if self.verifiers else None
        self.group_protocol = GroupProtocol(parties)
    
    def prove_with_multi_party(self,
                               statement: str,
                               witness: str,
                               seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute multi-party proof generation
        
        Args:
            statement: Statement to prove
            witness: Witness (secret information)
            seed: Optional random seed
            
        Returns:
            Multi-party proof results
        """
        if not self.provers:
            raise ProtocolError("No provers available")
        
        # Execute group protocol
        results = self.group_protocol.execute_group_protocol(statement, witness, seed)
        
        # Add threshold verification if available
        if self.threshold_verifier:
            threshold_result, threshold_details = self.threshold_verifier.verify(statement, witness, seed)
            results['threshold_verification'] = threshold_result
            results['threshold_details'] = threshold_details
        
        return results
    
    def verify_with_consensus(self,
                             statement: str,
                             witness: str,
                             seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Verify with consensus mechanism
        
        Args:
            statement: Statement to verify
            witness: Witness (secret information)
            seed: Optional random seed
            
        Returns:
            Consensus verification results
        """
        if not self.verifiers:
            raise ProtocolError("No verifiers available")
        
        # Each verifier verifies
        verification_results = {}
        for verifier in self.verifiers:
            try:
                proof = verifier.qezk.prove(statement, witness, seed)
                verification_results[verifier.party_id] = {
                    'is_valid': proof.is_valid,
                    'chsh_value': proof.chsh_value
                }
                
                # Vote
                self.group_protocol.consensus.vote(verifier.party_id, proof.is_valid)
                
            except Exception as e:
                verification_results[verifier.party_id] = {
                    'is_valid': False,
                    'error': str(e)
                }
                self.group_protocol.consensus.vote(verifier.party_id, False)
        
        consensus_result = self.group_protocol.consensus.get_consensus_result()
        
        return {
            'verification_results': verification_results,
            'consensus': consensus_result,
            'consensus_reached': self.group_protocol.consensus.has_consensus(),
            'num_verifiers': len(self.verifiers),
            'threshold': self.threshold_verifier.threshold if self.threshold_verifier else None
        }
