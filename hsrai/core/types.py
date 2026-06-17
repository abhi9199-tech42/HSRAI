from enum import Enum

class IntentType(Enum):
    """Classification of intent types in the reasoning graph."""
    GOAL = "goal"
    CONTEXT = "context"
    QUERY = "query"
    CONSTRAINT = "constraint"
    EMOTION = "emotion"
    BEHAVIORAL_PATTERN = "behavioral_pattern" # Added for HSRAI

class EdgeType(Enum):
    """Types of semantic relationships between intent nodes."""
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    PRIORITY = "priority"
    TRUST_BASED = "trust_based" # Added for HSRAI

class SemanticType(Enum):
    """Categories of semantic primitives in the knowledge system."""
    CONCEPT = "concept"
    ACTION = "action"
    ATTRIBUTE = "attribute"
    RELATION = "relation"
    ENTITY = "entity"
