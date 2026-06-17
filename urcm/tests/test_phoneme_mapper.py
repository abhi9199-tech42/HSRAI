import pytest
import numpy as np
from urcm.core.phoneme_mapper import (
    PhonemeFrequencyMapper,
    TextToPhonemeConverter,
    PhonemeFrequencyPipeline,
)


# ===========================================================================
# PhonemeFrequencyMapper
# ===========================================================================

class TestPhonemeFrequencyMapper:
    def test_valid_init(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        assert mapper.K == 24

    def test_dimension_too_low(self):
        with pytest.raises(ValueError, match="range"):
            PhonemeFrequencyMapper(frequency_dim=8)

    def test_dimension_too_high(self):
        with pytest.raises(ValueError, match="range"):
            PhonemeFrequencyMapper(frequency_dim=64)

    def test_map_phoneme_returns_correct_dim(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=20)
        vec = mapper.map_phoneme("a")
        assert vec.shape == (20,)

    def test_all_known_phonemes_nonzero(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        for phoneme in mapper.SANSKRIT_PHONEMES:
            vec = mapper.map_phoneme(phoneme)
            assert np.linalg.norm(vec) > 0, f"Phoneme '{phoneme}' maps to zero vector"

    def test_deterministic_mapping(self):
        m1 = PhonemeFrequencyMapper(frequency_dim=24)
        m2 = PhonemeFrequencyMapper(frequency_dim=24)
        v1 = m1.map_phoneme("k")
        v2 = m2.map_phoneme("k")
        np.testing.assert_array_equal(v1, v2)

    def test_unknown_phoneme_raises(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        with pytest.raises(ValueError, match="not in Sanskrit"):
            mapper.map_phoneme("q")

    def test_map_sequence_returns_2d(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        path = mapper.map_sequence(["a", "k", "t"])
        assert path.ndim == 2
        assert path.shape == (3, 24)

    def test_map_sequence_empty_raises(self):
        mapper = PhonemeFrequencyMapper(frequency_dim=24)
        with pytest.raises(ValueError, match="empty"):
            mapper.map_sequence([])


# ===========================================================================
# TextToPhonemeConverter
# ===========================================================================

class TestTextToPhonemeConverter:
    def test_valid_conversion(self):
        conv = TextToPhonemeConverter()
        ps = conv.convert_text_to_phonemes("cat")
        assert len(ps.phonemes) > 0

    def test_empty_text_raises(self):
        conv = TextToPhonemeConverter()
        with pytest.raises(ValueError, match="empty"):
            conv.convert_text_to_phonemes("")

    def test_whitespace_only_raises(self):
        conv = TextToPhonemeConverter()
        with pytest.raises(ValueError, match="empty"):
            conv.convert_text_to_phonemes("   ")


# ===========================================================================
# PhonemeFrequencyPipeline
# ===========================================================================

class TestPhonemeFrequencyPipeline:
    def test_pipeline_text_to_frequency(self):
        pipe = PhonemeFrequencyPipeline(frequency_dim=24)
        fp = pipe.process_text("hello")
        assert fp.vectors.ndim == 2
        assert fp.vectors.shape[1] == 24
        assert len(fp.phoneme_mapping) == fp.vectors.shape[0]

    def test_pipeline_deterministic(self):
        p1 = PhonemeFrequencyPipeline(frequency_dim=24)
        p2 = PhonemeFrequencyPipeline(frequency_dim=24)
        fp1 = p1.process_text("test")
        fp2 = p2.process_text("test")
        np.testing.assert_array_equal(fp1.vectors, fp2.vectors)

    def test_pipeline_empty_text_raises(self):
        pipe = PhonemeFrequencyPipeline()
        with pytest.raises(ValueError, match="empty"):
            pipe.process_text("")

    def test_pipeline_single_char(self):
        pipe = PhonemeFrequencyPipeline(frequency_dim=20)
        fp = pipe.process_text("a")
        assert fp.vectors.shape[0] >= 1
        assert fp.vectors.shape[1] == 20
