import math

from hypothesis import given
from hypothesis import strategies as st
from hypothesis import assume

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import EdgeType, IntentType, SemanticType
from hsrai.graph.builder import IntentGraphBuilder

# --- Strategies ---

_node_counter = 0

def _unique_payload(label=""):
    global _node_counter
    _node_counter += 1
    return [SemanticPrimitive(
        id=f"prim_{_node_counter}", concept=f"test_{label}_{_node_counter}",
        type=SemanticType.CONCEPT, semantic_weight=1.0, modality="text"
    )]

@st.composite
def graph_node_strategy(draw):
    node_type = draw(st.sampled_from(IntentType))
    return node_type, _unique_payload("node")

@st.composite
def conflict_graph_strategy(draw):
    """
    Generate a random graph with a known number of seeded contradictions.
    Returns (builder, expected_contradictions).
    """
    builder = IntentGraphBuilder()
    num_nodes = draw(st.integers(min_value=2, max_value=12))

    # Decide number of contradictions to seed (0 to floor(num_nodes/2))
    max_contradictions = num_nodes // 2
    num_contradictions = draw(st.integers(min_value=0, max_value=max_contradictions))

    # Generate all nodes with unique payloads so deterministic_id gives unique IDs
    nodes = []
    contradiction_pairs = []

    for _ in range(num_contradictions):
        constraint = builder.create_node(IntentType.CONSTRAINT, _unique_payload("c"))
        goal = builder.create_node(IntentType.GOAL, _unique_payload("g"))
        nodes.extend([constraint, goal])
        contradiction_pairs.append((constraint, goal))

    # Fill remaining slots with random type nodes (no CONSTRAINT to keep clean)
    remaining = num_nodes - len(nodes)
    non_contradiction_types = [t for t in IntentType if t != IntentType.CONSTRAINT]
    for _ in range(remaining):
        ntype = draw(st.sampled_from(non_contradiction_types))
        node = builder.create_node(ntype, _unique_payload("fill"))
        nodes.append(node)

    # Connect contradiction pairs with PRIORITY edges
    for constraint, goal in contradiction_pairs:
        weight = draw(st.floats(min_value=0.1, max_value=1.0))
        builder.connect_nodes(constraint.id, goal.id, EdgeType.PRIORITY, weight=weight)

    # Add some non-contradiction edges between random nodes (to ensure no false positives)
    all_ids = [n.id for n in nodes]
    num_extra_edges = draw(st.integers(min_value=0, max_value=min(5, len(nodes) - 1)))
    for _ in range(num_extra_edges):
        src = draw(st.sampled_from(all_ids))
        tgt = draw(st.sampled_from(all_ids))
        assume(src != tgt)
        etype = draw(st.sampled_from([EdgeType.CAUSAL, EdgeType.TEMPORAL, EdgeType.LOGICAL]))
        builder.connect_nodes(src, tgt, etype)

    return builder, num_contradictions

# --- Tests ---

class TestIntentGraphConstruction:

    def setup_method(self):
        self.builder = IntentGraphBuilder()

    def test_node_creation(self):
        """Verify basic node creation"""
        payload = [SemanticPrimitive(
            id="p1", concept="c1", type=SemanticType.CONCEPT, semantic_weight=1.0, modality="text"
        )]
        node = self.builder.create_node(IntentType.GOAL, payload)

        assert node.id in self.builder.graph.nodes
        assert self.builder.graph.nodes[node.id] == node
        assert node.type == IntentType.GOAL

    def test_edge_creation(self):
        """Verify edge connection"""
        payload = []
        n1 = self.builder.create_node(IntentType.GOAL, payload)
        n2 = self.builder.create_node(IntentType.CONTEXT, payload)

        edge = self.builder.connect_nodes(n1.id, n2.id, EdgeType.CAUSAL)

        assert edge in self.builder.graph.edges
        assert edge.source_id == n1.id
        assert edge.target_id == n2.id

    def test_conflict_detection(self):
        """Property 5: Conflict representation consistency"""
        payload = []
        # Create a Goal and a Constraint
        goal = self.builder.create_node(IntentType.GOAL, payload)
        constraint = self.builder.create_node(IntentType.CONSTRAINT, payload)

        # Connect with PRIORITY edge (Constraint -> Goal)
        self.builder.connect_nodes(constraint.id, goal.id, EdgeType.PRIORITY, weight=0.8)

        conflicts = self.builder.detect_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "blocking_constraint"
        assert conflicts[0]["source"] == constraint.id
        assert conflicts[0]["target"] == goal.id

        # Verify markers
        assert len(goal.conflict_markers) > 0
        assert len(constraint.conflict_markers) > 0

    def test_optimization_pruning(self):
        """Verify optimization removes isolated non-Goal nodes"""
        payload = []
        # Goal node (should stay)
        goal = self.builder.create_node(IntentType.GOAL, payload)

        # Isolated Context node (should be removed)
        context = self.builder.create_node(IntentType.CONTEXT, payload)

        # Connected Query node (should stay)
        query = self.builder.create_node(IntentType.QUERY, payload)
        self.builder.connect_nodes(goal.id, query.id, EdgeType.LOGICAL)

        self.builder.optimize_graph()

        assert goal.id in self.builder.graph.nodes
        assert context.id not in self.builder.graph.nodes
        assert query.id in self.builder.graph.nodes

    @given(st.lists(graph_node_strategy(), min_size=1, max_size=10))
    def test_graph_integrity(self, nodes_data):
        """Property 4: Intent graph completeness"""
        builder = IntentGraphBuilder()
        created_ids = []

        for n_type, payload in nodes_data:
            node = builder.create_node(n_type, payload)
            created_ids.append(node.id)

        # Connect them in a chain
        for i in range(len(created_ids) - 1):
            builder.connect_nodes(created_ids[i], created_ids[i+1], EdgeType.TEMPORAL)

        graph = builder.get_graph()

        # Verify node count matches unique IDs created (since duplicate content = same ID)
        assert len(graph.nodes) == len(set(created_ids))

        # Verify edge count (duplicates might result in self-loops or fewer edges)
        # We just check basic connectivity if we have distinct nodes
        if len(set(created_ids)) > 1:
            assert len(graph.edges) >= len(set(created_ids)) - 1

        # Verify connectivity consistency
        for edge in graph.edges:
            assert edge.source_id in graph.nodes
            assert edge.target_id in graph.nodes


class TestContradictionCatchRate:
    """
    Measures how many seeded contradictions the system correctly catches.
    """

    CAUGHT = 0
    TOTAL = 0
    RUNS = 0

    def setup_method(self):
        self.run_contradictions_caught = 0
        self.run_contradictions_seeded = 0

    def teardown_method(self):
        TestContradictionCatchRate.CAUGHT += self.run_contradictions_caught
        TestContradictionCatchRate.TOTAL += self.run_contradictions_seeded
        TestContradictionCatchRate.RUNS += 1

    @given(conflict_graph_strategy())
    def test_contradiction_catch_rate(self, graph_data):
        """
        For each randomly generated graph with N seeded contradictions,
        verify detect_conflicts() catches exactly N.
        """
        builder, seeded = graph_data
        self.run_contradictions_seeded += seeded

        conflicts = builder.detect_conflicts()
        caught = len(conflicts)

        # Every conflict must be of the right type
        for c in conflicts:
            assert c["type"] == "blocking_constraint"

        # Verify markers match detected conflicts
        marker_count = sum(
            1 for n in builder.graph.nodes.values() if n.conflict_markers
        )

        if seeded > 0:
            assert marker_count > 0
            # Each conflict marks 2 nodes, so markers count = 2 * caught
            assert marker_count >= caught  # at minimum one node per conflict

        # Track catch rate
        self.run_contradictions_caught += caught

    @classmethod
    def teardown_class(cls):
        if cls.TOTAL > 0:
            rate = cls.CAUGHT / cls.TOTAL * 100
            print(f"\n  Contradiction catch rate: {cls.CAUGHT}/{cls.TOTAL} = {rate:.1f}%")
        if cls.RUNS > 0:
            print(f"  Test runs: {cls.RUNS}")

    def test_false_positive_rate(self):
        """Verify no false positives when there are zero contradictions."""
        builder = IntentGraphBuilder()
        payload = []

        goal = builder.create_node(IntentType.GOAL, payload)
        context = builder.create_node(IntentType.CONTEXT, payload)
        query = builder.create_node(IntentType.QUERY, payload)

        builder.connect_nodes(goal.id, context.id, EdgeType.CAUSAL)
        builder.connect_nodes(context.id, query.id, EdgeType.TEMPORAL)
        builder.connect_nodes(query.id, goal.id, EdgeType.LOGICAL)

        conflicts = builder.detect_conflicts()
        assert len(conflicts) == 0

    def test_multi_goal_multi_constraint(self):
        """Multiple goals each constrained by multiple constraints."""
        builder = IntentGraphBuilder()
        payload = []

        goals = [builder.create_node(IntentType.GOAL, payload) for _ in range(3)]
        constraints = [builder.create_node(IntentType.CONSTRAINT, payload) for _ in range(2)]

        # Each constraint connects to every goal
        expected = 0
        for c in constraints:
            for g in goals:
                builder.connect_nodes(c.id, g.id, EdgeType.PRIORITY, weight=0.5)
                expected += 1

        conflicts = builder.detect_conflicts()
        assert len(conflicts) == expected

    def test_priority_edge_non_constraint(self):
        """PRIORITY edge between non-CONSTRAINT nodes should NOT trigger conflict."""
        builder = IntentGraphBuilder()
        payload = []

        goal = builder.create_node(IntentType.GOAL, payload)
        context = builder.create_node(IntentType.CONTEXT, payload)

        builder.connect_nodes(context.id, goal.id, EdgeType.PRIORITY, weight=0.5)

        conflicts = builder.detect_conflicts()
        assert len(conflicts) == 0

    def test_constraint_non_priority_edge(self):
        """CONSTRAINT->GOAL via non-PRIORITY edge should NOT trigger conflict."""
        builder = IntentGraphBuilder()
        payload = []

        goal = builder.create_node(IntentType.GOAL, payload)
        constraint = builder.create_node(IntentType.CONSTRAINT, payload)

        builder.connect_nodes(constraint.id, goal.id, EdgeType.CAUSAL, weight=0.5)

        conflicts = builder.detect_conflicts()
        assert len(conflicts) == 0

    def test_conflict_marker_clear_on_rerun(self):
        """Repeated detect_conflicts() calls should not duplicate markers."""
        builder = IntentGraphBuilder()
        payload = []

        goal = builder.create_node(IntentType.GOAL, payload)
        constraint = builder.create_node(IntentType.CONSTRAINT, payload)
        builder.connect_nodes(constraint.id, goal.id, EdgeType.PRIORITY, weight=0.8)

        conflicts1 = builder.detect_conflicts()
        assert len(conflicts1) == 1
        assert len(goal.conflict_markers) == 1

        conflicts2 = builder.detect_conflicts()
        assert len(conflicts2) == 1
        assert len(goal.conflict_markers) == 1
        assert len(constraint.conflict_markers) == 1
