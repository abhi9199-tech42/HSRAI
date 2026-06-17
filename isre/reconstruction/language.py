from .base import OutputReconstructor
from ..models.reasoning import ReasoningDecision

class LanguageGenerator(OutputReconstructor):
    """
    Generates natural language output from semantic decisions.
    Uses template-based or deterministic generation to ensure translation-only behavior.
    """

    @property
    def format_type(self) -> str:
        return "text"

    def reconstruct(self, decision: ReasoningDecision) -> str:
        """
        Translates the selected path into a coherent sentence.
        """
        concepts = []
        for step in decision.selected_path.steps:
            # Gather primary concept from each step
            if step.semantic_payload:
                # Simple concatenation logic for prototype
                # In a real system, this would use a grammar engine
                c = step.semantic_payload[0].concept
                concepts.append(self._humanize(c))
        
        # Construct justification
        core_message = " ".join(concepts)
        return f"Decision: {core_message}. Rationale: {decision.justification}"

    def _humanize(self, concept: str) -> str:
        """Simple mapping to make concepts readable."""
        mapping = {
            "action_move_fast": "run",
            "attribute_fast": "quickly",
            "attribute_slow": "slowly",
            "fruit": "apple", # Context dependent in real app
        }
        return mapping.get(concept, concept)
