"""
Network Communication Example

Demonstrates advanced network communication features.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from qezk import (
    NetworkClient, NetworkServer, ConnectionConfig, ConnectionState
)


def example_secure_connection():
    """Example: Secure connection"""
    print("=" * 70)
    print("Example 1: Secure Connection")
    print("=" * 70)
    print()
    
    # Configure secure connection
    config = ConnectionConfig(
        host='localhost',
        port=8888,
        use_tls=False,  # Set to True for TLS
        timeout=30.0,
        retry_count=3,
        retry_delay=1.0,
        keepalive=True,
        keepalive_interval=30.0
    )
    
    client = NetworkClient(config)
    
    print("Connection configuration:")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  TLS: {config.use_tls}")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Retry count: {config.retry_count}")
    print()


def example_connection_with_retry():
    """Example: Connection with retry mechanism"""
    print("=" * 70)
    print("Example 2: Connection with Retry")
    print("=" * 70)
    print()
    
    config = ConnectionConfig(
        host='localhost',
        port=8888,
        retry_count=3,
        retry_delay=1.0
    )
    
    client = NetworkClient(config)
    
    print("Attempting connection with retry...")
    if client.connect():
        print("✓ Connected successfully")
    else:
        print("✗ Connection failed after retries")
    print()


def example_message_queue():
    """Example: Message queue for reliable delivery"""
    print("=" * 70)
    print("Example 3: Message Queue")
    print("=" * 70)
    print()
    
    from qezk import MessageQueue
    
    queue = MessageQueue(max_size=100)
    
    # Enqueue messages
    for i in range(5):
        message = {'id': i, 'data': f'message_{i}'}
        queue.enqueue(message)
        print(f"Enqueued: {message}")
    
    print(f"\nQueue size: {queue.size()}")
    print()
    
    # Dequeue messages
    print("Dequeuing messages:")
    while queue.size() > 0:
        message = queue.dequeue()
        print(f"  Dequeued: {message}")
    print()


def example_network_server():
    """Example: Network server"""
    print("=" * 70)
    print("Example 4: Network Server")
    print("=" * 70)
    print()
    
    def message_handler(message):
        """Handle incoming messages"""
        print(f"Received: {message}")
        return {'status': 'ok', 'echo': message}
    
    config = ConnectionConfig(
        host='localhost',
        port=8888
    )
    
    server = NetworkServer(config, message_handler)
    
    print("Starting server...")
    print("(Press Ctrl+C to stop)")
    print()
    
    # Start server in background thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    time.sleep(1)
    print("Server started")
    print()


def example_network_client():
    """Example: Network client"""
    print("=" * 70)
    print("Example 5: Network Client")
    print("=" * 70)
    print()
    
    config = ConnectionConfig(
        host='localhost',
        port=8888
    )
    
    client = NetworkClient(config)
    
    print("Connecting to server...")
    if client.connect():
        print("✓ Connected")
        
        # Send message
        message = {'type': 'test', 'data': 'hello'}
        print(f"Sending: {message}")
        client.send_message(message)
        
        # Receive response
        response = client.receive_message()
        print(f"Received: {response}")
        
        client.disconnect()
    else:
        print("✗ Connection failed")
    print()


def example_connection_manager():
    """Example: Connection manager with pooling"""
    print("=" * 70)
    print("Example 6: Connection Manager")
    print("=" * 70)
    print()
    
    from qezk import ConnectionManager
    
    config = ConnectionConfig(
        host='localhost',
        port=8888,
        retry_count=2
    )
    
    manager = ConnectionManager(config)
    
    print("Getting connection from pool...")
    conn = manager.get_connection()
    
    if conn:
        print(f"✓ Connection state: {conn.state.value}")
        print(f"  Connected: {conn.is_connected()}")
    else:
        print("✗ No connection available")
    
    manager.close_all()
    print()


def main():
    """Run all examples"""
    example_secure_connection()
    example_connection_with_retry()
    example_message_queue()
    example_network_server()
    example_network_client()
    example_connection_manager()
    
    print("=" * 70)
    print("Network Communication Examples Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()


