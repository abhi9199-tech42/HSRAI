import pytest
from isre.reasoning.generator import ReasoningPathGenerator
from isre.models.intent import IntentGraph, IntentNode
from hsrai.common.types import IntentType, EdgeType, SemanticType
from hsrai.common.models import SemanticPrimitive


def _make_node(nid="n1", ntype=IntentType.GOAL):
    return IntentNode(
        id=nid,
        type=ntype,
        semantic_payload=[SemanticPrimitive(id=f"p_{nid}", concept="test", type=SemanticType.CONCEPT)],
    )


class TestReasoningPathGenerator:
    def test_generate_paths_returns_list(self):
        gen = ReasoningPathGenerator()
        graph = IntentGraph()
        graph.add_node(_make_node("n1"))
        paths = gen.generate_paths(graph)
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_paths_have_nodes(self):
        gen = ReasoningPathGenerator()
        graph = IntentGraph()
        graph.add_node(_make_node("n1"))
        graph.add_node(_make_node("n2"))
        paths = gen.generate_paths(graph)
        for path in paths:
            assert len(path.steps) > 0

    def test_no_conflicts_single_path_plus_verification(self):
        gen = ReasoningPathGenerator()
        graph = IntentGraph()
        graph.add_node(_make_node("n1"))
        paths = gen.generate_paths(graph)
        assert len(paths) == 2
        strategies = [p.metadata.get("strategy") for p in paths]
        assert "Direct Execution" in strategies
        assert "Verification Mode" in strategies

    def test_conflicts_generate_branching_paths(self):
        gen = ReasoningPathGenerator()
        graph = IntentGraph()
        n1 = _make_node("n1")
        n1.conflict_markers = [{"partner_id": "n2"}]
        n2 = _make_node("n2", IntentType.CONSTRAINT)
        n2.conflict_markers = [{"partner_id": "n1"}]
        graph.add_node(n1)
        graph.add_node(n2)
        paths = gen.generate_paths(graph)
        assert len(paths) >= 2
        path_ids = {p.id for p in paths}
        assert len(path_ids) == len(paths)

    def test_each_path_has_id(self):
        gen = ReasoningPathGenerator()
        graph = IntentGraph()
        graph.add_node(_make_node("n1"))
        paths = gen.generate_paths(graph)
        for path in paths:
            assert path.id.startswith("path_")
