import pytest
import numpy as np
from dataclasses import replace

from urcm.core.attractor_network import AttractorNetwork
from urcm.core.data_models import AttractorState


@pytest.fixture
def small_network():
    return AttractorNetwork(size=10, coupling_strength=2.0)


@pytest.fixture
def large_network():
    return AttractorNetwork(size=50, coupling_strength=5.0)


class TestInitialization:
    def test_attributes_set(self, small_network):
        assert small_network.N == 10
        assert small_network.K == 2.0

    def test_phases_shape(self, small_network):
        assert small_network.phases.shape == (10,)

    def test_phases_in_range(self, small_network):
        assert np.all(small_network.phases >= 0)
        assert np.all(small_network.phases < 2 * np.pi)

    def test_frequencies_shape(self, small_network):
        assert small_network.frequencies.shape == (10,)

    def test_attractors_empty(self, small_network):
        assert small_network.attractors == []


class TestSetState:
    def test_valid_dimensions(self, small_network):
        new_phases = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
        small_network.set_state(new_phases)
        np.testing.assert_allclose(small_network.phases, new_phases, atol=1e-10)

    def test_wraps_to_2pi(self, small_network):
        new_phases = np.array([0.0, 7.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        small_network.set_state(new_phases)
        assert np.all(small_network.phases < 2 * np.pi)
        assert small_network.phases[1] == pytest.approx(7.0 % (2 * np.pi))

    def test_invalid_dimensions_raises(self, small_network):
        bad_phases = np.array([0.0, 1.0, 2.0])
        with pytest.raises(ValueError, match="does not match network size"):
            small_network.set_state(bad_phases)


class TestStep:
    def test_returns_phases(self, small_network):
        result = small_network.step(dt=0.01)
        assert isinstance(result, np.ndarray)
        assert result.shape == (small_network.N,)

    def test_phases_in_range(self, small_network):
        for _ in range(100):
            small_network.step(dt=0.01)
        assert np.all(small_network.phases >= 0)
        assert np.all(small_network.phases < 2 * np.pi)

    def test_deterministic_given_state(self):
        net1 = AttractorNetwork(size=5, coupling_strength=3.0)
        net2 = AttractorNetwork(size=5, coupling_strength=3.0)
        phases = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        net2.frequencies = net1.frequencies.copy()
        net1.set_state(phases)
        net2.set_state(phases)
        np.testing.assert_array_equal(net1.step(dt=0.01), net2.step(dt=0.01))


class TestOrderParameter:
    def test_returns_float(self, small_network):
        r = small_network.get_order_parameter()
        assert isinstance(r, float)

    def test_in_range(self, small_network):
        r = small_network.get_order_parameter()
        assert 0.0 <= r <= 1.0

    def test_low_for_random_phases(self):
        net = AttractorNetwork(size=200, coupling_strength=0.01)
        rng = np.random.default_rng(99)
        net.phases = rng.uniform(0, 2 * np.pi, 200)
        r = net.get_order_parameter()
        assert r < 0.3

    def test_high_for_synchronized(self, small_network):
        small_network.phases[:] = np.pi / 4
        r = small_network.get_order_parameter()
        assert r > 0.99

    def test_increases_with_coupling(self):
        net_weak = AttractorNetwork(size=30, coupling_strength=0.1)
        net_strong = AttractorNetwork(size=30, coupling_strength=10.0)
        shared_phases = np.random.default_rng(7).uniform(0, 2 * np.pi, 30)
        net_weak.set_state(shared_phases.copy())
        net_strong.set_state(shared_phases.copy())

        for _ in range(200):
            net_weak.step(dt=0.05)
            net_strong.step(dt=0.05)

        assert net_strong.get_order_parameter() > net_weak.get_order_parameter()


class TestStabilityEigenvalues:
    def test_returns_array(self, small_network):
        eigenvalues = small_network.get_stability_eigenvalues()
        assert isinstance(eigenvalues, np.ndarray)

    def test_length_matches_size(self, small_network):
        eigenvalues = small_network.get_stability_eigenvalues()
        assert eigenvalues.shape == (small_network.N,)

    def test_finite(self, small_network):
        eigenvalues = small_network.get_stability_eigenvalues()
        assert np.all(np.isfinite(eigenvalues))


class TestAttractorRegistration:
    def _make_attractor(self, size=10):
        rng = np.random.default_rng(42)
        return AttractorState(
            phase_pattern=rng.uniform(0, 2 * np.pi, size),
            eigenvalues=-rng.uniform(0.1, 1.0, size),
            stability_type="stable",
            semantic_label="test_attractor",
        )

    def test_register_attractor(self, small_network):
        attractor = self._make_attractor()
        small_network.register_attractor(attractor)
        assert len(small_network.attractors) == 1
        assert small_network.attractors[0] is attractor

    def test_find_nearest_attractor_match(self, small_network):
        attractor = self._make_attractor()
        small_network.set_state(attractor.phase_pattern.copy())
        small_network.register_attractor(attractor)
        result = small_network.find_nearest_attractor(phase_threshold=5.0)
        assert result is not None
        assert result.semantic_label == "test_attractor"

    def test_find_nearest_attractor_returns_none_when_no_match(self, small_network):
        rng = np.random.default_rng(1)
        far_attractor = AttractorState(
            phase_pattern=rng.uniform(0, 2 * np.pi, 10),
            eigenvalues=-np.ones(10),
            stability_type="stable",
            semantic_label="far",
        )
        small_network.set_state(np.zeros(10))
        small_network.register_attractor(far_attractor)
        result = small_network.find_nearest_attractor(phase_threshold=0.001)
        assert result is None

    def test_find_nearest_returns_none_no_attractors(self, small_network):
        small_network.phases[:] = 0.0
        result = small_network.find_nearest_attractor()
        assert result is None

    def test_register_multiple(self, small_network):
        for i in range(3):
            small_network.register_attractor(self._make_attractor())
        assert len(small_network.attractors) == 3
