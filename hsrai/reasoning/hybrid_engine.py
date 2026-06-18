from dataclasses import dataclass
from typing import List, Optional

from hsrai.graph.models import IntentEdge, IntentGraph, IntentNode
from hsrai.reasoning.oscillatory import OscillatoryGating


@dataclass
class ReasoningPath:
    """A candidate reasoning path through the intent graph with stability metrics."""
    nodes: List[IntentNode]
    edges: List[IntentEdge]
    mu_stability: float = 0.0
    coherence_score: float = 0.0

    @property
    def length(self) -> int:
        return len(self.nodes)

    def __hash__(self) -> int:
        node_ids = tuple(n.id for n in self.nodes)
        edge_ids = tuple((e.source_id, e.target_id) for e in self.edges)
        return hash((node_ids, edge_ids))

class HybridReasoningEngine:
    """
    Orchestrates hybrid reasoning using structural graph traversal
    modulated by oscillatory dynamics.
    """

    def __init__(self, graph: IntentGraph, gating: OscillatoryGating = None):
        self.graph = graph
        self.gating = gating or OscillatoryGating()
        self.active_paths: List[ReasoningPath] = []
        self.prev_best_path_hash: Optional[int] = None
        self.stability_counter: int = 0
        self.convergence_threshold: float = 0.1 # Minimum Mu to consider

    def find_paths(self, start_id: str, end_id: str, max_depth: int = 10) -> List[ReasoningPath]:
        """
        Find all valid paths from start to end node (DFS).
        """
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            return []

        paths = []
        visited = set()

        def dfs(current_id: str, current_path_nodes: List[IntentNode], current_path_edges: List[IntentEdge]):
            if len(current_path_nodes) > max_depth:
                return

            if current_id == end_id:
                paths.append(ReasoningPath(
                    nodes=list(current_path_nodes),
                    edges=list(current_path_edges)
                ))
                return

            visited.add(current_id)

            # Find neighbors
            outgoing_edges = [e for e in self.graph.edges if e.source_id == current_id]

            for edge in outgoing_edges:
                neighbor_id = edge.target_id
                if neighbor_id not in visited:
                    neighbor_node = self.graph.nodes[neighbor_id]

                    dfs(neighbor_id,
                        current_path_nodes + [neighbor_node],
                        current_path_edges + [edge])

            visited.remove(current_id)

        start_node = self.graph.nodes[start_id]
        dfs(start_id, [start_node], [])

        self.active_paths = paths
        return paths

    def calculate_stability(self, path: ReasoningPath) -> float:
        """
        Calculate μ-stability = ρ / χ
        ρ (rho): Semantic density (avg semantic weight of nodes)
        χ (chi): Transformation cost (path length + conflict penalties)
        """
        if not path.nodes:
            return 0.0

        # Rho: Average semantic weight of primitives in nodes
        total_weight = 0.0
        count = 0
        for node in path.nodes:
            for prim in node.semantic_payload:
                total_weight += prim.semantic_weight
                count += 1

        rho = (total_weight / count) if count > 0 else 0.0

        # Chi: Cost
        # Base cost is path length (steps)
        # Add penalties for low-weight edges or conflicts
        chi = len(path.edges) + 1.0 # +1 to avoid division by zero

        for edge in path.edges:
            # Lower weight edge = Higher cost (resistance)
            chi += (1.0 - edge.weight)

        for node in path.nodes:
            # Conflicts increase cost significantly
            chi += len(node.conflict_markers) * 2.0

        mu = rho / chi
        path.mu_stability = mu
        return mu

    def step(self, dt: float = 0.1) -> Optional[ReasoningPath]:
        """
        Advance the reasoning process by one time step.
        Returns the best path if convergence is reached.
        """
        self.gating.advance_time(dt)

        # Only process if in attention window
        if not self.gating.in_attention_window():
            return None

        # Update stabilities
        best_mu = -1.0
        best_path = None

        for path in self.active_paths:
            mu = self.calculate_stability(path)

            # Apply Gating to stability (modulation)
            # We create a pseudo-vector for the path stability to apply gating
            # In a full model, this would be the node's resonance vector
            # Here we just modulate the scalar mu

            # Simple modulation: mu_gated = mu * cos_phase (if positive)
            g_t = self.gating.get_global_rhythm()
            modulation = max(0.1, g_t[1]) # Ensure non-negative multiplier

            path.mu_stability = mu * modulation

            if path.mu_stability > best_mu:
                best_mu = path.mu_stability
                best_path = path

        # Convergence Check
        # Check if the best path has been consistently selected

        if best_path and best_mu > self.convergence_threshold:
            current_path_hash = hash(best_path)

            if current_path_hash == self.prev_best_path_hash:
                self.stability_counter += 1
            else:
                self.stability_counter = 0
                self.prev_best_path_hash = current_path_hash

            # If stable for N cycles, converge
            if self.stability_counter >= 5:
                return best_path
        else:
             self.stability_counter = 0
             self.prev_best_path_hash = None

        return None
