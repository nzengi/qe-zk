"""
Quantum Network Integration Tests

Tests for quantum network infrastructure and protocols.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import time
from qezk import (
    QuantumEntanglementZK, NodeType, ChannelState, QuantumNode, QuantumChannel,
    QuantumNetwork, QuantumNetworkProtocol, QuantumNetworkMonitor
)
from qezk.exceptions import ProtocolError, ConfigurationError


class TestQuantumNetwork(unittest.TestCase):
    """Test cases for quantum network"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.network = QuantumNetwork()
        self.prover_qezk = QuantumEntanglementZK(num_epr_pairs=100)
        self.verifier_qezk = QuantumEntanglementZK(num_epr_pairs=100)
    
    def test_add_node(self):
        """Test adding node to network"""
        node = QuantumNode(
            node_id="node1",
            node_type=NodeType.PROVER,
            qezk_instance=self.prover_qezk
        )
        
        self.network.add_node(node)
        
        self.assertIn("node1", self.network.topology.nodes)
        self.assertEqual(self.network.topology.nodes["node1"].node_id, "node1")
    
    def test_add_duplicate_node(self):
        """Test adding duplicate node"""
        node = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        self.network.add_node(node)
        
        with self.assertRaises(ConfigurationError):
            self.network.add_node(node)
    
    def test_remove_node(self):
        """Test removing node from network"""
        node = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        self.network.add_node(node)
        
        self.network.remove_node("node1")
        
        self.assertNotIn("node1", self.network.topology.nodes)
    
    def test_add_channel(self):
        """Test adding channel to network"""
        node1 = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        node2 = QuantumNode(node_id="node2", node_type=NodeType.VERIFIER)
        
        self.network.add_node(node1)
        self.network.add_node(node2)
        
        channel = QuantumChannel(
            channel_id="ch1",
            node_a="node1",
            node_b="node2"
        )
        
        self.network.add_channel(channel)
        
        self.assertIn("ch1", self.network.topology.channels)
    
    def test_find_path(self):
        """Test finding path between nodes"""
        # Create linear topology: node1 -> node2 -> node3
        for i in range(3):
            node = QuantumNode(node_id=f"node{i+1}", node_type=NodeType.PROVER)
            self.network.add_node(node)
        
        for i in range(2):
            channel = QuantumChannel(
                channel_id=f"ch{i+1}",
                node_a=f"node{i+1}",
                node_b=f"node{i+2}"
            )
            self.network.add_channel(channel)
        
        path = self.network.find_path("node1", "node3")
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "node1")
        self.assertEqual(path[-1], "node3")
    
    def test_distribute_epr_pairs(self):
        """Test EPR pair distribution"""
        prover_node = QuantumNode(
            node_id="prover1",
            node_type=NodeType.PROVER,
            qezk_instance=self.prover_qezk
        )
        verifier_node = QuantumNode(
            node_id="verifier1",
            node_type=NodeType.VERIFIER,
            qezk_instance=self.verifier_qezk
        )
        
        self.network.add_node(prover_node)
        self.network.add_node(verifier_node)
        
        channel = QuantumChannel(
            channel_id="ch1",
            node_a="prover1",
            node_b="verifier1"
        )
        self.network.add_channel(channel)
        
        source_pairs, dest_pairs = self.network.distribute_epr_pairs(
            "prover1", "verifier1", num_pairs=10
        )
        
        self.assertEqual(len(source_pairs), 10)
        self.assertEqual(len(dest_pairs), 10)
    
    def test_network_protocol(self):
        """Test network protocol execution"""
        prover_node = QuantumNode(
            node_id="prover1",
            node_type=NodeType.PROVER,
            qezk_instance=self.prover_qezk
        )
        verifier_node = QuantumNode(
            node_id="verifier1",
            node_type=NodeType.VERIFIER,
            qezk_instance=self.verifier_qezk
        )
        
        self.network.add_node(prover_node)
        self.network.add_node(verifier_node)
        
        channel = QuantumChannel(
            channel_id="ch1",
            node_a="prover1",
            node_b="verifier1"
        )
        self.network.add_channel(channel)
        
        protocol = QuantumNetworkProtocol(self.network)
        
        proof = protocol.execute_protocol(
            "prover1", "verifier1", "I know the secret", "11010110",
            num_epr_pairs=100, seed=42
        )
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.statement, "I know the secret")
    
    def test_network_monitor(self):
        """Test network monitoring"""
        node = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        self.network.add_node(node)
        
        monitor = QuantumNetworkMonitor(self.network)
        monitor.start_monitoring(interval=0.1)
        
        time.sleep(0.2)
        
        monitor.stop_monitoring()
        
        metrics = monitor.get_metrics()
        self.assertGreater(len(metrics), 0)
    
    def test_network_health(self):
        """Test network health monitoring"""
        node1 = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        node2 = QuantumNode(node_id="node2", node_type=NodeType.VERIFIER)
        
        self.network.add_node(node1)
        self.network.add_node(node2)
        
        channel = QuantumChannel(
            channel_id="ch1",
            node_a="node1",
            node_b="node2"
        )
        self.network.add_channel(channel)
        
        monitor = QuantumNetworkMonitor(self.network)
        health = monitor.get_network_health()
        
        self.assertIn('health_score', health)
        self.assertIn('num_nodes', health)
        self.assertGreaterEqual(health['health_score'], 0.0)
        self.assertLessEqual(health['health_score'], 1.0)
    
    def test_get_network_stats(self):
        """Test network statistics"""
        node = QuantumNode(node_id="node1", node_type=NodeType.PROVER)
        self.network.add_node(node)
        
        stats = self.network.get_network_stats()
        
        self.assertIn('num_nodes', stats)
        self.assertIn('num_channels', stats)
        self.assertEqual(stats['num_nodes'], 1)


if __name__ == '__main__':
    unittest.main()


