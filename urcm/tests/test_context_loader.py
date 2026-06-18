import numpy as np
import pytest

from urcm.core.context_loader import ContextLoader


class TestContextLoader:
    def setup_method(self):
        self.loader = ContextLoader(frequency_dim=24)

    def test_load_context_state_returns_array(self):
        result = self.loader.load_context_state(["apple"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (24,)

    def test_load_context_known_concept(self):
        result = self.loader.load_context_state(["apple"])
        norm = np.linalg.norm(result)
        assert norm == pytest.approx(1.0, abs=1e-5)

    def test_load_context_multiple_concepts(self):
        result = self.loader.load_context_state(["apple", "run"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (24,)
        assert np.isfinite(result).all()

    def test_load_context_unknown_concept_returns_zeros(self):
        result = self.loader.load_context_state(["nonexistent_xyz_999"])
        assert np.allclose(result, 0.0)

    def test_load_context_empty_list_returns_zeros(self):
        result = self.loader.load_context_state([])
        assert np.allclose(result, 0.0)

    def test_load_context_concept_in_knowledge_base(self):
        result = self.loader.load_context_state(["physics_gravity"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (24,)
        assert np.isfinite(result).all()

    def test_stringify_content_dict(self):
        content = {"type": "fruit", "color": "red"}
        s = self.loader._stringify_content("apple", content)
        assert "apple" in s
        assert "type" in s
        assert "fruit" in s

    def test_stringify_content_list_value(self):
        content = {"colors": ["red", "green"]}
        s = self.loader._stringify_content("apple", content)
        assert "red" in s
        assert "green" in s

    def test_stringify_content_non_dict(self):
        s = self.loader._stringify_content("gravity", "9.81 m/s^2")
        assert "gravity" in s
