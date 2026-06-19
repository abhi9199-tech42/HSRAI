import math

import pytest

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import EdgeType, IntentType, SemanticType
from hsrai.graph.builder import IntentGraphBuilder
from hsrai.reasoning.hybrid_engine import HybridReasoningEngine
from hsrai.reasoning.oscillatory import OscillatoryGating


class TestReasoningEngine:

    def setup_method(self):
        self.builder = IntentGraphBuilder()
        # Create a simple diamond graph
        # Start -> A -> End
        # Start -> B -> End
        payload = [SemanticPrimitive(id="p", concept="c", type=SemanticType.CONCEPT, semantic_weight=1.0)]

        self.start = self.builder.create_node(IntentType.CONTEXT, payload, node_id="start")
        self.end = self.builder.create_node(IntentType.GOAL, payload, node_id="end")
        self.a = self.builder.create_node(IntentType.QUERY, payload, node_id="A")
        self.b = self.builder.create_node(IntentType.QUERY, payload, node_id="B")

        # Path 1: Start -> A -> End (High weight)
        self.builder.connect_nodes("start", "A", EdgeType.TEMPORAL, weight=0.9)
        self.builder.connect_nodes("A", "end", EdgeType.TEMPORAL, weight=0.9)

        # Path 2: Start -> B -> End (Low weight)
        self.builder.connect_nodes("start", "B", EdgeType.TEMPORAL, weight=0.1)
        self.builder.connect_nodes("B", "end", EdgeType.TEMPORAL, weight=0.1)

        self.engine = HybridReasoningEngine(self.builder.get_graph())

    def test_multipath_generation(self):
        """Property 6: Multi-path reasoning generation"""
        paths = self.engine.find_paths("start", "end")
        assert len(paths) == 2

        # Verify paths content
        path_strs = ["->".join([n.id for n in p.nodes]) for p in paths]
        assert "start->A->end" in path_strs
        assert "start->B->end" in path_strs

    def test_mu_stability_calculation(self):
        """Property 8: μ-stability calculation"""
        paths = self.engine.find_paths("start", "end")

        # Path A (High weight) should have higher stability (lower cost)
        # Cost = Length (2 edges) + 1 + (1-0.9)*2 = 3 + 0.2 = 3.2
        # Path B (Low weight)
        # Cost = Length (2 edges) + 1 + (1-0.1)*2 = 3 + 1.8 = 4.8

        mu_a = self.engine.calculate_stability(paths[0]) # Assuming order, need to check
        mu_b = self.engine.calculate_stability(paths[1])

        # Identify which is which
        path_a = next(p for p in paths if "A" in [n.id for n in p.nodes])
        path_b = next(p for p in paths if "B" in [n.id for n in p.nodes])

        mu_a = self.engine.calculate_stability(path_a)
        mu_b = self.engine.calculate_stability(path_b)

        assert mu_a > mu_b

    @pytest.mark.asyncio
    async def test_oscillatory_convergence(self):
        """Property 7: Oscillatory convergence"""
        self.engine.find_paths("start", "end")

        # Run for several steps
        converged_path = None
        # We need enough steps to allow phase to oscillate and delta_mu to stabilize
        # Use smaller dt to ensure we have enough steps within the attention window
        for _ in range(200):
            result = await self.engine.step(dt=0.01)
            if result:
                converged_path = result
                break

        # With the new convergence logic, it SHOULD converge to Path A
        assert converged_path is not None
        assert "A" in [n.id for n in converged_path.nodes]

    def test_gating_window(self):
        """Verify gating window logic"""
        gating = OscillatoryGating()
        gating.reset_phase_sync(0.0) # Cos(0) = 1 (In window)
        assert gating.in_attention_window_sync()

        gating.reset_phase_sync(math.pi) # Cos(pi) = -1 (Out of window)
        assert not gating.in_attention_window_sync()

