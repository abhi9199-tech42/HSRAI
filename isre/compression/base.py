from abc import ABC, abstractmethod
from typing import Any, List

from ..models.primitives import SemanticPrimitive


class SemanticCompressor(ABC):
    """
    Base class for all semantic compression modules.
    Ensures a consistent interface for converting raw input into semantic primitives.
    """

    @abstractmethod
    def compress(self, raw_input: Any) -> List[SemanticPrimitive]:
        """
        Convert raw input into a list of semantic primitives.
        Must be deterministic.
        """
        pass

    @property
    @abstractmethod
    def modality(self) -> str:
        """
        Return the input modality this compressor handles (e.g., 'text', 'speech').
        """
        pass
