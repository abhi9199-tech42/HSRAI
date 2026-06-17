import numpy as np
import pytest
from urcm.core.resonance_encoder import ResonancePathEncoder
from urcm.core.data_models import FrequencyPath


def _make_frequency_path(seq_len=5, input_dim=24):
    vectors = np.random.default_rng(0).normal(0, 1, (seq_len, input_dim))
    phoneme_mapping = [(f"ph{i}", i) for i in range(seq_len)]
    return FrequencyPath(vectors=vectors, smoothness_score=0.8, phoneme_mapping=phoneme_mapping)


class TestResonancePathEncoderInit:
    def test_default_init(self):
        enc = ResonancePathEncoder()
        assert enc.input_dim == 24
        assert enc.resonance_dim == 64
        assert enc.encoder_type == "recurrent_numpy"

    def test_custom_params(self):
        enc = ResonancePathEncoder(input_dim=16, resonance_dim=32, encoder_type="transformer_stub")
        assert enc.input_dim == 16
        assert enc.resonance_dim == 32
        assert enc.encoder_type == "transformer_stub"

    def test_invalid_encoder_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported encoder type"):
            ResonancePathEncoder(encoder_type="unknown_type")


class TestEncodePath:
    def test_encode_frequency_path_returns_correct_shape(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        fp = _make_frequency_path(seq_len=5, input_dim=24)
        result = enc.encode_path(fp)
        assert result.shape == (64,)

    def test_encode_raw_numpy_array(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        raw = np.random.default_rng(1).normal(0, 1, (4, 24))
        result = enc.encode_path(raw)
        assert result.shape == (64,)

    def test_recurrent_encoder_type(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64, encoder_type="recurrent_numpy")
        fp = _make_frequency_path(seq_len=5, input_dim=24)
        result = enc.encode_path(fp)
        assert result.shape == (64,)

    def test_transformer_encoder_type(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64, encoder_type="transformer_stub")
        fp = _make_frequency_path(seq_len=5, input_dim=24)
        result = enc.encode_path(fp)
        assert result.shape == (64,)

    def test_output_is_finite(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        fp = _make_frequency_path(seq_len=10, input_dim=24)
        result = enc.encode_path(fp)
        assert np.all(np.isfinite(result))

    def test_output_no_nan_inf_recurrent(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64, encoder_type="recurrent_numpy")
        raw = np.random.default_rng(2).normal(0, 5, (8, 24))
        result = enc.encode_path(raw)
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    def test_output_no_nan_inf_transformer(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64, encoder_type="transformer_stub")
        raw = np.random.default_rng(3).normal(0, 5, (8, 24))
        result = enc.encode_path(raw)
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    def test_input_dim_mismatch_raises(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        raw = np.random.default_rng(4).normal(0, 1, (5, 16))
        with pytest.raises(ValueError, match="Input dimension mismatch"):
            enc.encode_path(raw)

    def test_single_step_path(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        fp = _make_frequency_path(seq_len=1, input_dim=24)
        result = enc.encode_path(fp)
        assert result.shape == (64,)

    def test_deterministic_output(self):
        enc = ResonancePathEncoder(input_dim=24, resonance_dim=64)
        fp = _make_frequency_path(seq_len=5, input_dim=24)
        r1 = enc.encode_path(fp)
        r2 = enc.encode_path(fp)
        np.testing.assert_array_equal(r1, r2)
