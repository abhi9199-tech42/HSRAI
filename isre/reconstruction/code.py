from typing import Dict
from .base import OutputReconstructor
from ..models.reasoning import ReasoningDecision

class CodeGenerator(OutputReconstructor):
    """
    Generates executable code snippets from semantic decisions.
    """

    @property
    def format_type(self) -> str:
        return "code"

    def reconstruct(self, decision: ReasoningDecision) -> str:
        """
        Translates semantic steps into function calls.
        """
        lines = []
        for step in decision.selected_path.steps:
            for prim in step.semantic_payload:
                code_snippet = self._to_code(prim.concept)
                if code_snippet:
                    lines.append(code_snippet)
        
        return "\n".join(lines)

    def _to_code(self, concept: str) -> str:
        if "action_move_fast" in concept:
            return "agent.move(speed='fast')"
        if "attribute_fast" in concept:
            return "# speed set to fast"
        return f"# Processing {concept}"
