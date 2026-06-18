from abc import ABC, abstractmethod
from typing import Any

from ..models.reasoning import ReasoningDecision


class OutputReconstructor(ABC):
    """
    Base class for transforming semantic reasoning decisions into specific output formats.
    Requirement 5.1: Convert semantic decisions into language, code, or actions.
    """

    @abstractmethod
    def reconstruct(self, decision: ReasoningDecision) -> Any:
        """
        Transform the reasoning decision into the target format.
        This must be a translation process, not a reasoning process (Req 5.5).
        """
        pass

    @property
    @abstractmethod
    def format_type(self) -> str:
        """The type of output this reconstructor produces (e.g., 'text', 'code', 'action')."""
        pass
