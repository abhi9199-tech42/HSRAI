from hypothesis import given
from hypothesis import strategies as st

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import EdgeType, IntentType, SemanticType
from hsrai.graph.builder import IntentGraphBuilder

# --- Strategies ---

@st.composite
def graph_node_strategy(draw):
    node_type = draw(st.sampled_from(IntentType))
    # Create simple payload
    payload = [SemanticPrimitive(
        id="prim_1", concept="test", type=SemanticType.CONCEPT, semantic_weight=1.0, modality="text"
    )]
    return node_type, payload

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
