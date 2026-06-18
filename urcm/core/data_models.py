"""
Core data models for the URCM reasoning system.

This module defines the fundamental data structures used throughout the URCM system,
including resonance states, attractor states, reasoning paths, and mesh signals.

PhonemeSequence and FrequencyPath are imported from hsrai.common.phoneme.
"""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np


@dataclass
class ResonanceState:
    """Represents the resonance state of the system at a given time."""
    resonance_vector: np.ndarray
    mu_value: float
    rho_density: float  # Semantic density (Information purity)
    chi_cost: float     # Transformation cost (Energy expenditure)
    stability_score: float
    oscillation_phase: float
    timestamp: float

    def __post_init__(self):
        if self.resonance_vector.ndim != 1:
            raise ValueError("Resonance vector must be 1-dimensional")
        if not (0 <= self.oscillation_phase <= 2 * np.pi):
            raise ValueError("Oscillation phase must be in range [0, 2π]")
        if self.timestamp < 0:
            raise ValueError("Timestamp must be non-negative")
        # Ensure mu = rho / chi (with epsilon for stability)
        # Use relative epsilon to avoid domination for small chi
        chi_eff = self.chi_cost + 1e-9
        if abs(self.chi_cost) < 1e-6:
            chi_eff = max(abs(self.chi_cost), 1e-6)
        calculated_mu = self.rho_density / chi_eff
        if not np.isclose(self.mu_value, calculated_mu, rtol=1e-3):
            raise ValueError(
                f"mu_value ({self.mu_value:.6f}) does not match "
                f"rho/chi ({calculated_mu:.6f}). "
                f"mu_value must equal rho_density / (chi_cost + epsilon)."
            )


@dataclass
class AttractorState:
    """Represents a stable attractor state in the semantic space."""
    phase_pattern: np.ndarray
    eigenvalues: np.ndarray
    stability_type: str  # "stable", "unstable", "saddle"
    semantic_label: Optional[str] = None

    def __post_init__(self):
        if self.phase_pattern.ndim != 1:
            raise ValueError("Phase pattern must be 1-dimensional")
        if self.eigenvalues.ndim != 1:
            raise ValueError("Eigenvalues must be 1-dimensional")
        if self.stability_type not in ["stable", "unstable", "saddle"]:
            raise ValueError("Stability type must be 'stable', 'unstable', or 'saddle'")


@dataclass
class ReasoningPath:
    """Represents a complete reasoning path through the system."""
    initial_state: ResonanceState
    intermediate_states: List[ResonanceState]
    final_state: ResonanceState
    mu_trajectory: List[float]
    convergence_achieved: bool
    termination_reason: str

    def __post_init__(self):
        if not self.intermediate_states:
            self.intermediate_states = []
        if len(self.mu_trajectory) != len(self.intermediate_states) + 2:
            raise ValueError("μ trajectory length must match total number of states")
        if not self.termination_reason:
            raise ValueError("Termination reason cannot be empty")


@dataclass
class MeshSignal:
    """Represents a signal exchanged between mesh nodes."""
    sender_id: str
    delta_mu: float
    phase_alignment: float
    timestamp: float
    signal_type: str  # "sync", "convergence", "error"

    def __post_init__(self):
        if not self.sender_id:
            raise ValueError("Sender ID cannot be empty")
        if self.signal_type not in ["sync", "convergence", "error"]:
            raise ValueError("Signal type must be 'sync', 'convergence', or 'error'")
        if not (0 <= self.phase_alignment <= 2 * np.pi):
            raise ValueError("Phase alignment must be in range [0, 2π]")
        if self.timestamp < 0:
            raise ValueError("Timestamp must be non-negative")
