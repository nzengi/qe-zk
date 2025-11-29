"""
Network Communication Tests

Tests for advanced network communication features.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import threading
import time
from qezk import (
    SecureConnection, ConnectionManager, MessageQueue,
    NetworkClient, NetworkServer, ConnectionConfig, ConnectionState
)


class TestNetworkCommunication(unittest.TestCase):
    """Test cases for network communication"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ConnectionConfig(
            host='localhost',
            port=9999,
            timeout=5.0,
            retry_count=2
        )
    
    def test_connection_config(self):
        """Test connection configuration"""
        config = ConnectionConfig(
            host='localhost',
            port=8888,
            use_tls=True,
            timeout=30.0
        )
        
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 8888)
        self.assertTrue(config.use_tls)
        self.assertEqual(config.timeout, 30.0)
    
    def test_message_queue(self):
        """Test message queue"""
        queue = MessageQueue(max_size=10)
        
        # Enqueue messages
        for i in range(5):
            message = {'id': i}
            self.assertTrue(queue.enqueue(message))
        
        self.assertEqual(queue.size(), 5)
        
        # Dequeue messages
        for i in range(5):
            message = queue.dequeue()
            self.assertIsNotNone(message)
            self.assertEqual(message['id'], i)
        
        self.assertEqual(queue.size(), 0)
    
    def test_message_queue_overflow(self):
        """Test message queue overflow protection"""
        queue = MessageQueue(max_size=3)
        
        # Fill queue
        for i in range(3):
            self.assertTrue(queue.enqueue({'id': i}))
        
        # Try to overflow
        self.assertFalse(queue.enqueue({'id': 4}))
    
    def test_connection_state(self):
        """Test connection state enum"""
        states = [
            ConnectionState.DISCONNECTED,
            ConnectionState.CONNECTING,
            ConnectionState.CONNECTED,
            ConnectionState.AUTHENTICATED
        ]
        
        for state in states:
            self.assertIsInstance(state, ConnectionState)
    
    def test_secure_connection_creation(self):
        """Test secure connection creation"""
        conn = SecureConnection(self.config)
        self.assertIsNotNone(conn)
        self.assertEqual(conn.state, ConnectionState.DISCONNECTED)
    
    def test_connection_manager(self):
        """Test connection manager"""
        manager = ConnectionManager(self.config)
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.connections), 0)
    
    def test_network_client_creation(self):
        """Test network client creation"""
        client = NetworkClient(self.config)
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.connection_manager)
        self.assertIsNotNone(client.message_queue)
    
    def test_network_server_creation(self):
        """Test network server creation"""
        def handler(msg):
            return {'status': 'ok'}
        
        server = NetworkServer(self.config, handler)
        self.assertIsNotNone(server)
        self.assertFalse(server.running)
    
    def test_message_queue_clear(self):
        """Test message queue clear"""
        queue = MessageQueue()
        
        for i in range(5):
            queue.enqueue({'id': i})
        
        self.assertEqual(queue.size(), 5)
        queue.clear()
        self.assertEqual(queue.size(), 0)
    
    def test_connection_manager_close_all(self):
        """Test connection manager close all"""
        manager = ConnectionManager(self.config)
        
        # Try to get connection (will fail but tests the method)
        conn = manager.get_connection()
        
        manager.close_all()
        self.assertEqual(len(manager.connections), 0)


if __name__ == '__main__':
    unittest.main()


