import hashlib
from typing import Any, List

from ..models.primitives import SemanticPrimitive
from .base import SemanticCompressor


class PhonemeExtractor(SemanticCompressor):
    """
    Simulates extracting semantic primitives from speech via phonemic representation.
    In a full implementation, this would interface with a phoneme recognition model.
    """

    @property
    def modality(self) -> str:
        return "speech"

    def _generate_id(self, concept: str) -> str:
        return hashlib.sha256(concept.encode()).hexdigest()[:12]

    def compress(self, raw_input: Any) -> List[SemanticPrimitive]:
        """
        Simulates phoneme-to-semantic conversion.
        Input is expected to be a list of phoneme strings or a simulated audio signal.
        """
        # For the prototype, we assume input might be a string of phonemes
        if isinstance(raw_input, str):
            phonemes = raw_input.split()
        elif isinstance(raw_input, list):
            phonemes = raw_input
        else:
            raise ValueError("PhonemeExtractor requires string or list of phonemes")

        # Simulate mapping common phoneme patterns to concepts
        # e.g., /'æp.əl/ -> apple -> fruit
        phoneme_map = {
            "æp.əl": "fruit",
            "rʌn": "action_move_fast",
        }

        primitives = []
        for p in phonemes:
            concept = phoneme_map.get(p, f"audio_cluster_{p}")
            primitives.append(SemanticPrimitive(
                id=f"sem_ph_{self._generate_id(concept)}",
                concept=concept,
                modality=self.modality
            ))

        return primitives
