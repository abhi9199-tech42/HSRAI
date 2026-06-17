import pytest
import numpy as np
from dataclasses import replace

from urcm.core.error_handling import ErrorRecoverySystem
from urcm.core.latent_space import SemanticLatentSpace
from urcm.core.attractor_network import AttractorNetwork
from urcm.core.oscillatory_gating import OscillatoryGating
from urcm.core.phoneme_mapper import PhonemeFrequencyMapper
from urcm.core.data_models import ResonanceState, AttractorState


def _make_state(dim=24, mu_val=0.5):
    rho = mu_val * 0.8
    chi = 0.8
    vec = np.ones(dim) * 0.1
    vec /= np.linalg.norm(vec)
    return ResonanceState(
        resonance_vector=vec,
        mu_value=mu_val,
        rho_density=rho,
        chi_cost=chi,
        stability_score=0.9,
        oscillation_phase=1.0,
        timestamp=0.0,
    )


def _make_collapsed_state(dim=24):
    vec = np.zeros(dim)
    vec[0] = 0.05
    rho = 0.05
    chi = 0.1
    return ResonanceState(
        resonance_vector=vec,
        mu_value=rho / (chi + 1e-9),
        rho_density=rho,
        chi_cost=chi,
        stability_score=0.1,
        oscillation_phase=0.0,
        timestamp=0.0,
    )


@pytest.fixture
def components():
    latent_space = SemanticLatentSpace(input_dim=24, latent_dim=8)
    attractor_network = AttractorNetwork(size=24, coupling_strength=2.0)
    gating = OscillatoryGating(resonance_dim=24, base_frequency=1.0)
    phoneme_mapper = PhonemeFrequencyMapper(frequency_dim=24, smoothness_weight=0.1)
    return latent_space, attractor_network, gating, phoneme_mapper


@pytest.fixture
def recovery_system(components):
    latent_space, attractor_network, gating, phoneme_mapper = components
    return ErrorRecoverySystem(
        latent_space=latent_space,
        attractor_network=attractor_network,
        gating_system=gating,
        phoneme_mapper=phoneme_mapper,
    )


class TestCheckAndRecover:
    def test_returns_tuple(self, recovery_system):
        state = _make_state()
        result, actions = recovery_system.check_and_recover(state)
        assert isinstance(result, ResonanceState)
        assert isinstance(actions, list)

    def test_healthy_state_no_actions(self):
        latent_space = SemanticLatentSpace(input_dim=24, latent_dim=24)
        attractor_network = AttractorNetwork(size=24, coupling_strength=2.0)
        gating = OscillatoryGating(resonance_dim=24, base_frequency=1.0)
        phoneme_mapper = PhonemeFrequencyMapper(frequency_dim=24, smoothness_weight=0.1)
        attractor_network.phases = np.ones(24) * np.pi / 4
        rs = ErrorRecoverySystem(
            latent_space=latent_space,
            attractor_network=attractor_network,
            gating_system=gating,
            phoneme_mapper=phoneme_mapper,
        )
        state = _make_state()
        result, actions = rs.check_and_recover(state)
        assert "PhaseReset" not in actions


class TestCollapseDetection:
    def test_low_norm_triggers_recovery(self, recovery_system):
        collapsed = _make_collapsed_state()
        _, actions = recovery_system.check_and_recover(collapsed)
        assert "ReconstructionAnchoring" in actions or "CollapseRecoveryFailed" in actions

    def test_healthy_norm_no_collapse_action(self, recovery_system):
        net = recovery_system.attractor_network
        net.phases = np.ones(24) * 0.5
        state = _make_state()
        _, actions = recovery_system.check_and_recover(state)
        assert "ReconstructionAnchoring" not in actions


class TestDesyncDetection:
    def test_low_order_parameter_triggers_phase_reset(self, recovery_system):
        net = recovery_system.attractor_network
        rng = np.random.default_rng(42)
        net.phases = rng.uniform(0, 2 * np.pi, 24)
        r = net.get_order_parameter()
        if r < 0.3:
            state = _make_state()
            _, actions = recovery_system.check_and_recover(state)
            assert "PhaseReset" in actions

    def test_high_order_parameter_no_reset(self, recovery_system):
        net = recovery_system.attractor_network
        net.phases = np.ones(24) * np.pi
        r = net.get_order_parameter()
        if r >= 0.3:
            state = _make_state()
            _, actions = recovery_system.check_and_recover(state)
            assert "PhaseReset" not in actions


class TestErrorLogging:
    def test_errors_logged(self, recovery_system):
        collapsed = _make_collapsed_state()
        recovery_system.check_and_recover(collapsed)
        assert len(recovery_system.error_log) > 0

    def test_log_entries_have_expected_keys(self, recovery_system):
        collapsed = _make_collapsed_state()
        recovery_system.check_and_recover(collapsed)
        entry = recovery_system.error_log[0]
        assert "type" in entry
        assert "message" in entry
        assert "timestamp" in entry
