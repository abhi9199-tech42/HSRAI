import numpy as np
import pytest

from urcm.core.data_models import AttractorState, ResonanceState
from urcm.core.theory import ResonantLearning, URCMTheory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_resonance(dim: int = 16, rho: float = 1.0, chi: float = 0.001,
                     phase: float = 0.0, ts: float = 0.0):
    v = np.random.RandomState(0).randn(dim)
    mu = rho / (chi + 1e-9)
    return ResonanceState(
        resonance_vector=v,
        mu_value=mu,
        rho_density=rho,
        chi_cost=chi,
        stability_score=0.5,
        oscillation_phase=phase,
        timestamp=ts,
    )


def _make_attractor(dim: int = 16):
    pp = np.random.RandomState(1).randn(dim)
    pp = pp / np.linalg.norm(pp)
    ev = np.abs(np.random.RandomState(2).randn(dim))
    return AttractorState(
        phase_pattern=pp,
        eigenvalues=ev,
        stability_type="stable",
        semantic_label="test",
    )


# ===========================================================================
# URCMTheory.calculate_rho
# ===========================================================================

class TestCalculateRho:
    def test_uniform_vector_low_rho(self):
        vec = np.ones(16)
        rho = URCMTheory.calculate_rho(vec)
        assert rho < 0.1, f"Uniform vector should have low rho, got {rho}"

    def test_focused_vector_high_rho(self):
        vec = np.zeros(16)
        vec[0] = 10.0
        rho = URCMTheory.calculate_rho(vec)
        assert rho > 0.9, f"Focused vector should have high rho, got {rho}"

    def test_rho_in_unit_interval(self):
        rng = np.random.RandomState(42)
        for _ in range(20):
            vec = rng.randn(16)
            rho = URCMTheory.calculate_rho(vec)
            assert 0.0 <= rho <= 1.0, f"rho={rho} out of [0,1]"


# ===========================================================================
# URCMTheory.calculate_chi
# ===========================================================================

class TestCalculateChi:
    def test_same_vector_zero_cost(self):
        v = np.ones(16) * 3.0
        chi = URCMTheory.calculate_chi(v, v)
        assert chi == pytest.approx(0.0, abs=1e-9)

    def test_different_vectors_positive_cost(self):
        a = np.zeros(16)
        b = np.ones(16)
        chi = URCMTheory.calculate_chi(a, b)
        assert chi > 0

    def test_chi_non_negative(self):
        rng = np.random.RandomState(7)
        for _ in range(20):
            a = rng.randn(16)
            b = rng.randn(16)
            chi = URCMTheory.calculate_chi(a, b)
            assert chi >= 0


# ===========================================================================
# URCMTheory.compute_mu
# ===========================================================================

class TestComputeMu:
    def test_basic_formula(self):
        rho, chi = 1.0, 0.0
        mu = URCMTheory.compute_mu(rho, chi)
        expected = rho / (chi + 1e-6)
        assert mu == pytest.approx(expected, rel=1e-6)

    def test_mu_positive_when_rho_positive(self):
        mu = URCMTheory.compute_mu(0.5, 0.1)
        assert mu > 0

    def test_mu_zero_when_rho_zero(self):
        mu = URCMTheory.compute_mu(0.0, 1.0)
        assert mu == pytest.approx(0.0, abs=1e-9)


# ===========================================================================
# ResonantLearning.update_attractor
# ===========================================================================

class TestResonantLearning:
    def test_attractor_moves_toward_high_mu(self):
        dim = 16
        attractor = _make_attractor(dim)
        initial_pattern = attractor.phase_pattern.copy()

        rs = _make_resonance(dim=dim, rho=10.0, chi=0.001)
        rl = ResonantLearning(learning_rate=0.1)
        new_attractor = rl.update_attractor(attractor, rs)

        # The pattern should have moved
        assert not np.allclose(new_attractor.phase_pattern, initial_pattern), \
            "Attractor pattern should change after update"

    def test_attractor_stays_normalized(self):
        dim = 16
        attractor = _make_attractor(dim)
        rs = _make_resonance(dim=dim, rho=5.0, chi=0.01)
        rl = ResonantLearning(learning_rate=0.05)
        new_attractor = rl.update_attractor(attractor, rs)
        norm = np.linalg.norm(new_attractor.phase_pattern)
        assert norm == pytest.approx(1.0, abs=1e-5), \
            f"Attractor pattern should be unit-norm, got {norm}"

    def test_eigenvalues_increase_with_high_mu(self):
        dim = 16
        attractor = _make_attractor(dim)
        initial_eigs = attractor.eigenvalues.copy()
        rs = _make_resonance(dim=dim, rho=100.0, chi=0.0001)
        rl = ResonantLearning(learning_rate=0.1)
        new_attractor = rl.update_attractor(attractor, rs)
        assert np.all(new_attractor.eigenvalues >= initial_eigs), \
            "Eigenvalues should increase with high-mu input"

    def test_stability_type_preserved(self):
        dim = 16
        attractor = _make_attractor(dim)
        rs = _make_resonance(dim=dim)
        rl = ResonantLearning()
        new_attractor = rl.update_attractor(attractor, rs)
        assert new_attractor.stability_type == attractor.stability_type
