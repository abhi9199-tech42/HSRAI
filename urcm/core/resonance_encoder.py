"""
Resonance Path Encoder System.

This module is responsible for converting temporal frequency paths (sequences of phoneme vectors)
into stable resonance states (semantic representations).

It supports modular encoding backends, with a default NumPy-based recurrent implementation
that simulates semantic accumulation through time.
"""

from typing import Optional, Dict, Any, Union
import numpy as np
import time

from urcm.core.data_models import FrequencyPath, ResonanceState
from urcm.core.theory import URCMTheory

class ResonancePathEncoder:
    """
    Encodes frequency paths into resonance states using temporal processing.
    
    This system works like a 'Semantic Ear', listening to the sequence of
    phoneme frequencies and building up a stable 'chord' (ResonanceState)
    that represents the meaning.
    """
    
    def __init__(
        self, 
        input_dim: int = 24, 
        resonance_dim: int = 64,
        encoder_type: str = "recurrent_numpy"
    ):
        """
        Initialize the encoder.
        
        Args:
            input_dim: Dimensionality of input frequency vectors (K).
            resonance_dim: Dimensionality of the output resonance state.
            encoder_type: Type of encoder backend ('recurrent_numpy', 'transformer_stub').
        """
        self.input_dim = input_dim
        self.resonance_dim = resonance_dim
        self.encoder_type = encoder_type
        
        # Initialize internal state/weights based on type
        if encoder_type == "recurrent_numpy":
            self._init_numpy_recurrent()
        elif encoder_type == "transformer_stub":
            self._init_transformer_stub()
        else:
            raise ValueError(f"Unsupported encoder type: {encoder_type}")
            
    def _init_numpy_recurrent(self):
        """
        Initialize a simple Echo State Network / Reservoir-like structure
        using pure NumPy for temporal integration.
        """
        # Random projection matrix from Input -> Resonance Space
        np.random.seed(42)  # Deterministic initialization for consistency
        self.W_in = np.random.normal(0, 0.1, (self.input_dim, self.resonance_dim))
        
        # Recurrent weight matrix (Resonance -> Resonance)
        # Scaled to be stable (spectral radius < 1 generally, but close to 1 for long memory)
        self.W_res = np.random.normal(0, 0.1, (self.resonance_dim, self.resonance_dim))
        
        # Ensure spectral radius is < 1 to prevent explosion
        spectral_radius = np.max(np.abs(np.linalg.eigvals(self.W_res)))
        if spectral_radius > 0:
            self.W_res = self.W_res / (spectral_radius * 1.1)
            
        # Bias
        self.bias = np.random.normal(0, 0.01, self.resonance_dim)

    def _init_transformer_stub(self):
        """
        Initialize weights for a lightweight Transformer-like attention mechanism.
        (Stub implementation for future expansion).
        """
        np.random.seed(42)
        # Simple Query/Key/Value projection simulation
        # W_q: Input -> hidden
        # W_k: Input -> hidden
        # W_v: Input -> Resonance
        self.W_q = np.random.normal(0, 0.1, (self.input_dim, 32))
        self.W_k = np.random.normal(0, 0.1, (self.input_dim, 32))
        self.W_v = np.random.normal(0, 0.1, (self.input_dim, self.resonance_dim))
        
    def encode_path(self, frequency_path: Union[FrequencyPath, np.ndarray]) -> np.ndarray:
        """
        Convert a frequency path into a final resonance vector.
        
        Args:
            frequency_path: Input mechanism (FrequencyPath object or raw numpy array).
            
        Returns:
            np.ndarray: The final resonance vector (1D array of size resonance_dim).
        """
        # Extract vectors
        if isinstance(frequency_path, FrequencyPath):
            vectors = frequency_path.vectors
        else:
            vectors = frequency_path
            
        if vectors.shape[1] != self.input_dim:
            raise ValueError(
                f"Input dimension mismatch. Expected {self.input_dim}, got {vectors.shape[1]}"
            )
            
        if self.encoder_type == "recurrent_numpy":
            return self._encode_recurrent(vectors)
        elif self.encoder_type == "transformer_stub":
            return self._encode_transformer(vectors)
        else:
            raise ValueError(f"Unknown encoder type: {self.encoder_type}")

    def _encode_recurrent(self, vectors: np.ndarray) -> np.ndarray:
        # Initialize state
        current_state = np.zeros(self.resonance_dim)
        
        # Temporal Processing Loop (The "Listening" Phase)
        # s_t = tanh(W_in * x_t + W_res * s_{t-1} + b)
        for t in range(vectors.shape[0]):
            x_t = vectors[t]
            
            # Input projection
            input_signal = np.dot(x_t, self.W_in)
            
            # Recurrent echo
            echo_signal = np.dot(current_state, self.W_res)
            
            # Non-linear activation (tanh works well for resonance bounds [-1, 1])
            current_state = np.tanh(input_signal + echo_signal + self.bias)
            
        return current_state

    def _encode_transformer(self, vectors: np.ndarray) -> np.ndarray:
        """
        Simplified self-attention pooling (Stub).
        Computes a weighted average of value vectors based on self-attention.
        """
        # Q = vectors * W_q
        # K = vectors * W_k
        # V = vectors * W_v
        
        Q = np.dot(vectors, self.W_q) # (Seq, 32)
        K = np.dot(vectors, self.W_k) # (Seq, 32)
        V = np.dot(vectors, self.W_v) # (Seq, Dim)
        
        # Attention scores = softmax(Q * K.T / sqrt(d_k))
        # We'll just do a global pooling for the "context vector"
        # For this stub, let's treat the *last* vector as the query for the whole sequence
        query = Q[-1] # (32,)
        
        scores = np.dot(K, query) / np.sqrt(32) # (Seq,)
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores))
        weights = exp_scores / np.sum(exp_scores)
        
        # Weighted sum of V
        # context = sum(w_i * v_i)
        context = np.dot(weights, V) # (Dim,)
        
        return np.tanh(context) # Squash to valid resonance range

    def get_resonance_state(self, frequency_path: FrequencyPath) -> ResonanceState:
        """
        Generate a complete ResonanceState object with metadata and theoretical metrics.
        
        Args:
            frequency_path: The input frequency path.
            
        Returns:
            ResonanceState: Fully computed state ready for the Reasoning Engine.
        """
        # 1. Encode the path
        resonance_vector = self.encode_path(frequency_path)
        
        # 2. Calculate Theoretical Metrics
        # ρ (rho): Semantic Density - how 'pure' or 'strong' is the signal?
        rho = URCMTheory.calculate_rho(resonance_vector)
        
        # χ (chi): Transformation Cost - "Manifold distance" from zero/neutral state
        # In this context, we can define chi as the energy required to maintain this state.
        # Simple approximation: Norm of the vector.
        chi = np.linalg.norm(resonance_vector)
        
        # μ (mu): Resonance/Stability = rho / chi
        mu = URCMTheory.compute_mu(rho, chi)
        
        # Stability Score: A higher-level metric, can be derived from mu and smoothness
        stability = mu * (1.0 + frequency_path.smoothness_score)
        
        # Phase: Initial phase is 0, will be modulated by OscillatoryGating later
        phase = 0.0
        
        return ResonanceState(
            resonance_vector=resonance_vector,
            mu_value=mu,
            rho_density=rho,
            chi_cost=chi,
            stability_score=stability,
            oscillation_phase=phase,
            timestamp=time.time()
        )
