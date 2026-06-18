import pytest

from urcm.core.data_models import ReasoningPath
from urcm.core.system import URCMSystem


class TestURCMSystem:
    def setup_method(self):
        self.system = URCMSystem(
            frequency_dim=24,
            resonance_dim=64,
            latent_dim=16,
            base_frequency=1.0,
            beam_width=2,
            max_steps=10,
        )

    def test_initialization(self):
        assert self.system.status["initialized"] is True
        assert self.system.status["processed_count"] == 0
        assert self.system.frequency_dim == 24
        assert self.system.resonance_dim == 64
        assert self.system.latent_dim == 16

    def test_process_query_returns_reasoning_path(self):
        result = self.system.process_query("hello world")
        assert isinstance(result, ReasoningPath)

    def test_process_query_trajectory_nonempty(self):
        result = self.system.process_query("test input")
        assert len(result.mu_trajectory) > 0

    def test_process_query_increments_count(self):
        self.system.process_query("first")
        assert self.system.status["processed_count"] == 1
        self.system.process_query("second")
        assert self.system.status["processed_count"] == 2

    def test_process_query_empty_string(self):
        with pytest.raises(ValueError):
            self.system.process_query("")

    def test_process_query_has_initial_and_final(self):
        result = self.system.process_query("query")
        assert result.initial_state is not None
        assert result.final_state is not None

    def test_process_query_convergence_field(self):
        result = self.system.process_query("test")
        assert isinstance(result.convergence_achieved, bool)

    def test_process_query_termination_reason_nonempty(self):
        result = self.system.process_query("test")
        assert isinstance(result.termination_reason, str)
        assert len(result.termination_reason) > 0

    def test_validate_system(self):
        checks = self.system.validate_system()
        assert "overall_health" in checks
