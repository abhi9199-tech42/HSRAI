from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from hsrai.common.types import IntentType, EdgeType
from hsrai.common.models import SemanticPrimitive

class IntentNode(BaseModel):
    """
    A node in the Intent Graph, representing a specific intentional state.
    """
    id: str
    type: IntentType
    semantic_payload: List[SemanticPrimitive]
    activation_level: float = 1.0
    behavioral_score: float = 0.0 # Added for HSRAI
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
    trust_verified: bool = False # Added for HSRAI

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
        return [n for n in self.nodes.values() if n.type == node_type]

    def update_node_payload(self, node_id: str, new_payload: List[SemanticPrimitive]):
        if node_id in self.nodes:
            self.nodes[node_id].semantic_payload = new_payload
        else:
            raise KeyError(f"Node {node_id} not found in graph")

    def get_neighbors(self, node_id: str) -> List[str]:
        return [e.target_id for e in self.edges if e.source_id == node_id]

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
