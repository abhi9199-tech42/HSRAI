import time

import numpy as np

from urcm.core.convergence_engine import MuConvergenceEngine
from urcm.core.data_models import ReasoningPath, ResonanceState
from urcm.core.theory import URCMTheory


def _make_resonance_state(dim=64, seed=0):
    rng = np.random.default_rng(seed)
    rv = rng.normal(0, 0.1, dim)
    rho = URCMTheory.calculate_rho(rv)
    chi = np.linalg.norm(rv)
    mu = URCMTheory.compute_mu(rho, chi)
    return ResonanceState(
        resonance_vector=rv,
        mu_value=mu,
        rho_density=rho,
        chi_cost=chi,
        stability_score=mu,
        oscillation_phase=0.0,
        timestamp=time.time(),
    )


class TestMuConvergenceEngineInit:
    def test_default_init(self):
        eng = MuConvergenceEngine()
        assert eng.rho_threshold == 0.5
        assert eng.convergence_epsilon == 1e-3
        assert eng.max_steps == 50
        assert eng.beam_width == 3

    def test_custom_init(self):
        eng = MuConvergenceEngine(
            rho_threshold=0.8,
            convergence_epsilon=1e-4,
            max_steps=100,
            competition_beam_width=5,
        )
        assert eng.rho_threshold == 0.8
        assert eng.convergence_epsilon == 1e-4
        assert eng.max_steps == 100
        assert eng.beam_width == 5


class TestCalculateStateMetrics:
    def test_zero_rho_chi_gets_computed(self):
        state = _make_resonance_state()
        raw_state = ResonanceState(
            resonance_vector=state.resonance_vector,
            mu_value=0.0,
            rho_density=0.0,
            chi_cost=0.0,
            stability_score=0.0,
            oscillation_phase=0.0,
            timestamp=0.0,
        )
        eng = MuConvergenceEngine()
        result = eng.calculate_state_metrics(raw_state)
        assert result.rho_density > 0
        assert result.chi_cost > 0
        assert result.mu_value > 0

    def test_already_computed_state_unchanged(self):
        state = _make_resonance_state()
        eng = MuConvergenceEngine()
        result = eng.calculate_state_metrics(state)
        np.testing.assert_array_equal(result.resonance_vector, state.resonance_vector)
        assert result.mu_value == state.mu_value


class TestRunReasoningLoop:
    def test_returns_list_of_reasoning_paths(self):
        eng = MuConvergenceEngine(max_steps=10)
        init_state = _make_resonance_state(seed=42)

        def next_gen(state):
            return [_make_resonance_state(seed=int(state.resonance_vector[0] * 1000) % 1000 + 1)]

        paths = eng.run_reasoning_loop(init_state, next_gen)
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert all(isinstance(p, ReasoningPath) for p in paths)

    def test_convergence_achieved_or_max_steps(self):
        eng = MuConvergenceEngine(max_steps=5)
        init_state = _make_resonance_state(seed=10)

        def next_gen(state):
            return [_make_resonance_state(seed=77)]

        paths = eng.run_reasoning_loop(init_state, next_gen)
        assert len(paths) > 0
        p = paths[0]
        assert p.convergence_achieved or p.termination_reason == "Max Steps Reached"

    def test_mu_trajectory_non_empty(self):
        eng = MuConvergenceEngine(max_steps=5)
        init_state = _make_resonance_state(seed=20)
        counter = [0]

        def next_gen(state):
            counter[0] += 1
            return [_make_resonance_state(seed=counter[0] + 100)]

        paths = eng.run_reasoning_loop(init_state, next_gen)
        for p in paths:
            assert len(p.mu_trajectory) > 0

    def test_dead_end_terminates_path(self):
        eng = MuConvergenceEngine(max_steps=10)
        init_state = _make_resonance_state(seed=5)

        def next_gen(state):
            return []

        paths = eng.run_reasoning_loop(init_state, next_gen)
        assert len(paths) == 1
        assert "Dead End" in paths[0].termination_reason

    def test_multiple_candidates_compete(self):
        eng = MuConvergenceEngine(max_steps=3, competition_beam_width=2)
        init_state = _make_resonance_state(seed=1)
        counter = [0]

        def next_gen(state):
            counter[0] += 1
            return [
                _make_resonance_state(seed=counter[0] * 2),
                _make_resonance_state(seed=counter[0] * 2 + 1),
            ]

        paths = eng.run_reasoning_loop(init_state, next_gen)
        assert len(paths) > 0

    def test_all_paths_have_valid_structure(self):
        eng = MuConvergenceEngine(max_steps=4)
        init_state = _make_resonance_state(seed=3)
        counter = [0]

        def next_gen(state):
            counter[0] += 1
            return [_make_resonance_state(seed=counter[0] + 200)]

        paths = eng.run_reasoning_loop(init_state, next_gen)
        for p in paths:
            assert p.initial_state is not None
            assert p.final_state is not None
            assert isinstance(p.mu_trajectory, list)
            assert p.termination_reason != ""


class TestEvaluatePaths:
    def test_sorts_by_mu(self):
        eng = MuConvergenceEngine(competition_beam_width=2)
        states = [_make_resonance_state(seed=i) for i in range(5)]
        paths = []
        for s in states:
            paths.append(
                ReasoningPath(
                    initial_state=s,
                    intermediate_states=[],
                    final_state=s,
                    mu_trajectory=[s.mu_value, s.mu_value],
                    convergence_achieved=False,
                    termination_reason="Running",
                )
            )
        kept = eng.evaluate_paths(paths)
        assert len(kept) == 2
        mus = [p.mu_trajectory[-1] for p in kept]
        assert mus == sorted(mus, reverse=True)
