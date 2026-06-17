import numpy as np
import pytest
from urcm.core.oscillatory_gating import OscillatoryGating


class TestOscillatoryGatingInit:
    def test_default_init(self):
        og = OscillatoryGating()
        assert og.resonance_dim == 64
        assert og.base_frequency == 1.0
        assert og.phase == 0.0

    def test_custom_params(self):
        og = OscillatoryGating(resonance_dim=32, base_frequency=2.5)
        assert og.resonance_dim == 32
        assert og.base_frequency == 2.5

    def test_weight_shapes(self):
        og = OscillatoryGating(resonance_dim=48)
        assert og.W_g.shape == (48, 2)
        assert og.bias.shape == (48,)


class TestGlobalRhythm:
    def test_returns_shape_two(self):
        og = OscillatoryGating()
        g = og.get_global_rhythm()
        assert g.shape == (2,)

    def test_sin_cos_values(self):
        og = OscillatoryGating()
        og.phase = 0.0
        g = og.get_global_rhythm()
        np.testing.assert_allclose(g[0], 0.0, atol=1e-12)
        np.testing.assert_allclose(g[1], 1.0, atol=1e-12)

    def test_at_pi(self):
        og = OscillatoryGating()
        og.phase = np.pi
        g = og.get_global_rhythm()
        np.testing.assert_allclose(g[0], 0.0, atol=1e-12)
        np.testing.assert_allclose(g[1], -1.0, atol=1e-12)


class TestAdvanceTime:
    def test_updates_phase(self):
        og = OscillatoryGating(base_frequency=1.0)
        og.advance_time(0.5)
        expected = 2 * np.pi * 1.0 * 0.5
        np.testing.assert_allclose(og.phase, expected, atol=1e-12)

    def test_phase_wraps_to_2pi(self):
        og = OscillatoryGating(base_frequency=1.0)
        og.advance_time(2.0)
        assert og.phase <= 2 * np.pi

    def test_multiple_advances(self):
        og = OscillatoryGating(base_frequency=1.0)
        for _ in range(3):
            og.advance_time(0.5)
        assert og.phase <= 2 * np.pi
        assert og.phase > 0


class TestResetPhase:
    def test_reset_to_zero(self):
        og = OscillatoryGating()
        og.advance_time(1.0)
        og.reset_phase()
        assert og.phase == 0.0

    def test_reset_to_custom(self):
        og = OscillatoryGating()
        og.reset_phase(np.pi)
        np.testing.assert_allclose(og.phase, np.pi, atol=1e-12)


class TestApplyGating:
    def test_returns_correct_shape(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.ones(64)
        result = og.apply_gating(rv)
        assert result.shape == (64,)

    def test_sigmoid_output_in_0_1(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.ones(64)
        g = og.get_global_rhythm()
        gate_signal = np.dot(og.W_g, g) + og.bias
        sigmoid = 1.0 / (1.0 + np.exp(-gate_signal))
        assert np.all(sigmoid >= 0.0)
        assert np.all(sigmoid <= 1.0)

    def test_gated_output_bounded(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.ones(64)
        result = og.apply_gating(rv)
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)

    def test_wrong_dimension_raises(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.ones(32)
        with pytest.raises(ValueError, match="Input dimension"):
            og.apply_gating(rv)

    def test_with_time_advance(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.ones(64)
        result = og.apply_gating(rv, dt=0.1)
        assert result.shape == (64,)
        assert og.phase > 0

    def test_zero_input_gives_zero_output(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.zeros(64)
        result = og.apply_gating(rv)
        np.testing.assert_array_equal(result, np.zeros(64))

    def test_output_finite(self):
        og = OscillatoryGating(resonance_dim=64)
        rv = np.random.default_rng(0).normal(0, 1, 64)
        result = og.apply_gating(rv)
        assert np.all(np.isfinite(result))
