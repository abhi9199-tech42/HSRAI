from typing import List

from ..models.intent import IntentEdge, IntentGraph, IntentNode
from ..models.primitives import SemanticPrimitive
from ..types import EdgeType, IntentType


class IntentGraphBuilder:
    """
    Transforms SemanticPrimitives into a structured IntentGraph.
    Implements explicit conflict detection and representation.
    """

    def build_from_primitives(self, primitives: List[SemanticPrimitive]) -> IntentGraph:
        """
        Creates a basic intent graph where each primitive becomes a node.
        In a more advanced implementation, this would involve heuristic or LLM-guided clustering.
        """
        graph = IntentGraph()
        nodes = []

        # 1. Generate Nodes
        # For the prototype, we assume each meaningful concept warrants an intent node.
        # We categorize them based on concept prefixes or metadata if available.
        for prim in primitives:
            node_type = self._infer_intent_type(prim)
            node = IntentNode(
                id=f"node_{prim.id}",
                type=node_type,
                semantic_payload=[prim],
                activation_level=prim.semantic_weight
            )
            graph.add_node(node)
            nodes.append(node)

        # 2. Establish basic causal/temporal edges (sequential by default for now)
        for i in range(len(nodes) - 1):
            edge = IntentEdge(
                source_id=nodes[i].id,
                target_id=nodes[i+1].id,
                relationship_type=EdgeType.TEMPORAL,
                semantic_label="sequenced_intent"
            )
            graph.add_edge(edge)

        # 3. Detect and represent conflicts
        self._detect_conflicts(graph)

        return graph

    def _infer_intent_type(self, primitive: SemanticPrimitive) -> IntentType:
        """Heuristic to map semantic concepts to intent types."""
        concept = primitive.concept.lower()
        if "action" in concept or "goal" in concept:
            return IntentType.GOAL
        if "query" in concept or "?" in concept:
            return IntentType.QUERY
        if "constraint" in concept or "must" in concept or "only" in concept:
            return IntentType.CONSTRAINT
        if "emotion" in concept:
            return IntentType.EMOTION
        return IntentType.CONTEXT

    def _detect_conflicts(self, graph: IntentGraph):
        """
        Explicitly identifies and marks conflicts between nodes.
        Requirement 2.4: Explicitly represent conflicts.
        """
        node_list = list(graph.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                n1 = node_list[i]
                n2 = node_list[j]

                # Simple conflict heuristic: opposite semantic concepts
                if self._are_conflicting(n1, n2):
                    conflict_info = {
                        "type": "semantic_opposition",
                        "partner_id": n2.id,
                        "description": f"Conflict between {n1.id} and {n2.id}"
                    }
                    n1.conflict_markers.append(conflict_info)

                    # Mutual marking
                    n2.conflict_markers.append({
                        "type": "semantic_opposition",
                        "partner_id": n1.id,
                        "description": f"Conflict between {n2.id} and {n1.id}"
                    })

    def _are_conflicting(self, n1: IntentNode, n2: IntentNode) -> bool:
        """Determines if two nodes have conflicting semantics."""
        # Example logic: "fast" vs "slow" in the same context
        concepts1 = [p.concept for p in n1.semantic_payload]
        concepts2 = [p.concept for p in n2.semantic_payload]

        opposites = {
            "attribute_fast": "attribute_slow",
            "action_move_fast": "action_move_slow"
        }

        for c1 in concepts1:
            for c2 in concepts2:
                if opposites.get(c1) == c2 or opposites.get(c2) == c1:
                    return True
        return False
