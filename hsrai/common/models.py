from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np
from pydantic import BaseModel, Field

from .types import SemanticType


class SemanticPrimitive(BaseModel):
    """
    Base unit of meaning in the HSRAI.
    Represents a compressed, pre-linguistic concept.
    """
    id: str
    concept: str
    type: SemanticType = SemanticType.CONCEPT
    semantic_weight: float = 1.0
    modality: str = "text"
    compression_metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}

    def __hash__(self):
        return hash((self.id, self.concept, self.type, self.semantic_weight, self.modality))

    def __eq__(self, other):
        if not isinstance(other, SemanticPrimitive):
            return False
        return (self.id == other.id and
                self.concept == other.concept and
                self.type == other.type and
                self.semantic_weight == other.semantic_weight and
                self.modality == other.modality)

@dataclass
class ResonanceState:
    """
    Represents the resonance state of the system at a given time.
    Integrates oscillatory dynamics with semantic processing.
    """
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
        epsilon = 1e-9
        chi_eff = self.chi_cost + epsilon if abs(self.chi_cost) < epsilon else self.chi_cost
        calculated_mu = self.rho_density / chi_eff
        if not np.isclose(self.mu_value, calculated_mu, rtol=1e-6, atol=1e-9):
             raise ValueError(
                 f"mu_value ({self.mu_value:.6f}) does not match "
                 f"rho/chi ({calculated_mu:.6f}). "
                 f"mu_value must equal rho_density / (chi_cost + epsilon)."
             )

@dataclass
class TrustCertificate:
    """
    Cryptographic proof of behavioral alignment and verification.
    """
    certificate_id: str
    issuer_id: str
    subject_id: str
    trust_score: float
    timestamp: float
    signature: str
    public_key_fingerprint: str = ""  # SHA256 of the public key used for signing
    claims: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not (0.0 <= self.trust_score <= 1.0):
            raise ValueError("Trust score must be between 0.0 and 1.0")
