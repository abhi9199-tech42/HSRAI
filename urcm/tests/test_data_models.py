import pytest
import numpy as np
from urcm.core.data_models import (
    ResonanceState,
    AttractorState,
    ReasoningPath,
    MeshSignal,
)
from hsrai.common.phoneme import PhonemeSequence, FrequencyPath


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_resonance(vector_dim: int = 8, mu: float = None, rho: float = 1.0,
                     chi: float = 0.001, phase: float = 0.0, ts: float = 0.0):
    v = np.random.RandomState(0).randn(vector_dim)
    if mu is None:
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


# ===========================================================================
# PhonemeSequence
# ===========================================================================

class TestPhonemeSequence:
    def test_valid_construction(self):
        ps = PhonemeSequence(phonemes=["a", "k", "t"], source_text="akt")
        assert ps.phonemes == ["a", "k", "t"]

    def test_empty_phonemes_raises(self):
        with pytest.raises(ValueError, match="empty"):
            PhonemeSequence(phonemes=[], source_text="x")

    def test_empty_source_text_raises(self):
        with pytest.raises(ValueError, match="empty"):
            PhonemeSequence(phonemes=["a"], source_text="")


# ===========================================================================
# FrequencyPath
# ===========================================================================

class TestFrequencyPath:
    def test_valid_construction(self):
        vecs = np.random.randn(3, 24)
        fp = FrequencyPath(vectors=vecs, smoothness_score=0.1,
                           phoneme_mapping=[("a", 0), ("k", 1), ("t", 2)])
        assert fp.vectors.shape == (3, 24)

    def test_wrong_ndim_raises(self):
        vecs = np.random.randn(24)
        with pytest.raises(ValueError, match="2-dimensional"):
            FrequencyPath(vectors=vecs, smoothness_score=0.0,
                          phoneme_mapping=[("a", 0)])

    def test_dimension_out_of_range(self):
        vecs = np.random.randn(1, 10)
        with pytest.raises(ValueError, match="range"):
            FrequencyPath(vectors=vecs, smoothness_score=0.0,
                          phoneme_mapping=[("a", 0)])

    def test_negative_smoothness(self):
        vecs = np.random.randn(1, 20)
        with pytest.raises(ValueError, match="non-negative"):
            FrequencyPath(vectors=vecs, smoothness_score=-1.0,
                          phoneme_mapping=[("a", 0)])

    def test_mapping_length_mismatch(self):
        vecs = np.random.randn(3, 20)
        with pytest.raises(ValueError, match="length"):
            FrequencyPath(vectors=vecs, smoothness_score=0.0,
                          phoneme_mapping=[("a", 0)])


# ===========================================================================
# ResonanceState
# ===========================================================================

class TestResonanceState:
    def test_valid_construction(self):
        rs = _make_resonance()
        assert rs.resonance_vector.ndim == 1

    def test_invalid_vector_ndim(self):
        v = np.ones((2, 2))
        mu = 1.0 / (0.001 + 1e-9)
        with pytest.raises(ValueError, match="1-dimensional"):
            ResonanceState(resonance_vector=v, mu_value=mu,
                           rho_density=1.0, chi_cost=0.001,
                           stability_score=0.5, oscillation_phase=0.0,
                           timestamp=0.0)

    def test_invalid_phase_too_large(self):
        v = np.ones(4)
        mu = 1.0 / (0.001 + 1e-9)
        with pytest.raises(ValueError, match="phase"):
            ResonanceState(resonance_vector=v, mu_value=mu,
                           rho_density=1.0, chi_cost=0.001,
                           stability_score=0.5, oscillation_phase=10.0,
                           timestamp=0.0)

    def test_invalid_phase_negative(self):
        v = np.ones(4)
        mu = 1.0 / (0.001 + 1e-9)
        with pytest.raises(ValueError, match="phase"):
            ResonanceState(resonance_vector=v, mu_value=mu,
                           rho_density=1.0, chi_cost=0.001,
                           stability_score=0.5, oscillation_phase=-1.0,
                           timestamp=0.0)

    def test_negative_timestamp(self):
        v = np.ones(4)
        mu = 1.0 / (0.001 + 1e-9)
        with pytest.raises(ValueError, match="Timestamp"):
            ResonanceState(resonance_vector=v, mu_value=mu,
                           rho_density=1.0, chi_cost=0.001,
                           stability_score=0.5, oscillation_phase=0.0,
                           timestamp=-5.0)

    def test_mu_invariant_mismatch(self):
        v = np.ones(4)
        wrong_mu = 0.001
        with pytest.raises(ValueError, match="mu_value"):
            ResonanceState(resonance_vector=v, mu_value=wrong_mu,
                           rho_density=1.0, chi_cost=0.001,
                           stability_score=0.5, oscillation_phase=0.0,
                           timestamp=0.0)


# ===========================================================================
# AttractorState
# ===========================================================================

class TestAttractorState:
    def test_valid_construction(self):
        a = AttractorState(
            phase_pattern=np.ones(8),
            eigenvalues=np.ones(8),
            stability_type="stable",
            semantic_label="test",
        )
        assert a.stability_type == "stable"

    def test_invalid_phase_ndim(self):
        with pytest.raises(ValueError, match="1-dimensional"):
            AttractorState(
                phase_pattern=np.ones((2, 2)),
                eigenvalues=np.ones(4),
                stability_type="stable",
            )

    def test_invalid_eigenvalues_ndim(self):
        with pytest.raises(ValueError, match="1-dimensional"):
            AttractorState(
                phase_pattern=np.ones(4),
                eigenvalues=np.ones((2, 2)),
                stability_type="stable",
            )

    def test_invalid_stability_type(self):
        with pytest.raises(ValueError, match="Stability type"):
            AttractorState(
                phase_pattern=np.ones(4),
                eigenvalues=np.ones(4),
                stability_type="weird",
            )


# ===========================================================================
# ReasoningPath
# ===========================================================================

class TestReasoningPath:
    def test_valid_construction(self):
        s0 = _make_resonance(ts=0.0)
        s1 = _make_resonance(ts=1.0)
        s2 = _make_resonance(ts=2.0)
        rp = ReasoningPath(
            initial_state=s0,
            intermediate_states=[s1],
            final_state=s2,
            mu_trajectory=[s0.mu_value, s1.mu_value, s2.mu_value],
            convergence_achieved=True,
            termination_reason="converged",
        )
        assert rp.convergence_achieved

    def test_trajectory_length_mismatch(self):
        s0 = _make_resonance(ts=0.0)
        s2 = _make_resonance(ts=2.0)
        with pytest.raises(ValueError, match="trajectory"):
            ReasoningPath(
                initial_state=s0,
                intermediate_states=[],
                final_state=s2,
                mu_trajectory=[1.0],  # wrong length
                convergence_achieved=False,
                termination_reason="timeout",
            )

    def test_empty_termination_reason(self):
        s0 = _make_resonance(ts=0.0)
        s2 = _make_resonance(ts=1.0)
        with pytest.raises(ValueError, match="Termination reason"):
            ReasoningPath(
                initial_state=s0,
                intermediate_states=[],
                final_state=s2,
                mu_trajectory=[s0.mu_value, s2.mu_value],
                convergence_achieved=False,
                termination_reason="",
            )


# ===========================================================================
# MeshSignal
# ===========================================================================

class TestMeshSignal:
    def test_valid_construction(self):
        ms = MeshSignal(sender_id="node1", delta_mu=0.1,
                        phase_alignment=1.0, timestamp=0.0,
                        signal_type="sync")
        assert ms.sender_id == "node1"

    def test_empty_sender(self):
        with pytest.raises(ValueError, match="Sender ID"):
            MeshSignal(sender_id="", delta_mu=0.0,
                       phase_alignment=0.0, timestamp=0.0,
                       signal_type="sync")

    def test_invalid_signal_type(self):
        with pytest.raises(ValueError, match="Signal type"):
            MeshSignal(sender_id="n1", delta_mu=0.0,
                       phase_alignment=0.0, timestamp=0.0,
                       signal_type="invalid")

    def test_invalid_phase_alignment(self):
        with pytest.raises(ValueError, match="Phase alignment"):
            MeshSignal(sender_id="n1", delta_mu=0.0,
                       phase_alignment=10.0, timestamp=0.0,
                       signal_type="sync")

    def test_negative_timestamp(self):
        with pytest.raises(ValueError, match="Timestamp"):
            MeshSignal(sender_id="n1", delta_mu=0.0,
                       phase_alignment=0.0, timestamp=-1.0,
                       signal_type="sync")
