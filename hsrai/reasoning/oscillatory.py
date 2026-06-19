import asyncio
import threading

import numpy as np


class OscillatoryGating:
    """
    Manages the global oscillatory rhythm and applies gating to resonance states.

    Implements the equation: ỹt = yt ⊙ σ(Wg·g(t) + b)
    """

    def __init__(self, resonance_dim: int = 64, base_frequency: float = 1.0):
        self.resonance_dim = resonance_dim
        self.base_frequency = base_frequency
        self.phase = 0.0
        self._lock = asyncio.Lock()
        self._sync_lock = threading.Lock()

        # Initialize Gating Weights (W_g) and Bias (b)
        rng = np.random.default_rng(42)
        self.W_g = rng.normal(0, 0.5, (resonance_dim, 2))
        self.bias = np.zeros(resonance_dim)  # Start neutral

    def get_global_rhythm(self) -> np.ndarray:
        """
        Returns the current global rhythm state g(t) = [sin(φ), cos(φ)].
        Returns a vector of shape (2,).
        """
        return np.array([np.sin(self.phase), np.cos(self.phase)])

    async def advance_time(self, dt: float):
        """
        Advances the internal phase based on time step dt.
        phase = phase + 2π * f * dt
        """
        async with self._lock:
            self.phase += 2 * np.pi * self.base_frequency * dt
            self.phase %= (2 * np.pi)  # Keep in [0, 2π]

    def advance_time_sync(self, dt: float):
        """Synchronous version for non-async contexts."""
        with self._sync_lock:
            self.phase += 2 * np.pi * self.base_frequency * dt
            self.phase %= (2 * np.pi)

    async def reset_phase(self, new_phase: float = 0.0):
        """Resets the oscillatory phase (e.g., for error recovery)."""
        async with self._lock:
            self.phase = new_phase

    def reset_phase_sync(self, new_phase: float = 0.0):
        """Synchronous version for non-async contexts."""
        with self._sync_lock:
            self.phase = new_phase

    async def apply_gating(self, resonance_vector: np.ndarray, dt: float = 0.0) -> np.ndarray:
        """
        Applies oscillatory gating to a resonance vector.

        Args:
            resonance_vector: The input vector y_t.
            dt: Optional time increment to advance phase before gating.

        Returns:
            The gated vector ỹt = yt ⊙ σ(Wg·g(t) + b).
        """
        # Ensure input dimensions match
        if resonance_vector.shape[0] != self.resonance_dim:
             raise ValueError(f"Input dimension {resonance_vector.shape[0]} does not match resonance dim {self.resonance_dim}")

        if dt > 0:
            await self.advance_time(dt)

        g_t = self.get_global_rhythm()  # Shape (2,)

        # Calculate Gate Activation
        # gate_signal = W_g · g(t) + b
        gate_signal = np.dot(self.W_g, g_t) + self.bias

        # Sigmoid function σ(x) = 1 / (1 + e^-x)
        sigmoid = 1.0 / (1.0 + np.exp(-gate_signal))

        # Apply gating: yt ⊙ gate
        return resonance_vector * sigmoid

    def apply_gating_sync(self, resonance_vector: np.ndarray, dt: float = 0.0) -> np.ndarray:
        """Synchronous version for non-async contexts."""
        if resonance_vector.shape[0] != self.resonance_dim:
             raise ValueError(f"Input dimension {resonance_vector.shape[0]} does not match resonance dim {self.resonance_dim}")

        if dt > 0:
            self.advance_time_sync(dt)

        g_t = self.get_global_rhythm()
        gate_signal = np.dot(self.W_g, g_t) + self.bias
        sigmoid = 1.0 / (1.0 + np.exp(-gate_signal))
        return resonance_vector * sigmoid

    async def in_attention_window(self, threshold: float = 0.0) -> bool:
        """
        Checks if the current phase is within the 'attention window'.
        Defined as the positive half-cycle of the cosine component (cos(φ) > threshold).
        """
        async with self._lock:
            g_t = self.get_global_rhythm()
            return g_t[1] > threshold

    def in_attention_window_sync(self, threshold: float = 0.0) -> bool:
        """Synchronous version for non-async contexts."""
        with self._sync_lock:
            g_t = self.get_global_rhythm()
            return g_t[1] > threshold
