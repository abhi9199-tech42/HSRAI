import copy
import uuid
from typing import List, Tuple

from ..models.intent import IntentGraph, IntentNode
from ..models.reasoning import ReasoningPath


class ReasoningPathGenerator:
    """
    Generates multiple parallel reasoning paths from an IntentGraph.
    Handles conflict resolution by creating branching paths (Requirements 3.1).
    """

    def generate_paths(self, graph: IntentGraph) -> List[ReasoningPath]:
        """
        Input: IntentGraph with potential conflicts.
        Output: List of distinct ReasoningPaths representing different resolution strategies.
        """
        # 1. Identify conflicts
        conflicts = self._get_conflicts(graph)

        # 2. Base path (linear sequence of all nodes if no conflicts, or generic topological sort)
        # For prototype, we take nodes in order of creation/ID or a simple sort
        base_sequence = list(graph.nodes.values())
        # In a real graph, we'd follow edges. Assuming temporal edges for now.

        paths = []

        if not conflicts:
            # Single path strategy
            paths.append(self._create_path(base_sequence, "Direct Execution"))
        else:
            # Multi-path generation based on conflict resolution
            # For each conflict pair (A, B), generate strategies:
            # Strategy 1: Prioritize A (Suppress B)
            # Strategy 2: Prioritize B (Suppress A)

            # Simple implementation: Handle the first major conflict found to branch
            # (Full CSP solver would be needed for complex multi-conflict graphs)

            # Group conflicts for valid branching (simplification)
            processed_pairs = set()

            for conflict in conflicts:
                n1, n2 = conflict
                pair_id = tuple(sorted((n1.id, n2.id)))

                if pair_id in processed_pairs:
                    continue
                processed_pairs.add(pair_id)

                # Path A: Keep n1, Remove/Deactivate n2
                seq_a = [n for n in base_sequence if n.id != n2.id]
                paths.append(self._create_path(seq_a, f"Prioritize {n1.id} over {n2.id}"))

                # Path B: Keep n2, Remove/Deactivate n1
                seq_b = [n for n in base_sequence if n.id != n1.id]
                paths.append(self._create_path(seq_b, f"Prioritize {n2.id} over {n1.id}"))

        # 3. Add generic "Cautious" path that keeps all but lowers confidence/weights?
        # Or an "Exploratory" path.
        # Requirement 3.1 asks for multiple reasoning paths.
        if len(paths) == 1:
             # If no conflicts, still generate an alternative "Audit/Verify" path
             paths.append(self._create_path(base_sequence, "Verification Mode", activation_scale=0.8))

        return paths

    def _get_conflicts(self, graph: IntentGraph) -> List[Tuple[IntentNode, IntentNode]]:
        """Returns list of conflicting node pairs."""
        conflicts = []
        nodes = graph.nodes
        for node in nodes.values():
            for marker in node.conflict_markers:
                partner_id = marker['partner_id']
                if partner_id in nodes:
                    # Avoid duplicates by id comparison
                    if node.id < partner_id:
                        conflicts.append((node, nodes[partner_id]))
        return conflicts

    def _create_path(self, steps: List[IntentNode], strategy_name: str, activation_scale: float = 1.0) -> ReasoningPath:
        # Calculate initial semantic coherence (mock calculation based on node types)
        coherence = 1.0
        # Penalty for mixed goals/constraints without resolution?

        return ReasoningPath(
            id=f"path_{uuid.uuid4().hex[:8]}",
            steps=copy.deepcopy(steps),
            intent_satisfaction_score=0.5, # To be filled by Scorer
            semantic_coherence_score=0.5, # To be filled by Scorer
            metadata={"strategy": strategy_name, "scale": activation_scale}
        )
