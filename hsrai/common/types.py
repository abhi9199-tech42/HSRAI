from enum import Enum

class IntentType(Enum):
    GOAL = "goal"
    CONTEXT = "context"
    QUERY = "query"
    CONSTRAINT = "constraint"
    EMOTION = "emotion"
    BEHAVIORAL_PATTERN = "behavioral_pattern" # Added for HSRAI

class EdgeType(Enum):
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    PRIORITY = "priority"
    TRUST_BASED = "trust_based" # Added for HSRAI

class SemanticType(Enum):
    CONCEPT = "concept"
    ACTION = "action"
    ATTRIBUTE = "attribute"
    RELATION = "relation"
    ENTITY = "entity"
