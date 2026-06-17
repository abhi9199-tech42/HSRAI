from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from ..types import SemanticType

class SemanticPrimitive(BaseModel):
    """
    Base unit of meaning in the ISRE.
    Represents a compressed, pre-linguistic concept.
    """
    id: str
    concept: str
    semantic_weight: float = 1.0
    modality: str = "text"
    compression_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, SemanticPrimitive):
            return False
        return self.id == other.id
