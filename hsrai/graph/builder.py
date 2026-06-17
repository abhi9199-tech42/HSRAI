from typing import List, Dict, Any, Optional

from hsrai.core.types import IntentType, EdgeType
from hsrai.core.models import SemanticPrimitive
from hsrai.core.utils import deterministic_id
from hsrai.graph.models import IntentNode, IntentEdge, IntentGraph

class IntentGraphBuilder:
    """
    Builder for constructing and optimizing IntentGraphs.
    """
    
    def __init__(self):
        self.graph = IntentGraph()
        
    def create_node(self, 
                   node_type: IntentType, 
                   payload: List[SemanticPrimitive], 
                   behavioral_score: float = 0.0,
                   node_id: str = None) -> IntentNode:
        """
        Create and add a new IntentNode to the graph.
        """
        if node_id is None:
            # Deterministic ID generation
            id_data = {
                "type": node_type.value,
                "payload_ids": sorted([p.id for p in payload]),
                "behavioral_score": behavioral_score
            }
            node_id = f"node_{deterministic_id(id_data)[:8]}"
            
        node = IntentNode(
            id=node_id,
            type=node_type,
            semantic_payload=payload,
            activation_level=1.0, # Default activation
            behavioral_score=behavioral_score
        )
        
        self.graph.add_node(node)
        return node

    def connect_nodes(self, 
                     source_id: str, 
                     target_id: str, 
                     edge_type: EdgeType, 
                     weight: float = 1.0,
                     trust_verified: bool = False) -> IntentEdge:
        """
        Create and add a directed edge between two nodes.
        """
        edge = IntentEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=edge_type,
            weight=weight,
            trust_verified=trust_verified
        )
        
        self.graph.add_edge(edge)
        return edge

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect explicit conflicts in the graph.
        Current Rule: A Constraint connected to a Goal via a PRIORITY edge 
        implies a potential resource conflict or blocking state.
        """
        conflicts = []
        
        for edge in self.graph.edges:
            source = self.graph.nodes.get(edge.source_id)
            target = self.graph.nodes.get(edge.target_id)
            
            if not source or not target:
                continue
                
            # Case 1: Constraint blocks Goal
            if source.type == IntentType.CONSTRAINT and target.type == IntentType.GOAL:
                # If connected by PRIORITY, it means the constraint overrides the goal
                if edge.relationship_type == EdgeType.PRIORITY:
                    conflict = {
                        "type": "blocking_constraint",
                        "source": source.id,
                        "target": target.id,
                        "severity": edge.weight
                    }
                    conflicts.append(conflict)
                    
                    # Mark nodes
                    source.conflict_markers.append(conflict)
                    target.conflict_markers.append(conflict)

        return conflicts

    def optimize_graph(self):
        """
        Optimize the graph for reasoning.
        - Prune isolated nodes (unless they are key Goals)
        - Normalize weights
        """
        # Remove isolated nodes that are not Goals
        nodes_to_remove = []
        for node_id, node in self.graph.nodes.items():
            if node.type == IntentType.GOAL:
                continue
                
            has_edges = False
            for edge in self.graph.edges:
                if edge.source_id == node_id or edge.target_id == node_id:
                    has_edges = True
                    break
            
            if not has_edges:
                nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            del self.graph.nodes[node_id]

    def get_graph(self) -> IntentGraph:
        return self.graph
