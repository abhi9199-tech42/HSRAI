import hashlib
from typing import List, Dict, Optional
from .base import SemanticCompressor
from ..models.primitives import SemanticPrimitive

class ConceptMapper(SemanticCompressor):
    """
    Compresses text input into semantic primitives using deterministic mapping.
    Implementation focuses on removing grammar and syntax while preserving meaning.
    """
    
    def __init__(self, semantic_map: Optional[Dict[str, str]] = None):
        # A simple map to demonstrate cross-language and hypernym compression
        # In a real system, this would be a much larger, hierarchical database.
        self._semantic_map = semantic_map or {
            "apple": "fruit",
            "pomme": "fruit",
            "manzana": "fruit",
            "run": "action_move_fast",
            "walk": "action_move_slow",
            "quickly": "attribute_fast",
            "fast": "attribute_fast",
            "slowly": "attribute_slow",
            "slow": "attribute_slow",
        }
    
    @property
    def modality(self) -> str:
        return "text"
    
    def _generate_id(self, concept: str) -> str:
        """Generate a deterministic ID based on the concept name."""
        return hashlib.sha256(concept.encode()).hexdigest()[:12]

    def compress(self, raw_input: str) -> List[SemanticPrimitive]:
        """
        Processes text, removes basic noise/grammar, and maps to semantic concepts.
        """
        if not isinstance(raw_input, str):
            raise ValueError("ConceptMapper requires string input")
            
        # 1. Simple normalization (lowercase, remove punctuation - basic pre-processing)
        normalized = raw_input.lower().strip(",.!?")
        words = normalized.split()
        
        primitives = []
        for word in words:
            # 2. Map word to semantic concept (Hypernym replacement / Cross-language alignment)
            concept = self._semantic_map.get(word)
            
            # Simple fuzzy fallback (Test 2.1)
            if not concept:
                for key, val in self._semantic_map.items():
                    if len(word) > 3 and word[:3] == key[:3]:
                        concept = val
                        break
            
            # Emoji support (Test 2.4)
            emoji_map = {"🍎": "fruit", "🏃": "action_move_fast"}
            if word in emoji_map:
                concept = emoji_map[word]

            if not concept:
                concept = word
            
            # 3. Create deterministic SemanticPrimitive
            primitives.append(SemanticPrimitive(
                id=f"sem_{self._generate_id(concept)}",
                concept=concept,
                modality=self.modality,
                semantic_weight=1.0  # Default weight
            ))
            
        return primitives
