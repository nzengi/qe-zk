"""
Quantum Network Integration Example

Demonstrates quantum network infrastructure and QE-ZK protocol over network.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qezk import (
    QuantumEntanglementZK, NodeType, ChannelState, QuantumNode, QuantumChannel,
    QuantumNetwork, QuantumNetworkProtocol, QuantumNetworkMonitor
)


def example_basic_network():
    """Example: Basic quantum network"""
    print("=" * 70)
    print("Example 1: Basic Quantum Network")
    print("=" * 70)
    print()
    
    network = QuantumNetwork()
    
    # Create nodes
    prover_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    prover_node = QuantumNode(
        node_id="prover1",
        node_type=NodeType.PROVER,
        qezk_instance=prover_qezk,
        position=(0.0, 0.0)
    )
    
    verifier_node = QuantumNode(
        node_id="verifier1",
        node_type=NodeType.VERIFIER,
        qezk_instance=verifier_qezk,
        position=(1.0, 0.0)
    )
    
    # Add nodes to network
    network.add_node(prover_node)
    network.add_node(verifier_node)
    
    # Create channel
    channel = QuantumChannel(
        channel_id="ch1",
        node_a="prover1",
        node_b="verifier1",
        fidelity=0.95,
        latency=0.001
    )
    
    network.add_channel(channel)
    
    print("Network Created:")
    print(f"  Nodes: {len(network.topology.nodes)}")
    print(f"  Channels: {len(network.topology.channels)}")
    print()
    
    # Get network stats
    stats = network.get_network_stats()
    print("Network Statistics:")
    print(f"  Total nodes: {stats['num_nodes']}")
    print(f"  Total channels: {stats['num_channels']}")
    print(f"  Node types: {stats['node_types']}")
    print()


def example_network_topology():
    """Example: Network topology with multiple nodes"""
    print("=" * 70)
    print("Example 2: Network Topology")
    print("=" * 70)
    print()
    
    network = QuantumNetwork()
    
    # Create multiple nodes
    nodes = []
    for i in range(4):
        node_type = NodeType.PROVER if i < 2 else NodeType.VERIFIER
        qezk = QuantumEntanglementZK(num_epr_pairs=100)
        node = QuantumNode(
            node_id=f"node{i+1}",
            node_type=node_type,
            qezk_instance=qezk,
            position=(float(i), 0.0)
        )
        nodes.append(node)
        network.add_node(node)
    
    # Create channels (ring topology)
    for i in range(4):
        channel = QuantumChannel(
            channel_id=f"ch{i+1}",
            node_a=f"node{i+1}",
            node_b=f"node{(i+1)%4+1}",
            fidelity=0.9,
            latency=0.001
        )
        network.add_channel(channel)
    
    print("Ring Topology Created:")
    print(f"  Nodes: {len(network.topology.nodes)}")
    print(f"  Channels: {len(network.topology.channels)}")
    print()
    
    # Find paths
    path = network.find_path("node1", "node3")
    print(f"Path from node1 to node3: {path}")
    print()


def example_epr_distribution():
    """Example: EPR pair distribution over network"""
    print("=" * 70)
    print("Example 3: EPR Pair Distribution")
    print("=" * 70)
    print()
    
    network = QuantumNetwork()
    
    # Create nodes
    prover_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    prover_node = QuantumNode(
        node_id="prover1",
        node_type=NodeType.PROVER,
        qezk_instance=prover_qezk
    )
    
    verifier_node = QuantumNode(
        node_id="verifier1",
        node_type=NodeType.VERIFIER,
        qezk_instance=verifier_qezk
    )
    
    network.add_node(prover_node)
    network.add_node(verifier_node)
    
    # Create channel
    channel = QuantumChannel(
        channel_id="ch1",
        node_a="prover1",
        node_b="verifier1",
        fidelity=0.95
    )
    network.add_channel(channel)
    
    # Distribute EPR pairs
    source_pairs, dest_pairs = network.distribute_epr_pairs(
        "prover1", "verifier1", num_pairs=100, state_type='phi_plus'
    )
    
    print(f"Distributed {len(source_pairs)} EPR pairs")
    print(f"  Source node pairs: {len(network.epr_distribution['prover1'])}")
    print(f"  Destination node pairs: {len(network.epr_distribution['verifier1'])}")
    print()


def example_network_protocol():
    """Example: QE-ZK protocol over quantum network"""
    print("=" * 70)
    print("Example 4: QE-ZK Protocol Over Network")
    print("=" * 70)
    print()
    
    network = QuantumNetwork()
    
    # Create nodes
    prover_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    prover_node = QuantumNode(
        node_id="prover1",
        node_type=NodeType.PROVER,
        qezk_instance=prover_qezk
    )
    
    verifier_node = QuantumNode(
        node_id="verifier1",
        node_type=NodeType.VERIFIER,
        qezk_instance=verifier_qezk
    )
    
    network.add_node(prover_node)
    network.add_node(verifier_node)
    
    # Create channel
    channel = QuantumChannel(
        channel_id="ch1",
        node_a="prover1",
        node_b="verifier1",
        fidelity=0.95
    )
    network.add_channel(channel)
    
    # Execute protocol
    protocol = QuantumNetworkProtocol(network)
    
    statement = "I know the secret password"
    witness = "11010110"
    
    proof = protocol.execute_protocol(
        "prover1", "verifier1", statement, witness, num_epr_pairs=100, seed=42
    )
    
    print("Protocol Execution Result:")
    print(f"  Statement: {proof.statement}")
    print(f"  CHSH Value: {proof.chsh_value:.4f}")
    print(f"  Is Valid: {proof.is_valid}")
    print()


def example_network_monitor():
    """Example: Network monitoring"""
    print("=" * 70)
    print("Example 5: Network Monitoring")
    print("=" * 70)
    print()
    
    network = QuantumNetwork()
    
    # Create nodes
    prover_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    verifier_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    prover_node = QuantumNode(
        node_id="prover1",
        node_type=NodeType.PROVER,
        qezk_instance=prover_qezk
    )
    
    verifier_node = QuantumNode(
        node_id="verifier1",
        node_type=NodeType.VERIFIER,
        qezk_instance=verifier_qezk
    )
    
    network.add_node(prover_node)
    network.add_node(verifier_node)
    
    # Create channel
    channel = QuantumChannel(
        channel_id="ch1",
        node_a="prover1",
        node_b="verifier1",
        fidelity=0.95
    )
    network.add_channel(channel)
    
    # Monitor network
    monitor = QuantumNetworkMonitor(network)
    monitor.start_monitoring(interval=0.1)
    
    import time
    time.sleep(0.3)  # Collect some metrics
    
    monitor.stop_monitoring()
    
    # Get metrics
    metrics = monitor.get_metrics()
    print(f"Collected {len(metrics)} metrics")
    print()
    
    # Get network health
    health = monitor.get_network_health()
    print("Network Health:")
    print(f"  Health score: {health['health_score']:.2%}")
    print(f"  Online channels: {health['online_channels']}")
    print(f"  Total EPR pairs: {health['total_epr_pairs']}")
    print()


def main():
    """Run all examples"""
    example_basic_network()
    example_network_topology()
    example_epr_distribution()
    example_network_protocol()
    example_network_monitor()
    
    print("=" * 70)
    print("Quantum Network Integration Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


