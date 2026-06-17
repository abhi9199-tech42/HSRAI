from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class KnowledgeSourceType(Enum):
    INTERNAL_DB = "internal_db"
    EXTERNAL_API = "external_api"
    BEHAVIORAL_LIBRARY = "behavioral_library"
    PHYSICS_ENGINE = "physics_engine"
    USER_INPUT = "user_input"

@dataclass
class KnowledgeEntry:
    id: str
    content: Any
    source_type: KnowledgeSourceType
    source_id: str
    trust_rating: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeGap:
    description: str
    missing_fields: List[str]
    criticality: float # 0.0 to 1.0
    trust_implication: float # How much this gap affects trust
    required_source_type: Optional[KnowledgeSourceType] = None
