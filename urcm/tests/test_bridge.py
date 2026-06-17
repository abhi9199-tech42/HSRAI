import pytest
import numpy as np

from urcm.integration.isre.bridge import IntentResonanceBridge
from urcm.integration.isre.intent_models import IntentNode, GoalHierarchy
from urcm.core.data_models import ResonanceState


class TestIntentResonanceBridge:
    def setup_method(self):
        self.bridge = IntentResonanceBridge()

    def _make_intent(self, desc="test intent", priority=0.5):
        return IntentNode(
            intent_id="intent_1",
            description=desc,
            priority=priority,
        )

    def _make_context(self, dim=24):
        vec = np.random.randn(dim)
        return vec / np.linalg.norm(vec)

    def test_resonate_on_intent_returns_float(self):
        intent = self._make_intent()
        ctx = self._make_context()
        mu = self.bridge.resonate_on_intent(intent, ctx)
        assert isinstance(mu, float)

    def test_resonate_on_intent_finite(self):
        intent = self._make_intent()
        ctx = self._make_context()
        mu = self.bridge.resonate_on_intent(intent, ctx)
        assert np.isfinite(mu)

    def test_resonate_on_intent_different_intents_different_mu(self):
        ctx = self._make_context()
        intent1 = self._make_intent(desc="completely different meaning A")
        intent2 = self._make_intent(desc="completely different meaning B")
        mu1 = self.bridge.resonate_on_intent(intent1, ctx)
        mu2 = self.bridge.resonate_on_intent(intent2, ctx)
        assert mu1 != pytest.approx(mu2, abs=1e-6)

    def test_resonate_on_intent_positive_mu(self):
        intent = self._make_intent(desc="meaningful semantic content")
        ctx = self._make_context()
        mu = self.bridge.resonate_on_intent(intent, ctx)
        assert mu >= 0.0

    def test_find_resonant_goal_returns_best(self):
        hierarchy = GoalHierarchy(root_id="root")
        hierarchy.add_node(IntentNode(
            intent_id="a", description="alpha bravo charlie",
            priority=0.8, children_ids=["b", "c"],
        ))
        hierarchy.add_node(IntentNode(
            intent_id="b", description="delta echo foxtrot",
            priority=0.3,
        ))
        hierarchy.add_node(IntentNode(
            intent_id="c", description="golf hotel india",
            priority=0.9,
        ))
        ctx = self._make_context()
        best, mu = self.bridge.find_resonant_goal(hierarchy, ctx)
        assert best is not None
        assert isinstance(mu, float)
        assert best.intent_id in ("b", "c")

    def test_find_resonant_goal_empty_hierarchy(self):
        hierarchy = GoalHierarchy(root_id="root")
        ctx = self._make_context()
        best, mu = self.bridge.find_resonant_goal(hierarchy, ctx)
        assert best is None
        assert mu == -1.0

    def test_resonate_on_intent_context_dim_mismatch(self):
        intent = self._make_intent()
        ctx = np.random.randn(10)
        mu = self.bridge.resonate_on_intent(intent, ctx)
        assert np.isfinite(mu)
