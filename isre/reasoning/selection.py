from typing import List
from ..models.reasoning import ReasoningPath, ReasoningDecision
from ..models.intent import IntentNode
from ..types import IntentType

class CompetitiveSelector:
    """
    Evaluates and selects the best reasoning path based on multiple objectives.
    Requirement 3.2: Competitive selection.
    """

    def select(self, paths: List[ReasoningPath]) -> ReasoningDecision:
        if not paths:
            raise ValueError("Cannot select from empty path list")

        best_path = None
        best_score = -1.0
        
        scored_paths = []

        for path in paths:
            # 1. Calculate Component Scores
            satisfaction = self._score_intent_satisfaction(path)
            compliance = self._score_constraint_compliance(path)
            coherence = self._score_semantic_coherence(path)

            # Update path object with calculated scores
            path.intent_satisfaction_score = satisfaction
            path.constraint_compliance_score = compliance
            path.semantic_coherence_score = coherence

            # 2. Weighted Sum (for now equal weights)
            # In a real system, these weights could be adaptive.
            total_score = (satisfaction * 0.4) + (compliance * 0.4) + (coherence * 0.2)
            
            scored_paths.append(path)
            
            if total_score > best_score:
                best_score = total_score
                best_path = path

        return ReasoningDecision(
            selected_path=best_path,
            justification=f"Selected path with highest composite score: {best_score:.2f} "
                          f"(Sat: {best_path.intent_satisfaction_score:.2f}, "
                          f"Comp: {best_path.constraint_compliance_score:.2f})",
            confidence=best_score,
            alternative_paths=[p for p in scored_paths if p.id != best_path.id]
        )

    def _score_intent_satisfaction(self, path: ReasoningPath) -> float:
        """High score if GOAL nodes are present and active."""
        goals = [n for n in path.steps if n.type == IntentType.GOAL]
        if not goals:
            return 0.1
        # Simple heuristic: sum of activation levels of goals / total possible
        return sum(n.activation_level for n in goals) / len(goals)

    def _score_constraint_compliance(self, path: ReasoningPath) -> float:
        """
        High score if CONSTRAINT nodes are respected.
        In our prototype, if a path *removed* a node due to conflict, it might be cleaner.
        Checking if remaining nodes have internal conflicts.
        """
        # Penalize if any active node has a conflict marker pointing to another active node in the path
        active_ids = {n.id for n in path.steps}
        conflicts_found = 0
        
        for node in path.steps:
            for marker in node.conflict_markers:
                if marker['partner_id'] in active_ids:
                    conflicts_found += 1
        
        # If conflicts exist in the path, compliance is low
        if conflicts_found > 0:
            return 0.2
        return 1.0

    def _score_semantic_coherence(self, path: ReasoningPath) -> float:
        """
        Measure of how 'smooth' the semantic transition is.
        Placeholder: simply 0.8 for valid paths.
        """
        return 0.8
