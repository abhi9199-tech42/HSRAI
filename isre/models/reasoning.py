from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .intent import IntentNode


class ReasoningPath(BaseModel):
    """
    A sequence of steps followed by the reasoning engine.
    """
    id: str
    steps: List[IntentNode]
    intent_satisfaction_score: float = 0.0
    constraint_compliance_score: float = 0.0
    semantic_coherence_score: float = 0.0
    oscillation_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReasoningDecision(BaseModel):
    """
    The final selection from multiple reasoning paths.
    """
    selected_path: ReasoningPath
    justification: str
    confidence: float
    alternative_paths: List[ReasoningPath]
    convergence_metadata: Dict[str, Any] = Field(default_factory=dict)
