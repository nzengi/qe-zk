"""
Complete Distributed QE-ZK Protocol

Full implementation of distributed QE-ZK protocol over network.
"""

import json
import socket
import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from .protocol import QuantumEntanglementZK, QEZKProof
from .exceptions import ProtocolError, ConfigurationError


class MessageType(Enum):
    """Protocol message types"""
    SETUP_REQUEST = "setup_request"
    SETUP_RESPONSE = "setup_response"
    PROVER_RESULTS = "prover_results"
    VERIFIER_RESULTS = "verifier_results"
    VERIFICATION_REQUEST = "verification_request"
    VERIFICATION_RESPONSE = "verification_response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class ProtocolMessage:
    """Network protocol message"""
    message_type: str
    data: Dict[str, Any]
    timestamp: float
    message_id: str
    sender_id: str
    
    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProtocolMessage':
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create(cls, message_type: MessageType, data: Dict[str, Any], sender_id: str) -> 'ProtocolMessage':
        """Create new message"""
        return cls(
            message_type=message_type.value,
            data=data,
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            sender_id=sender_id
        )


class DistributedProver:
    """
    Distributed Prover implementation
    
    Handles prover side of distributed QE-ZK protocol.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK, host: str = 'localhost', port: int = 8888):
        """
        Initialize distributed prover
        
        Args:
            qezk: QE-ZK instance
            host: Host address
            port: Port number
        """
        self.qezk = qezk
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.running = False
        self.node_id = "prover"
        self.current_statement: Optional[str] = None
        self.current_witness: Optional[str] = None
    
    def start_server(self):
        """Start prover server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.running = True
        
        print(f"Prover server listening on {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"Verifier connected from {address}")
                self.client_socket = client_socket
                self._handle_verifier()
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
    
    def _handle_verifier(self):
        """Handle verifier connection"""
        try:
            while True:
                data = self.client_socket.recv(8192)
                if not data:
                    break
                
                message = ProtocolMessage.from_json(data.decode())
                response = self._process_message(message)
                
                if response:
                    self._send_message(response)
                    
        except Exception as e:
            print(f"Error handling verifier: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def _process_message(self, message: ProtocolMessage) -> Optional[ProtocolMessage]:
        """Process incoming message"""
        if message.message_type == MessageType.SETUP_REQUEST.value:
            return self._handle_setup_request(message)
        elif message.message_type == MessageType.VERIFICATION_REQUEST.value:
            return self._handle_verification_request(message)
        elif message.message_type == MessageType.HEARTBEAT.value:
            return ProtocolMessage.create(MessageType.HEARTBEAT, {}, self.node_id)
        else:
            return ProtocolMessage.create(
                MessageType.ERROR,
                {'error': f'Unknown message type: {message.message_type}'},
                self.node_id
            )
    
    def _handle_setup_request(self, message: ProtocolMessage) -> ProtocolMessage:
        """Handle setup request"""
        try:
            statement = message.data.get('statement')
            witness = message.data.get('witness')
            seed = message.data.get('seed')
            
            if not statement or not witness:
                raise ProtocolError("Missing statement or witness")
            
            self.current_statement = statement
            self.current_witness = witness
            
            # Execute prover phase
            prover_particles, _ = self.qezk.setup(seed)
            prover_results, measurement_bases = self.qezk.prover_phase(
                statement, witness, prover_particles
            )
            
            return ProtocolMessage.create(
                MessageType.PROVER_RESULTS,
                {
                    'prover_results': prover_results,
                    'measurement_bases': measurement_bases,
                    'statement': statement
                },
                self.node_id
            )
            
        except Exception as e:
            return ProtocolMessage.create(
                MessageType.ERROR,
                {'error': str(e)},
                self.node_id
            )
    
    def _handle_verification_request(self, message: ProtocolMessage) -> ProtocolMessage:
        """Handle verification request"""
        try:
            prover_results = message.data.get('prover_results')
            verifier_results = message.data.get('verifier_results')
            measurement_bases = message.data.get('measurement_bases')
            
            if not all([prover_results, verifier_results, measurement_bases]):
                raise ProtocolError("Missing verification data")
            
            # Verify
            is_valid, chsh_value = self.qezk.verify(
                prover_results, verifier_results, measurement_bases
            )
            
            return ProtocolMessage.create(
                MessageType.VERIFICATION_RESPONSE,
                {
                    'is_valid': is_valid,
                    'chsh_value': chsh_value,
                    'statement': self.current_statement
                },
                self.node_id
            )
            
        except Exception as e:
            return ProtocolMessage.create(
                MessageType.ERROR,
                {'error': str(e)},
                self.node_id
            )
    
    def _send_message(self, message: ProtocolMessage):
        """Send message to verifier"""
        if self.client_socket:
            data = message.to_json().encode()
            self.client_socket.send(data)
    
    def stop(self):
        """Stop prover server"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.socket:
            self.socket.close()


class DistributedVerifier:
    """
    Distributed Verifier implementation
    
    Handles verifier side of distributed QE-ZK protocol.
    """
    
    def __init__(self, qezk: QuantumEntanglementZK, prover_host: str = 'localhost', prover_port: int = 8888):
        """
        Initialize distributed verifier
        
        Args:
            qezk: QE-ZK instance
            prover_host: Prover host address
            prover_port: Prover port number
        """
        self.qezk = qezk
        self.prover_host = prover_host
        self.prover_port = prover_port
        self.socket: Optional[socket.socket] = None
        self.node_id = "verifier"
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to prover"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.prover_host, self.prover_port))
            self.connected = True
            print(f"Connected to prover at {self.prover_host}:{self.prover_port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def verify_statement(self, statement: str, seed: Optional[int] = None) -> Optional[QEZKProof]:
        """
        Verify statement using distributed protocol
        
        Args:
            statement: Statement to verify
            seed: Optional random seed
            
        Returns:
            QEZKProof if successful, None otherwise
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            # Step 1: Send setup request
            setup_message = ProtocolMessage.create(
                MessageType.SETUP_REQUEST,
                {'statement': statement, 'seed': seed},
                self.node_id
            )
            self._send_message(setup_message)
            
            # Step 2: Receive prover results
            prover_response = self._receive_message()
            if not prover_response or prover_response.message_type == MessageType.ERROR.value:
                print("Error from prover")
                return None
            
            prover_results = prover_response.data['prover_results']
            measurement_bases = prover_response.data['measurement_bases']
            
            # Step 3: Execute verifier phase
            _, verifier_particles = self.qezk.setup(seed)
            verifier_results = self.qezk.verifier_phase(
                statement, verifier_particles, measurement_bases
            )
            
            # Step 4: Send verification request
            verification_message = ProtocolMessage.create(
                MessageType.VERIFICATION_REQUEST,
                {
                    'prover_results': prover_results,
                    'verifier_results': verifier_results,
                    'measurement_bases': measurement_bases
                },
                self.node_id
            )
            self._send_message(verification_message)
            
            # Step 5: Receive verification response
            verification_response = self._receive_message()
            if not verification_response or verification_response.message_type == MessageType.ERROR.value:
                print("Verification error")
                return None
            
            # Create proof
            return QEZKProof(
                prover_results=prover_results,
                verifier_results=verifier_results,
                measurement_bases=measurement_bases,
                chsh_value=verification_response.data['chsh_value'],
                is_valid=verification_response.data['is_valid'],
                statement=statement
            )
            
        except Exception as e:
            print(f"Protocol error: {e}")
            return None
    
    def _send_message(self, message: ProtocolMessage):
        """Send message to prover"""
        if self.socket:
            data = message.to_json().encode()
            self.socket.send(data)
    
    def _receive_message(self) -> Optional[ProtocolMessage]:
        """Receive message from prover"""
        try:
            if self.socket:
                data = self.socket.recv(8192)
                if data:
                    return ProtocolMessage.from_json(data.decode())
        except Exception as e:
            print(f"Error receiving message: {e}")
        return None
    
    def disconnect(self):
        """Disconnect from prover"""
        if self.socket:
            self.socket.close()
            self.connected = False

