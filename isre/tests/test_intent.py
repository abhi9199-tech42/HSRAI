import pytest
from isre.models.intent import IntentNode, IntentEdge, IntentGraph
from hsrai.common.types import IntentType, EdgeType, SemanticType
from hsrai.common.models import SemanticPrimitive


def _make_primitive(concept="test", pid="p1"):
    return SemanticPrimitive(id=pid, concept=concept, type=SemanticType.CONCEPT)


def _make_node(nid="n1", ntype=IntentType.GOAL):
    return IntentNode(id=nid, type=ntype, semantic_payload=[_make_primitive(pid=nid)])


class TestIntentNode:
    def test_creation(self):
        node = _make_node("n1", IntentType.GOAL)
        assert node.id == "n1"
        assert node.type == IntentType.GOAL
        assert len(node.semantic_payload) == 1

    def test_hash_equality(self):
        a = _make_node("n1")
        b = _make_node("n1")
        assert hash(a) == hash(b)
        assert a == b

    def test_inequality(self):
        a = _make_node("n1")
        b = _make_node("n2")
        assert a != b

    def test_default_activation(self):
        node = _make_node()
        assert node.activation_level == 1.0

    def test_conflict_markers_default(self):
        node = _make_node()
        assert node.conflict_markers == []


class TestIntentEdge:
    def test_creation(self):
        edge = IntentEdge(
            source_id="n1", target_id="n2", relationship_type=EdgeType.CAUSAL
        )
        assert edge.source_id == "n1"
        assert edge.target_id == "n2"
        assert edge.relationship_type == EdgeType.CAUSAL

    def test_default_weight(self):
        edge = IntentEdge(source_id="a", target_id="b", relationship_type=EdgeType.TEMPORAL)
        assert edge.weight == 1.0

    def test_trust_verified_default(self):
        edge = IntentEdge(source_id="a", target_id="b", relationship_type=EdgeType.TRUST_BASED)
        assert edge.trust_verified is False


class TestIntentGraph:
    def test_add_node(self):
        g = IntentGraph()
        node = _make_node("n1")
        g.add_node(node)
        assert "n1" in g.nodes

    def test_add_edge(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_node(_make_node("n2"))
        edge = IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.CAUSAL)
        g.add_edge(edge)
        assert len(g.edges) == 1

    def test_add_edge_missing_node_raises(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        edge = IntentEdge(source_id="n1", target_id="n99", relationship_type=EdgeType.CAUSAL)
        with pytest.raises(ValueError):
            g.add_edge(edge)

    def test_get_nodes_by_type(self):
        g = IntentGraph()
        g.add_node(_make_node("n1", IntentType.GOAL))
        g.add_node(_make_node("n2", IntentType.CONTEXT))
        goals = g.get_nodes_by_type(IntentType.GOAL)
        assert len(goals) == 1
        assert goals[0].id == "n1"

    def test_update_node_payload(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        new_payload = [_make_primitive("updated", "p2")]
        g.update_node_payload("n1", new_payload)
        assert g.nodes["n1"].semantic_payload[0].concept == "updated"

    def test_update_nonexistent_node_raises(self):
        g = IntentGraph()
        with pytest.raises(KeyError):
            g.update_node_payload("n99", [])

    def test_get_neighbors(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_node(_make_node("n2"))
        g.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.TEMPORAL))
        neighbors = g.get_neighbors("n1")
        assert "n2" in neighbors

    def test_clear(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_edge(IntentEdge(source_id="n1", target_id="n1", relationship_type=EdgeType.LOGICAL))
        g.clear()
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_has_cycles_no_cycle(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_node(_make_node("n2"))
        g.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.CAUSAL))
        assert not _has_cycle(g)

    def test_has_cycles_with_cycle(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_node(_make_node("n2"))
        g.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.CAUSAL))
        g.add_edge(IntentEdge(source_id="n2", target_id="n1", relationship_type=EdgeType.CAUSAL))
        assert _has_cycle(g)

    def test_priority_inversion_none(self):
        g = IntentGraph()
        g.add_node(_make_node("n1"))
        g.add_node(_make_node("n2"))
        g.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.PRIORITY))
        inversions = _check_priority_inversion(g)
        assert inversions == []

    def test_priority_inversion_detected(self):
        g = IntentGraph()
        n1 = _make_node("n1")
        n1.activation_level = 0.3
        n2 = _make_node("n2")
        n2.activation_level = 0.9
        g.add_node(n1)
        g.add_node(n2)
        # n2 has higher activation but n1 has priority over n2
        g.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.PRIORITY))
        inversions = _check_priority_inversion(g)
        assert len(inversions) == 1


def _has_cycle(graph: IntentGraph) -> bool:
    """DFS-based cycle detection."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in graph.nodes}
    adj = {}
    for e in graph.edges:
        adj.setdefault(e.source_id, []).append(e.target_id)

    def dfs(u):
        color[u] = GRAY
        for v in adj.get(u, []):
            if color.get(v) == GRAY:
                return True
            if color.get(v) == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(dfs(nid) for nid, c in list(color.items()) if c == WHITE)


def _check_priority_inversion(graph: IntentGraph) -> list:
    """Detect priority edges where source has lower activation than target."""
    inversions = []
    for e in graph.edges:
        if e.relationship_type == EdgeType.PRIORITY:
            src = graph.nodes.get(e.source_id)
            tgt = graph.nodes.get(e.target_id)
            if src and tgt and src.activation_level < tgt.activation_level:
                inversions.append((e.source_id, e.target_id))
    return inversions
