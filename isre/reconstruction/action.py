from typing import Any, Dict, List

from ..models.reasoning import ReasoningDecision
from .base import OutputReconstructor


class ActionPlanner(OutputReconstructor):
    """
    Generates structured action sequences for robotic or agentic execution.
    """

    @property
    def format_type(self) -> str:
        return "action"

    def reconstruct(self, decision: ReasoningDecision) -> List[Dict[str, Any]]:
        """
        Translates semantics into a JSON-serializable plan.
        """
        plan = []
        for i, step in enumerate(decision.selected_path.steps):
            action_item = {
                "step": i + 1,
                "node_id": step.id,
                "type": step.type.value,
                "parameters": {}
            }

            # Extract params from primitives
            for prim in step.semantic_payload:
                action_item["parameters"][prim.id] = prim.concept

            plan.append(action_item)

        return plan
