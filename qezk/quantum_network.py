"""
Quantum Network Integration

Quantum network infrastructure for QE-ZK protocol.
Includes quantum nodes, channels, routing, and EPR distribution.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from collections import defaultdict

from .protocol import QuantumEntanglementZK, QEZKProof
from .entanglement import EntanglementSource
from .exceptions import ProtocolError, EntanglementError, ConfigurationError


class NodeType(Enum):
    """Quantum network node types"""
    PROVER = "prover"
    VERIFIER = "verifier"
    REPEATER = "repeater"
    SWITCH = "switch"
    HUB = "hub"


class ChannelState(Enum):
    """Quantum channel states"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class QuantumNode:
    """Quantum network node"""
    node_id: str
    node_type: NodeType
    qezk_instance: Optional[QuantumEntanglementZK] = None
    position: Tuple[float, float] = (0.0, 0.0)  # (x, y) coordinates
    neighbors: List[str] = field(default_factory=list)
    channels: Dict[str, 'QuantumChannel'] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantumChannel:
    """Quantum channel between nodes"""
    channel_id: str
    node_a: str
    node_b: str
    state: ChannelState = ChannelState.IDLE
    fidelity: float = 1.0
    capacity: int = 1000  # Max EPR pairs per second
    latency: float = 0.0  # Latency in seconds
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkTopology:
    """Quantum network topology"""
    nodes: Dict[str, QuantumNode] = field(default_factory=dict)
    channels: Dict[str, QuantumChannel] = field(default_factory=dict)
    routing_table: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)


class QuantumNetwork:
    """
    Quantum network infrastructure
    
    Manages quantum nodes, channels, and routing for QE-ZK protocol.
    """
    
    def __init__(self):
        """Initialize quantum network"""
        self.topology = NetworkTopology()
        self.epr_distribution: Dict[str, List[np.ndarray]] = {}  # node_id -> EPR pairs
        self.lock = threading.Lock()
    
    def add_node(self, node: QuantumNode):
        """
        Add node to network
        
        Args:
            node: Quantum node to add
        """
        with self.lock:
            if node.node_id in self.topology.nodes:
                raise ConfigurationError(f"Node {node.node_id} already exists")
            
            self.topology.nodes[node.node_id] = node
            self.epr_distribution[node.node_id] = []
            self._update_routing_table()
    
    def remove_node(self, node_id: str):
        """
        Remove node from network
        
        Args:
            node_id: Node ID to remove
        """
        with self.lock:
            if node_id not in self.topology.nodes:
                raise ConfigurationError(f"Node {node_id} not found")
            
            # Remove channels connected to this node
            channels_to_remove = [
                ch_id for ch_id, ch in self.topology.channels.items()
                if ch.node_a == node_id or ch.node_b == node_id
            ]
            for ch_id in channels_to_remove:
                del self.topology.channels[ch_id]
            
            # Remove from neighbors
            for node in self.topology.nodes.values():
                if node_id in node.neighbors:
                    node.neighbors.remove(node_id)
            
            del self.topology.nodes[node_id]
            if node_id in self.epr_distribution:
                del self.epr_distribution[node_id]
            
            self._update_routing_table()
    
    def add_channel(self, channel: QuantumChannel):
        """
        Add channel to network
        
        Args:
            channel: Quantum channel to add
        """
        with self.lock:
            if channel.channel_id in self.topology.channels:
                raise ConfigurationError(f"Channel {channel.channel_id} already exists")
            
            # Validate nodes exist
            if channel.node_a not in self.topology.nodes:
                raise ConfigurationError(f"Node {channel.node_a} not found")
            if channel.node_b not in self.topology.nodes:
                raise ConfigurationError(f"Node {channel.node_b} not found")
            
            self.topology.channels[channel.channel_id] = channel
            
            # Update node neighbors
            self.topology.nodes[channel.node_a].neighbors.append(channel.node_b)
            self.topology.nodes[channel.node_b].neighbors.append(channel.node_a)
            
            # Update node channels
            self.topology.nodes[channel.node_a].channels[channel.channel_id] = channel
            self.topology.nodes[channel.node_b].channels[channel.channel_id] = channel
            
            self._update_routing_table()
    
    def _update_routing_table(self):
        """Update routing table using shortest path algorithm"""
        # Simple shortest path (BFS)
        routing_table = {}
        
        for source_id in self.topology.nodes:
            routing_table[source_id] = {}
            
            # BFS from source
            queue = [(source_id, [source_id])]
            visited = {source_id}
            
            while queue:
                current, path = queue.pop(0)
                
                for neighbor in self.topology.nodes[current].neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        routing_table[source_id][neighbor] = new_path
                        queue.append((neighbor, new_path))
        
        self.topology.routing_table = routing_table
    
    def find_path(self, source: str, destination: str) -> Optional[List[str]]:
        """
        Find path between nodes
        
        Args:
            source: Source node ID
            destination: Destination node ID
            
        Returns:
            Path as list of node IDs, or None if no path exists
        """
        if source not in self.topology.routing_table:
            return None
        
        return self.topology.routing_table[source].get(destination)
    
    def distribute_epr_pairs(self,
                            source: str,
                            destination: str,
                            num_pairs: int,
                            state_type: str = 'phi_plus') -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Distribute EPR pairs over network
        
        Args:
            source: Source node ID
            destination: Destination node ID
            num_pairs: Number of EPR pairs to distribute
            state_type: Bell state type
            
        Returns:
            Tuple of (source_pairs, destination_pairs)
        """
        if source not in self.topology.nodes:
            raise ConfigurationError(f"Source node {source} not found")
        if destination not in self.topology.nodes:
            raise ConfigurationError(f"Destination node {destination} not found")
        
        source_node = self.topology.nodes[source]
        if source_node.qezk_instance is None:
            raise ProtocolError(f"Source node {source} has no QE-ZK instance")
        
        # Find path
        path = self.find_path(source, destination)
        if path is None:
            raise ProtocolError(f"No path from {source} to {destination}")
        
        # Generate EPR pairs at source
        entanglement = EntanglementSource(source_node.qezk_instance.quantum_prep)
        epr_pairs = entanglement.generate_epr_pairs(num_pairs, state_type)
        
        # Distribute along path (simplified - in real network, would use quantum repeaters)
        # For now, simulate direct distribution
        source_pairs = epr_pairs
        destination_pairs = epr_pairs  # In simulation, same reference
        
        # Store at nodes
        with self.lock:
            self.epr_distribution[source].extend(source_pairs)
            self.epr_distribution[destination].extend(destination_pairs)
        
        return source_pairs, destination_pairs
    
    def get_node(self, node_id: str) -> Optional[QuantumNode]:
        """Get node by ID"""
        return self.topology.nodes.get(node_id)
    
    def get_channel(self, channel_id: str) -> Optional[QuantumChannel]:
        """Get channel by ID"""
        return self.topology.channels.get(channel_id)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            'num_nodes': len(self.topology.nodes),
            'num_channels': len(self.topology.channels),
            'node_types': {
                node_type.value: sum(1 for n in self.topology.nodes.values() 
                                   if n.node_type == node_type)
                for node_type in NodeType
            },
            'total_epr_pairs': sum(len(pairs) for pairs in self.epr_distribution.values())
        }


class QuantumNetworkProtocol:
    """
    QE-ZK protocol over quantum network
    
    Executes QE-ZK protocol using quantum network infrastructure.
    """
    
    def __init__(self, network: QuantumNetwork):
        """
        Initialize quantum network protocol
        
        Args:
            network: Quantum network instance
        """
        self.network = network
    
    def execute_protocol(self,
                        prover_id: str,
                        verifier_id: str,
                        statement: str,
                        witness: str,
                        num_epr_pairs: int = 10000,
                        seed: Optional[int] = None) -> QEZKProof:
        """
        Execute QE-ZK protocol over quantum network
        
        Args:
            prover_id: Prover node ID
            verifier_id: Verifier node ID
            statement: Statement to prove
            witness: Witness (secret information)
            num_epr_pairs: Number of EPR pairs
            seed: Optional random seed
            
        Returns:
            QEZKProof
        """
        prover_node = self.network.get_node(prover_id)
        verifier_node = self.network.get_node(verifier_id)
        
        if prover_node is None:
            raise ConfigurationError(f"Prover node {prover_id} not found")
        if verifier_node is None:
            raise ConfigurationError(f"Verifier node {verifier_id} not found")
        
        if prover_node.qezk_instance is None:
            raise ProtocolError(f"Prover node {prover_id} has no QE-ZK instance")
        if verifier_node.qezk_instance is None:
            raise ProtocolError(f"Verifier node {verifier_id} has no QE-ZK instance")
        
        # Distribute EPR pairs over network
        prover_particles, verifier_particles = self.network.distribute_epr_pairs(
            prover_id, verifier_id, num_epr_pairs, 'phi_plus'
        )
        
        # Execute protocol using prover's QE-ZK instance
        qezk = prover_node.qezk_instance
        
        # Prover phase
        prover_results, measurement_bases = qezk.prover_phase(
            statement, witness, prover_particles
        )
        
        # Verifier phase (using verifier's instance)
        verifier_results = verifier_node.qezk_instance.verifier_phase(
            statement, verifier_particles, measurement_bases
        )
        
        # Verification
        is_valid, chsh_value = qezk.verify(
            prover_results, verifier_results, measurement_bases
        )
        
        return QEZKProof(
            prover_results=prover_results,
            verifier_results=verifier_results,
            measurement_bases=measurement_bases,
            chsh_value=chsh_value,
            is_valid=is_valid,
            statement=statement
        )
    
    def execute_multi_hop_protocol(self,
                                   prover_id: str,
                                   verifier_id: str,
                                   statement: str,
                                   witness: str,
                                   num_epr_pairs: int = 10000,
                                   seed: Optional[int] = None) -> QEZKProof:
        """
        Execute protocol with multi-hop EPR distribution
        
        Args:
            prover_id: Prover node ID
            verifier_id: Verifier node ID
            statement: Statement to prove
            witness: Witness (secret information)
            num_epr_pairs: Number of EPR pairs
            seed: Optional random seed
            
        Returns:
            QEZKProof
        """
        # Find path
        path = self.network.find_path(prover_id, verifier_id)
        if path is None:
            raise ProtocolError(f"No path from {prover_id} to {verifier_id}")
        
        if len(path) < 2:
            raise ProtocolError("Path must have at least 2 nodes")
        
        # Distribute EPR pairs through path (using quantum repeaters)
        # For now, use direct distribution (repeater logic would go here)
        prover_particles, verifier_particles = self.network.distribute_epr_pairs(
            prover_id, verifier_id, num_epr_pairs, 'phi_plus'
        )
        
        # Execute protocol
        prover_node = self.network.get_node(prover_id)
        verifier_node = self.network.get_node(verifier_id)
        
        qezk = prover_node.qezk_instance
        
        prover_results, measurement_bases = qezk.prover_phase(
            statement, witness, prover_particles
        )
        
        verifier_results = verifier_node.qezk_instance.verifier_phase(
            statement, verifier_particles, measurement_bases
        )
        
        is_valid, chsh_value = qezk.verify(
            prover_results, verifier_results, measurement_bases
        )
        
        return QEZKProof(
            prover_results=prover_results,
            verifier_results=verifier_results,
            measurement_bases=measurement_bases,
            chsh_value=chsh_value,
            is_valid=is_valid,
            statement=statement
        )


class QuantumNetworkMonitor:
    """
    Quantum network monitor
    
    Monitors network state, performance, and health.
    """
    
    def __init__(self, network: QuantumNetwork):
        """
        Initialize network monitor
        
        Args:
            network: Quantum network to monitor
        """
        self.network = network
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics: List[Dict[str, Any]] = []
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start network monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                metrics = self._collect_metrics()
                self.metrics.append(metrics)
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect network metrics"""
        stats = self.network.get_network_stats()
        
        # Channel states
        channel_states = defaultdict(int)
        for channel in self.network.topology.channels.values():
            channel_states[channel.state.value] += 1
        
        return {
            'timestamp': time.time(),
            'stats': stats,
            'channel_states': dict(channel_states),
            'num_epr_pairs': sum(len(pairs) for pairs in self.network.epr_distribution.values())
        }
    
    def get_metrics(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get collected metrics
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of metrics
        """
        if limit:
            return self.metrics[-limit:]
        return self.metrics
    
    def get_network_health(self) -> Dict[str, Any]:
        """Get network health status"""
        stats = self.network.get_network_stats()
        
        # Calculate health score
        total_channels = stats['num_channels']
        if total_channels == 0:
            health_score = 0.0
        else:
            online_channels = sum(
                1 for ch in self.network.topology.channels.values()
                if ch.state != ChannelState.OFFLINE
            )
            health_score = online_channels / total_channels
        
        return {
            'health_score': health_score,
            'num_nodes': stats['num_nodes'],
            'num_channels': stats['num_channels'],
            'online_channels': sum(
                1 for ch in self.network.topology.channels.values()
                if ch.state != ChannelState.OFFLINE
            ),
            'total_epr_pairs': stats['total_epr_pairs']
        }


