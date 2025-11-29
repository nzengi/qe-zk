"""
Advanced Network Communication

Enhanced network communication layer with encryption, authentication,
retry mechanisms, and connection management.
"""

import socket
import ssl
import time
import threading
import hashlib
import hmac
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
import json
from .exceptions import ProtocolError, SecurityError


class ConnectionState(Enum):
    """Connection state"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    ERROR = "error"


@dataclass
class ConnectionConfig:
    """Network connection configuration"""
    host: str
    port: int
    use_tls: bool = False
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    keepalive: bool = True
    keepalive_interval: float = 30.0
    buffer_size: int = 8192
    authentication_required: bool = False
    auth_token: Optional[str] = None


class SecureConnection:
    """
    Secure network connection with TLS and authentication
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize secure connection
        
        Args:
            config: Connection configuration
        """
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.ssl_context: Optional[ssl.SSLContext] = None
        self.state = ConnectionState.DISCONNECTED
        self.last_heartbeat = time.time()
        self.keepalive_thread: Optional[threading.Thread] = None
        self.running = False
    
    def connect(self) -> bool:
        """
        Establish secure connection
        
        Returns:
            True if connection successful
        """
        try:
            self.state = ConnectionState.CONNECTING
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.timeout)
            
            # Connect
            self.socket.connect((self.config.host, self.config.port))
            
            # Wrap with TLS if enabled
            if self.config.use_tls:
                self.ssl_context = ssl.create_default_context()
                if self.config.tls_cert_file:
                    self.ssl_context.load_cert_chain(
                        self.config.tls_cert_file,
                        self.config.tls_key_file
                    )
                self.socket = self.ssl_context.wrap_socket(self.socket)
            
            self.state = ConnectionState.CONNECTED
            
            # Authenticate if required
            if self.config.authentication_required:
                if not self._authenticate():
                    self.disconnect()
                    return False
            
            # Start keepalive if enabled
            if self.config.keepalive:
                self._start_keepalive()
            
            return True
            
        except Exception as e:
            self.state = ConnectionState.ERROR
            print(f"Connection error: {e}")
            return False
    
    def _authenticate(self) -> bool:
        """Authenticate connection"""
        try:
            self.state = ConnectionState.AUTHENTICATING
            
            if not self.config.auth_token:
                return False
            
            # Send authentication token
            auth_message = {
                'type': 'auth',
                'token': self.config.auth_token,
                'timestamp': time.time()
            }
            
            self.send_json(auth_message)
            
            # Receive authentication response
            response = self.receive_json()
            
            if response and response.get('status') == 'authenticated':
                self.state = ConnectionState.AUTHENTICATED
                return True
            
            return False
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def send(self, data: bytes) -> bool:
        """
        Send data over connection
        
        Args:
            data: Data to send
            
        Returns:
            True if successful
        """
        try:
            if self.socket and self.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED]:
                self.socket.sendall(data)
                return True
        except Exception as e:
            print(f"Send error: {e}")
            self.state = ConnectionState.ERROR
        return False
    
    def receive(self, size: Optional[int] = None) -> Optional[bytes]:
        """
        Receive data from connection
        
        Args:
            size: Number of bytes to receive (None = use buffer_size)
            
        Returns:
            Received data or None
        """
        try:
            if self.socket and self.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED]:
                size = size or self.config.buffer_size
                data = self.socket.recv(size)
                if data:
                    self.last_heartbeat = time.time()
                    return data
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Receive error: {e}")
            self.state = ConnectionState.ERROR
        return None
    
    def send_json(self, data: Dict[str, Any]) -> bool:
        """Send JSON data"""
        json_str = json.dumps(data)
        return self.send(json_str.encode())
    
    def receive_json(self) -> Optional[Dict[str, Any]]:
        """Receive JSON data"""
        data = self.receive()
        if data:
            try:
                return json.loads(data.decode())
            except json.JSONDecodeError:
                pass
        return None
    
    def _start_keepalive(self):
        """Start keepalive thread"""
        self.running = True
        self.keepalive_thread = threading.Thread(target=self._keepalive_loop, daemon=True)
        self.keepalive_thread.start()
    
    def _keepalive_loop(self):
        """Keepalive loop"""
        while self.running:
            time.sleep(self.config.keepalive_interval)
            
            if time.time() - self.last_heartbeat > self.config.keepalive_interval * 2:
                # Connection seems dead
                self.state = ConnectionState.ERROR
                break
            
            # Send heartbeat
            try:
                heartbeat = {'type': 'heartbeat', 'timestamp': time.time()}
                self.send_json(heartbeat)
            except:
                break
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.state = ConnectionState.DISCONNECTED
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED]


class ConnectionManager:
    """
    Connection manager with retry and pooling
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize connection manager
        
        Args:
            config: Connection configuration
        """
        self.config = config
        self.connections: List[SecureConnection] = []
        self.max_connections = 5
        self.lock = threading.Lock()
    
    def get_connection(self) -> Optional[SecureConnection]:
        """
        Get available connection (with retry)
        
        Returns:
            SecureConnection or None
        """
        for attempt in range(self.config.retry_count):
            try:
                # Try to reuse existing connection
                with self.lock:
                    for conn in self.connections:
                        if conn.is_connected():
                            return conn
                
                # Create new connection
                conn = SecureConnection(self.config)
                if conn.connect():
                    with self.lock:
                        if len(self.connections) < self.max_connections:
                            self.connections.append(conn)
                    return conn
                    
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay)
        
        return None
    
    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in self.connections:
                conn.disconnect()
            self.connections.clear()


class MessageQueue:
    """
    Message queue for reliable message delivery
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize message queue
        
        Args:
            max_size: Maximum queue size
        """
        self.queue: List[Dict[str, Any]] = []
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def enqueue(self, message: Dict[str, Any]) -> bool:
        """
        Add message to queue
        
        Args:
            message: Message to add
            
        Returns:
            True if successful
        """
        with self.lock:
            if len(self.queue) >= self.max_size:
                return False
            self.queue.append(message)
            return True
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Remove and return message from queue
        
        Returns:
            Message or None
        """
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
        return None
    
    def size(self) -> int:
        """Get queue size"""
        with self.lock:
            return len(self.queue)
    
    def clear(self):
        """Clear queue"""
        with self.lock:
            self.queue.clear()


class NetworkClient:
    """
    Enhanced network client with all features
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize network client
        
        Args:
            config: Connection configuration
        """
        self.config = config
        self.connection_manager = ConnectionManager(config)
        self.message_queue = MessageQueue()
        self.message_handlers: Dict[str, Callable] = {}
    
    def connect(self) -> bool:
        """Connect to server"""
        conn = self.connection_manager.get_connection()
        return conn is not None
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send message with retry
        
        Args:
            message: Message to send
            
        Returns:
            True if successful
        """
        conn = self.connection_manager.get_connection()
        if not conn:
            # Queue message for later
            self.message_queue.enqueue(message)
            return False
        
        success = conn.send_json(message)
        
        if not success:
            # Queue for retry
            self.message_queue.enqueue(message)
        
        return success
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message"""
        conn = self.connection_manager.get_connection()
        if not conn:
            return None
        
        return conn.receive_json()
    
    def process_queue(self):
        """Process queued messages"""
        while self.message_queue.size() > 0:
            message = self.message_queue.dequeue()
            if message:
                self.send_message(message)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
    
    def disconnect(self):
        """Disconnect from server"""
        self.connection_manager.close_all()


class NetworkServer:
    """
    Enhanced network server with connection management
    """
    
    def __init__(self, config: ConnectionConfig, handler: Callable):
        """
        Initialize network server
        
        Args:
            config: Server configuration
            handler: Message handler function
        """
        self.config = config
        self.handler = handler
        self.socket: Optional[socket.socket] = None
        self.ssl_context: Optional[ssl.SSLContext] = None
        self.running = False
        self.clients: List[SecureConnection] = []
        self.lock = threading.Lock()
    
    def start(self):
        """Start server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.config.host, self.config.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)
            
            # Setup TLS if enabled
            if self.config.use_tls:
                self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                if self.config.tls_cert_file:
                    self.ssl_context.load_cert_chain(
                        self.config.tls_cert_file,
                        self.config.tls_key_file
                    )
            
            self.running = True
            print(f"Server listening on {self.config.host}:{self.config.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"Client connected from {address}")
                    
                    # Wrap with TLS if enabled
                    if self.config.use_tls and self.ssl_context:
                        client_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
                    
                    # Handle client in thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle client connection"""
        try:
            while self.running:
                data = client_socket.recv(self.config.buffer_size)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    response = self.handler(message)
                    
                    if response:
                        client_socket.sendall(json.dumps(response).encode())
                        
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Client {address} disconnected")
    
    def stop(self):
        """Stop server"""
        self.running = False
        if self.socket:
            self.socket.close()

