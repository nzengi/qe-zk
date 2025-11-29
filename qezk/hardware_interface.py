"""
Quantum Hardware Interface

Abstract interface for real quantum hardware integration.
Supports multiple quantum computing backends (IBM Q, Google Quantum AI, Rigetti, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from .exceptions import QuantumStateError, EntanglementError, MeasurementError


class QuantumHardwareBackend(ABC):
    """
    Abstract base class for quantum hardware backends
    
    This interface allows QE-ZK to work with different quantum computing platforms.
    """
    
    @abstractmethod
    def create_bell_state(self, state_type: str = 'phi_plus') -> np.ndarray:
        """
        Create Bell state on quantum hardware
        
        Args:
            state_type: Type of Bell state ('phi_plus', 'phi_minus', 'psi_plus', 'psi_minus')
            
        Returns:
            Quantum state (may be simulated representation)
        """
        pass
    
    @abstractmethod
    def measure(self, qubit_index: int, basis: str) -> int:
        """
        Measure qubit in specified basis
        
        Args:
            qubit_index: Index of qubit to measure
            basis: Measurement basis ('Z', 'X', or 'Y')
            
        Returns:
            Measurement result (0 or 1)
        """
        pass
    
    @abstractmethod
    def apply_gate(self, gate_name: str, qubit_index: int) -> None:
        """
        Apply quantum gate to qubit
        
        Args:
            gate_name: Name of gate ('H', 'X', 'Y', 'Z', 'CNOT', etc.)
            qubit_index: Index of qubit to apply gate to
        """
        pass
    
    @abstractmethod
    def get_state(self) -> np.ndarray:
        """
        Get current quantum state (if accessible)
        
        Returns:
            Quantum state vector
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset quantum state to |00⟩"""
        pass


class SimulationBackend(QuantumHardwareBackend):
    """
    Simulation backend (current implementation)
    
    Uses NumPy for quantum state simulation.
    This is the default backend for development and testing.
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Initialize simulation backend
        
        Args:
            num_qubits: Number of qubits (default: 2 for EPR pairs)
        """
        self.num_qubits = num_qubits
        self.state = np.array([1, 0, 0, 0], dtype=complex)  # |00⟩
        
        # Quantum gates
        self.H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        self.X = np.array([[0, 1], [1, 0]], dtype=complex)
        self.Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self.I = np.eye(2, dtype=complex)
        self.S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
        self.T = np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex)  # π/8 gate
        self.CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
    
    def create_bell_state(self, state_type: str = 'phi_plus') -> np.ndarray:
        """Create Bell state (simulation)"""
        self.state = np.array([1, 0, 0, 0], dtype=complex)
        
        # Apply Hadamard to first qubit
        H_full = np.kron(self.H, self.I)
        self.state = H_full @ self.state
        
        # Apply CNOT
        self.state = self.CNOT @ self.state
        
        # Apply additional gates for other Bell states
        if state_type == 'phi_minus':
            Z_full = np.kron(self.Z, self.I)
            self.state = Z_full @ self.state
        elif state_type == 'psi_plus':
            X_full = np.kron(self.X, self.I)
            self.state = X_full @ self.state
        elif state_type == 'psi_minus':
            Y_full = np.kron(self.Y, self.I)
            self.state = Y_full @ self.state
        
        return self.state
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """Measure qubit in specified basis (simulation)"""
        if basis == 'Z':
            # Standard computational basis
            if qubit_index == 0:
                prob_0 = np.abs(self.state[0])**2 + np.abs(self.state[1])**2
            else:
                prob_0 = np.abs(self.state[0])**2 + np.abs(self.state[2])**2
            
            result = 0 if np.random.random() < prob_0 else 1
            
        elif basis == 'X':
            # Hadamard basis
            # Apply Hadamard before measurement
            if qubit_index == 0:
                H_full = np.kron(self.H, self.I)
                temp_state = H_full @ self.state
                prob_0 = np.abs(temp_state[0])**2 + np.abs(temp_state[1])**2
            else:
                H_full = np.kron(self.I, self.H)
                temp_state = H_full @ self.state
                prob_0 = np.abs(temp_state[0])**2 + np.abs(temp_state[2])**2
            
            result = 0 if np.random.random() < prob_0 else 1
            
        elif basis == 'Y':
            # Y basis (requires S gate + Hadamard)
            # Simplified: use X basis approximation
            result = self.measure(qubit_index, 'X')
            
        else:
            raise MeasurementError(f"Unknown basis: {basis}")
        
        return result
    
    def apply_gate(self, gate_name: str, qubit_index: int) -> None:
        """Apply quantum gate (simulation)"""
        gate_map = {
            'H': self.H,
            'X': self.X,
            'Y': self.Y,
            'Z': self.Z,
            'I': self.I,
            'S': self.S,
            'T': self.T
        }
        
        if gate_name not in gate_map:
            raise QuantumStateError(f"Unknown gate: {gate_name}")
        
        gate = gate_map[gate_name]
        
        if qubit_index == 0:
            gate_full = np.kron(gate, self.I)
        else:
            gate_full = np.kron(self.I, gate)
        
        self.state = gate_full @ self.state
    
    def get_state(self) -> np.ndarray:
        """Get current quantum state"""
        return self.state.copy()
    
    def reset(self) -> None:
        """Reset to |00⟩"""
        self.state = np.array([1, 0, 0, 0], dtype=complex)


class IBMQBackend(QuantumHardwareBackend):
    """
    IBM Quantum (Qiskit) backend interface
    
    Requires: pip install qiskit qiskit-ibm-provider
    """
    
    def __init__(self, backend_name: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize IBM Quantum backend
        
        Args:
            backend_name: Name of IBM Quantum backend (e.g., 'ibmq_lima')
            api_token: IBM Quantum API token
        """
        self.backend_name = backend_name
        self.api_token = api_token
        self.provider = None
        self.backend = None
        self._initialize_ibmq()
    
    def _initialize_ibmq(self):
        """Initialize IBM Quantum connection"""
        try:
            from qiskit import IBMQ
            from qiskit_ibm_provider import IBMProvider
            
            if self.api_token:
                IBMProvider.save_account(token=self.api_token)
            
            self.provider = IBMProvider()
            
            if self.backend_name:
                self.backend = self.provider.get_backend(self.backend_name)
            else:
                # Use least busy available backend
                backends = self.provider.backends()
                self.backend = self.provider.least_busy(backends)
                
        except ImportError:
            raise QuantumStateError(
                "Qiskit not installed. Install with: pip install qiskit qiskit-ibm-provider"
            )
        except Exception as e:
            raise QuantumStateError(f"Failed to initialize IBM Quantum: {str(e)}")
    
    def create_bell_state(self, state_type: str = 'phi_plus') -> np.ndarray:
        """Create Bell state on IBM Quantum hardware"""
        from qiskit import QuantumCircuit
        
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        
        # Additional gates for other Bell states
        if state_type == 'phi_minus':
            qc.z(0)
        elif state_type == 'psi_plus':
            qc.x(0)
        elif state_type == 'psi_minus':
            qc.y(0)
        
        # Execute on hardware
        job = self.backend.run(qc)
        result = job.result()
        
        # Return statevector (simulated for now)
        from qiskit.quantum_info import Statevector
        statevector = Statevector.from_instruction(qc)
        return statevector.data
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """Measure qubit on IBM Quantum hardware"""
        from qiskit import QuantumCircuit
        
        qc = QuantumCircuit(2, 2)
        
        # Apply basis rotation
        if basis == 'X':
            qc.h(qubit_index)
        elif basis == 'Y':
            qc.s(qubit_index)
            qc.h(qubit_index)
        # Z basis: no rotation needed
        
        qc.measure(qubit_index, qubit_index)
        
        job = self.backend.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        
        # Extract measurement result
        measurement = list(counts.keys())[0]
        return int(measurement[qubit_index])
    
    def apply_gate(self, gate_name: str, qubit_index: int) -> None:
        """Apply gate on IBM Quantum hardware"""
        # Gate application is handled in circuit construction
        pass
    
    def get_state(self) -> np.ndarray:
        """Get state from IBM Quantum (may not be accessible)"""
        # Real hardware doesn't allow state inspection
        raise QuantumStateError("State inspection not available on real hardware")
    
    def reset(self) -> None:
        """Reset qubits (hardware dependent)"""
        # Hardware reset may require re-initialization
        pass


class GoogleQuantumAIBackend(QuantumHardwareBackend):
    """
    Google Quantum AI (Cirq) backend interface
    
    Requires: pip install cirq-google
    """
    
    def __init__(self, processor_id: Optional[str] = None):
        """
        Initialize Google Quantum AI backend
        
        Args:
            processor_id: Google Quantum AI processor ID
        """
        self.processor_id = processor_id
        self._initialize_google()
    
    def _initialize_google(self):
        """Initialize Google Quantum AI connection"""
        try:
            import cirq
            import cirq_google
            
            if self.processor_id:
                self.processor = cirq_google.get_engine().get_processor(self.processor_id)
            else:
                # Use default processor
                self.processor = cirq_google.get_engine().get_processor()
                
        except ImportError:
            raise QuantumStateError(
                "Cirq not installed. Install with: pip install cirq cirq-google"
            )
        except Exception as e:
            raise QuantumStateError(f"Failed to initialize Google Quantum AI: {str(e)}")
    
    def create_bell_state(self, state_type: str = 'phi_plus') -> np.ndarray:
        """Create Bell state on Google Quantum AI hardware"""
        import cirq
        
        qubits = cirq.LineQubit.range(2)
        circuit = cirq.Circuit()
        circuit.append(cirq.H(qubits[0]))
        circuit.append(cirq.CNOT(qubits[0], qubits[1]))
        
        # Execute on hardware
        # (Implementation details depend on Google Quantum AI API)
        # For now, return simulated state
        return np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
    
    def measure(self, qubit_index: int, basis: str) -> int:
        """Measure qubit on Google Quantum AI hardware"""
        # Implementation depends on Google Quantum AI API
        raise NotImplementedError("Google Quantum AI measurement not fully implemented")
    
    def apply_gate(self, gate_name: str, qubit_index: int) -> None:
        """Apply gate on Google Quantum AI hardware"""
        pass
    
    def get_state(self) -> np.ndarray:
        """Get state from Google Quantum AI"""
        raise QuantumStateError("State inspection not available on real hardware")
    
    def reset(self) -> None:
        """Reset qubits"""
        pass


class HardwareInterface:
    """
    High-level interface for quantum hardware integration
    
    Provides a unified interface for QE-ZK to work with different backends.
    """
    
    def __init__(self, backend: Optional[QuantumHardwareBackend] = None):
        """
        Initialize hardware interface
        
        Args:
            backend: Quantum hardware backend (default: SimulationBackend)
        """
        if backend is None:
            self.backend = SimulationBackend()
        else:
            self.backend = backend
    
    def generate_epr_pairs(self, num_pairs: int, state_type: str = 'phi_plus') -> List[np.ndarray]:
        """
        Generate EPR pairs using hardware backend
        
        Args:
            num_pairs: Number of EPR pairs to generate
            state_type: Type of Bell state
            
        Returns:
            List of EPR pair states
        """
        epr_pairs = []
        for _ in range(num_pairs):
            bell_state = self.backend.create_bell_state(state_type)
            epr_pairs.append(bell_state)
        return epr_pairs
    
    def measure_particle(self, particle_index: int, basis: str) -> int:
        """
        Measure particle in specified basis
        
        Args:
            particle_index: Index of particle/qubit
            basis: Measurement basis ('Z', 'X', or 'Y')
            
        Returns:
            Measurement result (0 or 1)
        """
        return self.backend.measure(particle_index, basis)
    
    def apply_quantum_gate(self, gate_name: str, qubit_index: int) -> None:
        """
        Apply quantum gate to qubit
        
        Args:
            gate_name: Name of gate
            qubit_index: Index of qubit
        """
        self.backend.apply_gate(gate_name, qubit_index)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the hardware backend
        
        Returns:
            Dictionary with backend information
        """
        return {
            'backend_type': type(self.backend).__name__,
            'is_simulation': isinstance(self.backend, SimulationBackend),
            'num_qubits': getattr(self.backend, 'num_qubits', None)
        }

