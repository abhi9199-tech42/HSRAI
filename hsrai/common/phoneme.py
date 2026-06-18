from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class PhonemeSequence:
    """Represents a sequence of phonemes derived from input text."""
    phonemes: List[str]
    source_text: str
    language_hint: Optional[str] = None

    def __post_init__(self):
        if not self.phonemes:
            raise ValueError("Phoneme sequence cannot be empty")
        if not self.source_text:
            raise ValueError("Source text cannot be empty")

@dataclass
class FrequencyPath:
    """Represents a continuous frequency path derived from phoneme sequences."""
    vectors: np.ndarray  # Shape: (sequence_length, K) where K ∈ [16, 32]
    smoothness_score: float
    phoneme_mapping: List[Tuple[str, int]]  # (phoneme, vector_index)

    def __post_init__(self):
        if self.vectors.ndim != 2:
            raise ValueError("Frequency vectors must be 2-dimensional")
        if not (16 <= self.vectors.shape[1] <= 32):
            raise ValueError("Frequency dimension K must be in range [16, 32]")
        if self.smoothness_score < 0:
            raise ValueError("Smoothness score must be non-negative")
        if len(self.phoneme_mapping) != self.vectors.shape[0]:
            raise ValueError("Phoneme mapping length must match vector sequence length")
