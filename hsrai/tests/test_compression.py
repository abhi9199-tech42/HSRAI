import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, HealthCheck
from hsrai.compression.mapper import PhonemeFrequencyMapper, PhonemeSequence, FrequencyPath

# --- Strategies ---

@st.composite
def phoneme_sequence_strategy(draw):
    # A simple strategy to generate non-empty lists of phoneme-like strings
    # Limit max_size to avoid slow generation/processing
    phonemes = draw(st.lists(st.text(min_size=1, max_size=3, alphabet="abcdefghijklmnopqrstuvwxyz"), min_size=1, max_size=20))
    source_text = draw(st.text(min_size=1, max_size=50))
    return PhonemeSequence(phonemes=phonemes, source_text=source_text)

# --- Tests ---

class TestPhonemeMapper:
    
    def test_initialization(self):
        # Test valid dimensions
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        assert mapper.K == 24
        
        # Test invalid dimensions
        with pytest.raises(ValueError):
            PhonemeFrequencyMapper(frequency_dim=10)
        with pytest.raises(ValueError):
            PhonemeFrequencyMapper(frequency_dim=40)

    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    @given(phoneme_sequence_strategy())
    def test_mapping_consistency(self, sequence):
        """Property 2: Phoneme mapping determinism"""
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        
        # First pass
        path1 = mapper.map_sequence(sequence)
        
        # Second pass - should be identical
        path2 = mapper.map_sequence(sequence)
        
        # Check shapes
        assert path1.vectors.shape == (len(sequence.phonemes), 24)
        
        # Check determinism
        np.testing.assert_array_equal(path1.vectors, path2.vectors)
        assert path1.smoothness_score == path2.smoothness_score
        assert path1.phoneme_mapping == path2.phoneme_mapping

    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    @given(phoneme_sequence_strategy())
    def test_smoothness_calculation(self, sequence):
        """Verify smoothness score is calculated correctly"""
        mapper = PhonemeFrequencyMapper(frequency_dim=16)
        path = mapper.map_sequence(sequence)
        
        assert path.smoothness_score >= 0.0
        
        # If sequence has length 1, smoothness should be 0
        if len(sequence.phonemes) == 1:
            assert path.smoothness_score == 0.0

    def test_known_phoneme_mapping(self):
        """Ensure Sanskrit phonemes map to consistent non-zero vectors"""
        mapper = PhonemeFrequencyMapper(frequency_dim=32)
        seq = PhonemeSequence(phonemes=['a', 'k', 'u'], source_text="aku")
        path = mapper.map_sequence(seq)
        
        # Check that we didn't get zero vectors (which happens for unknown phonemes in the current fallback)
        # Note: The fallback in the code is np.zeros, but 'a', 'k', 'u' are in SANSKRIT_PHONEMES
        for vec in path.vectors:
            assert np.linalg.norm(vec) > 0.0
            assert np.isclose(np.linalg.norm(vec), 1.0) # Should be normalized

