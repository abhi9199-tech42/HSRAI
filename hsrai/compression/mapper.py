from typing import Dict, List

import numpy as np

from hsrai.common.phoneme import FrequencyPath, PhonemeSequence


class PhonemeFrequencyMapper:
    """
    Maps Sanskrit-derived phonemes to continuous frequency vectors in K-dimensional space.
    """

    # Sanskrit-derived phoneme set for complete articulatory coverage
    SANSKRIT_PHONEMES = {
        # Vowels (स्वर)
        'a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'e', 'ai', 'o', 'au',

        # Consonants - Stops (स्पर्श)
        # Velar (कण्ठ्य)
        'k', 'kh', 'g', 'gh', 'ṅ',
        # Palatal (तालव्य)
        'c', 'ch', 'j', 'jh', 'ñ',
        # Retroflex (मूर्धन्य)
        'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
        # Dental (दन्त्य)
        't', 'th', 'd', 'dh', 'n',
        # Labial (ओष्ठ्य)
        'p', 'ph', 'b', 'bh', 'm',

        # Semivowels (अन्तःस्थ)
        'y', 'r', 'l', 'v',

        # Sibilants (ऊष्म)
        'ś', 'ṣ', 's', 'h',

        # Additional phonemes for broader coverage
        'x', 'z', 'f', 'w'  # For non-Sanskrit languages
    }

    def __init__(self, frequency_dim: int = 24, smoothness_weight: float = 0.1):
        """
        Initialize the phoneme-frequency mapper.
        
        Args:
            frequency_dim: Dimensionality of frequency vectors (K ∈ [16, 32])
            smoothness_weight: Weight for smoothness constraint enforcement
        """
        if not (16 <= frequency_dim <= 32):
            raise ValueError("Frequency dimension K must be in range [16, 32]")

        self.phoneme_space = self.SANSKRIT_PHONEMES.copy()
        self.K = frequency_dim
        self.smoothness_weight = smoothness_weight

        # Initialize phoneme-to-frequency mapping
        self._initialize_phoneme_vectors()

    def _initialize_phoneme_vectors(self):
        """Initialize deterministic phoneme-to-frequency vector mappings."""
        # Create deterministic mapping based on phoneme characteristics
        self.phoneme_vectors = {}

        # Use a deterministic seed for consistent mappings
        rng = np.random.RandomState(42)

        # Group phonemes by articulatory features for better organization
        phoneme_groups = self._group_phonemes_by_features()

        # Generate vectors with structured initialization
        for group_name, phonemes in phoneme_groups.items():
            # Each group gets a base vector in a different region of frequency space
            group_base = rng.uniform(-1, 1, self.K)
            group_base = group_base / np.linalg.norm(group_base)  # Normalize

            for phoneme in phonemes:
                # Add small perturbations within the group
                perturbation = rng.uniform(-0.3, 0.3, self.K)
                vector = group_base + perturbation
                # Normalize to unit sphere for consistency
                vector = vector / np.linalg.norm(vector)
                self.phoneme_vectors[phoneme] = vector

    def _group_phonemes_by_features(self) -> Dict[str, List[str]]:
        """Group phonemes by articulatory features for structured mapping."""
        groups = {
            'vowels': ['a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'e', 'ai', 'o', 'au'],
            'velar': ['k', 'kh', 'g', 'gh', 'ṅ'],
            'palatal': ['c', 'ch', 'j', 'jh', 'ñ'],
            'retroflex': ['ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ'],
            'dental': ['t', 'th', 'd', 'dh', 'n'],
            'labial': ['p', 'ph', 'b', 'bh', 'm'],
            'semivowels': ['y', 'r', 'l', 'v'],
            'sibilants': ['ś', 'ṣ', 's', 'h'],
            'extra': ['x', 'z', 'f', 'w']
        }
        return groups

    def map_sequence(self, sequence: PhonemeSequence) -> FrequencyPath:
        """
        Map a phoneme sequence to a continuous frequency path.
        """
        vectors = []
        mapping = []

        for i, phoneme in enumerate(sequence.phonemes):
            if phoneme in self.phoneme_vectors:
                vec = self.phoneme_vectors[phoneme]
            else:
                # Fallback for unknown phonemes - use average of nearest known vectors
                # to maintain unit normalization consistency
                if self.phoneme_vectors:
                    avg_vec = np.mean(list(self.phoneme_vectors.values()), axis=0)
                    norm = np.linalg.norm(avg_vec)
                    vec = avg_vec / norm if norm > 0 else np.ones(self.K) / np.sqrt(self.K)
                else:
                    vec = np.ones(self.K) / np.sqrt(self.K)

            vectors.append(vec)
            mapping.append((phoneme, i))

        vectors_array = np.array(vectors)

        # Calculate smoothness score (simple euclidean distance between steps)
        smoothness = 0.0
        if len(vectors_array) > 1:
            diffs = np.diff(vectors_array, axis=0)
            smoothness = np.sum(np.linalg.norm(diffs, axis=1))

        return FrequencyPath(
            vectors=vectors_array,
            smoothness_score=smoothness,
            phoneme_mapping=mapping
        )
