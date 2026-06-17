from enum import Enum, auto
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class IntentType(Enum):
    GOAL = "goal"
    CONTEXT = "context"
    QUERY = "query"
    CONSTRAINT = "constraint"
    EMOTION = "emotion"

class EdgeType(Enum):
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    PRIORITY = "priority"

class SemanticType(Enum):
    CONCEPT = "concept"
    ACTION = "action"
    ATTRIBUTE = "attribute"
    RELATION = "relation"
