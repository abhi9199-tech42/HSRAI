import pytest
import numpy as np
import time

from urcm.core.validation import DataValidation
from urcm.core.data_models import (
    ResonanceState, AttractorState, ReasoningPath, MeshSignal
)
from hsrai.common.phoneme import PhonemeSequence, FrequencyPath


def _make_resonance(vector=None, mu=1.0, rho=1.0, chi=1.0, phase=1.0):
    vec = vector if vector is not None else np.ones(24)
    calculated_mu = rho / (chi + 1e-9)
    return ResonanceState(
        resonance_vector=vec,
        mu_value=calculated_mu,
        rho_density=rho,
        chi_cost=chi,
        stability_score=0.5,
        oscillation_phase=phase,
        timestamp=time.time(),
    )


def _bypass_resonance_state(vector, mu_value=np.nan, rho=1.0, chi=1.0,
                            phase=1.0, stability=0.5, ts=1.0):
    """Create a ResonanceState bypassing __post_init__ validation."""
    obj = ResonanceState.__new__(ResonanceState)
    obj.resonance_vector = vector
    obj.mu_value = mu_value
    obj.rho_density = rho
    obj.chi_cost = chi
    obj.stability_score = stability
    obj.oscillation_phase = phase
    obj.timestamp = ts
    return obj


def _bypass_frequency_path(vectors, smoothness=0.8, mapping=None):
    """Create a FrequencyPath bypassing __post_init__ validation."""
    obj = FrequencyPath.__new__(FrequencyPath)
    obj.vectors = vectors
    obj.smoothness_score = smoothness
    obj.phoneme_mapping = mapping or [("a", i) for i in range(vectors.shape[0])]
    return obj


# ── PhonemeSequence ──────────────────────────────────────────────────

class TestValidatePhonemeSequence:
    def test_valid(self):
        seq = PhonemeSequence(phonemes=["a", "k", "t"], source_text="akt")
        assert DataValidation.validate_phoneme_sequence(seq) is True

    def test_empty_phonemes(self):
        seq = PhonemeSequence.__new__(PhonemeSequence)
        seq.phonemes = []
        seq.source_text = "test"
        seq.language_hint = None
        assert DataValidation.validate_phoneme_sequence(seq) is False

    def test_empty_source_text(self):
        seq = PhonemeSequence.__new__(PhonemeSequence)
        seq.phonemes = ["a"]
        seq.source_text = ""
        seq.language_hint = None
        assert DataValidation.validate_phoneme_sequence(seq) is False

    def test_whitespace_source_text(self):
        seq = PhonemeSequence.__new__(PhonemeSequence)
        seq.phonemes = ["a"]
        seq.source_text = "   "
        seq.language_hint = None
        assert DataValidation.validate_phoneme_sequence(seq) is False

    def test_invalid_language_hint_type(self):
        seq = PhonemeSequence.__new__(PhonemeSequence)
        seq.phonemes = ["a"]
        seq.source_text = "a"
        seq.language_hint = 123
        assert DataValidation.validate_phoneme_sequence(seq) is False

    def test_none_language_hint(self):
        seq = PhonemeSequence(phonemes=["a"], source_text="a", language_hint=None)
        assert DataValidation.validate_phoneme_sequence(seq) is True


# ── FrequencyPath ────────────────────────────────────────────────────

class TestValidateFrequencyPath:
    def _make_path(self, rows=3, cols=24):
        vectors = np.random.randn(rows, cols)
        mapping = [("a", i) for i in range(rows)]
        return FrequencyPath(vectors=vectors, smoothness_score=0.8, phoneme_mapping=mapping)

    def test_valid(self):
        path = self._make_path()
        assert DataValidation.validate_frequency_path(path) is True

    def test_invalid_ndim(self):
        path = self._make_path()
        path.vectors = np.ones(24)
        assert DataValidation.validate_frequency_path(path) is False

    def test_dimension_too_small(self):
        vectors = np.ones((3, 10))
        mapping = [("a", i) for i in range(3)]
        path = _bypass_frequency_path(vectors, smoothness=0.5, mapping=mapping)
        assert DataValidation.validate_frequency_path(path) is False

    def test_dimension_too_large(self):
        vectors = np.ones((3, 40))
        mapping = [("a", i) for i in range(3)]
        path = _bypass_frequency_path(vectors, smoothness=0.5, mapping=mapping)
        assert DataValidation.validate_frequency_path(path) is False

    def test_negative_smoothness(self):
        path = self._make_path()
        path.smoothness_score = -1.0
        assert DataValidation.validate_frequency_path(path) is False

    def test_phoneme_mapping_length_mismatch(self):
        path = self._make_path(rows=3)
        path.phoneme_mapping = [("a", 0)]
        assert DataValidation.validate_frequency_path(path) is False


# ── ResonanceState ──────────────────────────────────────────────────

class TestValidateResonanceState:
    def test_valid(self):
        state = _make_resonance()
        assert DataValidation.validate_resonance_state(state) is True

    def test_invalid_vector_ndim(self):
        vec = np.ones((4, 4))
        state = _bypass_resonance_state(vector=vec)
        assert DataValidation.validate_resonance_state(state) is False

    def test_nan_in_vector(self):
        vec = np.ones(24)
        vec[5] = np.nan
        state = _make_resonance(vector=vec)
        assert DataValidation.validate_resonance_state(state) is False

    def test_inf_in_vector(self):
        vec = np.ones(24)
        vec[0] = np.inf
        state = _make_resonance(vector=vec)
        assert DataValidation.validate_resonance_state(state) is False

    def test_nan_mu(self):
        state = _make_resonance()
        state.mu_value = np.nan
        assert DataValidation.validate_resonance_state(state) is False

    def test_phase_out_of_range(self):
        state = _make_resonance()
        state.oscillation_phase = 10.0
        assert DataValidation.validate_resonance_state(state) is False

    def test_negative_timestamp(self):
        state = _make_resonance()
        state.timestamp = -1.0
        assert DataValidation.validate_resonance_state(state) is False

    def test_rho_out_of_range(self):
        state = _make_resonance()
        state.rho_density = 2.0
        assert DataValidation.validate_resonance_state(state) is False

    def test_negative_chi(self):
        state = _make_resonance()
        state.chi_cost = -1.0
        assert DataValidation.validate_resonance_state(state) is False


# ── AttractorState ──────────────────────────────────────────────────

class TestValidateAttractorState:
    def _make_attractor(self, stability="stable", dim=24):
        if stability == "stable":
            eigenvalues = np.full(dim, -1.0)
        elif stability == "unstable":
            eigenvalues = np.full(dim, 1.0)
        else:
            eigenvalues = np.concatenate([np.full(dim // 2, -1.0), np.full(dim - dim // 2, 1.0)])
        phases = np.linspace(0, 2 * np.pi, dim)
        return AttractorState(
            phase_pattern=phases, eigenvalues=eigenvalues, stability_type=stability
        )

    def test_valid_stable(self):
        attr = self._make_attractor("stable")
        assert DataValidation.validate_attractor_state(attr) is True

    def test_valid_unstable(self):
        attr = self._make_attractor("unstable")
        assert DataValidation.validate_attractor_state(attr) is True

    def test_valid_saddle(self):
        attr = self._make_attractor("saddle")
        assert DataValidation.validate_attractor_state(attr) is True

    def test_invalid_stability_type(self):
        attr = self._make_attractor("stable")
        attr.stability_type = "invalid"
        assert DataValidation.validate_attractor_state(attr) is False

    def test_phase_out_of_range(self):
        attr = self._make_attractor("stable")
        attr.phase_pattern[0] = -0.1
        assert DataValidation.validate_attractor_state(attr) is False

    def test_phase_exceeds_2pi(self):
        attr = self._make_attractor("stable")
        attr.phase_pattern[0] = 2 * np.pi + 0.1
        assert DataValidation.validate_attractor_state(attr) is False

    def test_nan_eigenvalues(self):
        attr = self._make_attractor("stable")
        attr.eigenvalues[0] = np.nan
        assert DataValidation.validate_attractor_state(attr) is False

    def test_eigenvalue_inconsistency_with_stable(self):
        attr = self._make_attractor("stable")
        attr.eigenvalues[0] = 1.0
        assert DataValidation.validate_attractor_state(attr) is False


# ── ReasoningPath ───────────────────────────────────────────────────

class TestValidateReasoningPath:
    def _make_path(self, intermediates=2, converged=True):
        initial = _make_resonance(vector=np.ones(24))
        intermediates_list = [_make_resonance(vector=np.ones(24)) for _ in range(intermediates)]
        final = _make_resonance(vector=np.ones(24))
        mu_traj = [1.0] * (intermediates + 2)
        return ReasoningPath(
            initial_state=initial,
            intermediate_states=intermediates_list,
            final_state=final,
            mu_trajectory=mu_traj,
            convergence_achieved=converged,
            termination_reason="converged",
        )

    def test_valid(self):
        path = self._make_path()
        assert DataValidation.validate_reasoning_path(path) is True

    def test_empty_intermediates(self):
        path = self._make_path(intermediates=0)
        assert DataValidation.validate_reasoning_path(path) is True

    def test_trajectory_length_mismatch(self):
        path = self._make_path(intermediates=2)
        path.mu_trajectory = [1.0, 2.0]
        assert DataValidation.validate_reasoning_path(path) is False

    def test_convergence_but_large_delta(self):
        path = self._make_path(intermediates=1, converged=True)
        path.mu_trajectory = [1.0, 5.0, 1.0]
        assert DataValidation.validate_reasoning_path(path) is False

    def test_empty_termination_reason(self):
        path = self._make_path()
        path.termination_reason = ""
        assert DataValidation.validate_reasoning_path(path) is False

    def test_invalid_initial_state(self):
        path = self._make_path()
        path.initial_state.mu_value = np.nan
        assert DataValidation.validate_reasoning_path(path) is False


# ── MeshSignal ──────────────────────────────────────────────────────

class TestValidateMeshSignal:
    def _make_signal(self, signal_type="sync"):
        return MeshSignal(
            sender_id="node_1",
            delta_mu=0.5,
            phase_alignment=1.0,
            timestamp=time.time(),
            signal_type=signal_type,
        )

    def test_valid_sync(self):
        assert DataValidation.validate_mesh_signal(self._make_signal("sync")) is True

    def test_valid_convergence(self):
        assert DataValidation.validate_mesh_signal(self._make_signal("convergence")) is True

    def test_valid_error(self):
        assert DataValidation.validate_mesh_signal(self._make_signal("error")) is True

    def test_invalid_sender_id(self):
        sig = self._make_signal()
        sig.sender_id = ""
        assert DataValidation.validate_mesh_signal(sig) is False

    def test_invalid_signal_type(self):
        sig = self._make_signal()
        sig.signal_type = "unknown"
        assert DataValidation.validate_mesh_signal(sig) is False

    def test_nan_delta_mu(self):
        sig = self._make_signal()
        sig.delta_mu = np.nan
        assert DataValidation.validate_mesh_signal(sig) is False

    def test_phase_out_of_range(self):
        sig = self._make_signal()
        sig.phase_alignment = 10.0
        assert DataValidation.validate_mesh_signal(sig) is False

    def test_negative_timestamp(self):
        sig = self._make_signal()
        sig.timestamp = -1.0
        assert DataValidation.validate_mesh_signal(sig) is False


# ── Mu Value ────────────────────────────────────────────────────────

class TestValidateMuValue:
    def test_positive(self):
        assert DataValidation.validate_mu_value(1.0) is True

    def test_large_positive(self):
        assert DataValidation.validate_mu_value(1e6) is True

    def test_zero(self):
        assert DataValidation.validate_mu_value(0.0) is False

    def test_negative(self):
        assert DataValidation.validate_mu_value(-1.0) is False

    def test_nan(self):
        assert DataValidation.validate_mu_value(np.nan) is False

    def test_inf(self):
        assert DataValidation.validate_mu_value(np.inf) is False

    def test_string(self):
        assert DataValidation.validate_mu_value("1.0") is False
