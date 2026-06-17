from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..types import IntentType, EdgeType
from .primitives import SemanticPrimitive

class IntentNode(BaseModel):
    """
    A node in the Intent Graph, representing a specific intentional state.
    """
    id: str
    type: IntentType
    semantic_payload: List[SemanticPrimitive]
    activation_level: float = 1.0
    conflict_markers: List[Dict[str, Any]] = Field(default_factory=list)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, IntentNode):
            return False
        return self.id == other.id

class IntentEdge(BaseModel):
    """
    A directed edge between IntentNodes, representing their relationship.
    """
    source_id: str
    target_id: str
    relationship_type: EdgeType
    weight: float = 1.0
    semantic_label: Optional[str] = None

class IntentGraph(BaseModel):
    """
    A structured collection of IntentNodes and IntentEdges.
    """
    nodes: Dict[str, IntentNode] = Field(default_factory=dict)
    edges: List[IntentEdge] = Field(default_factory=list)

    def add_node(self, node: IntentNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: IntentEdge):
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError("Edge source and target nodes must exist in the graph")
        self.edges.append(edge)

    def get_nodes_by_type(self, node_type: IntentType) -> List[IntentNode]:
        """API for external inspection: Returns all nodes of a specific type. (Requirement 8.4)"""
        return [n for n in self.nodes.values() if n.type == node_type]

    def update_node_payload(self, node_id: str, new_payload: List[SemanticPrimitive]):
        """API for external modification: Updates the semantic payload of a node. (Requirement 8.4)"""
        if node_id in self.nodes:
            self.nodes[node_id].semantic_payload = new_payload
        else:
            raise KeyError(f"Node {node_id} not found in graph")

    def get_neighbors(self, node_id: str) -> List[str]:
        return [e.target_id for e in self.edges if e.source_id == node_id]

    def has_cycles(self) -> bool:
        """Requirement 8.1: Detect cycles in the intent graph."""
        visited = set()
        path = set()

        def visit(node_id):
            if node_id in path: return True
            if node_id in visited: return False
            visited.add(node_id)
            path.add(node_id)
            for neighbor in self.get_neighbors(node_id):
                if visit(neighbor): return True
            path.remove(node_id)
            return False

        return any(visit(node_id) for node_id in self.nodes)

    def check_priority_inversion(self) -> List[str]:
        """Test 7.4: Detect if a goal has higher activation than its constraining nodes."""
        inversions = []
        for edge in self.edges:
            src = self.nodes[edge.source_id]
            tgt = self.nodes[edge.target_id]
            if src.type == IntentType.CONSTRAINT and tgt.type == IntentType.GOAL:
                if tgt.activation_level > src.activation_level:
                    inversions.append(f"Inversion: {tgt.id} (Goal) > {src.id} (Constraint)")
        return inversions

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
