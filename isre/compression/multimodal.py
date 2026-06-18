from typing import Any, Dict, List

from ..models.primitives import SemanticPrimitive
from .base import SemanticCompressor
from .speech import PhonemeExtractor
from .text import ConceptMapper


class MultimodalProcessor:
    """
    Coordinates multiple semantic compressors to handle various input types.
    Maintains the deterministic property of the compression layer.
    """

    def __init__(self):
        self._compressors: Dict[str, SemanticCompressor] = {}
        # Register default compressors
        self.register_compressor(ConceptMapper())
        self.register_compressor(PhonemeExtractor())

    def register_compressor(self, compressor: SemanticCompressor):
        """Add or update a specialized compressor."""
        self._compressors[compressor.modality] = compressor

    def process(self, raw_input: Any, modality: str) -> List[SemanticPrimitive]:
        """
        Routes input to the appropriate compressor based on modality.
        """
        if modality not in self._compressors:
            raise ValueError(f"No compressor registered for modality: {modality}")

        return self._compressors[modality].compress(raw_input)
