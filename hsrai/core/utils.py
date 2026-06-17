import hashlib
import json
from typing import Dict, Any, Union
from enum import Enum

def deterministic_id(data: Dict[str, Any]) -> str:
    """
    Generate a deterministic ID based on the dictionary content.
    Sorts keys and uses a consistent separator to ensure reproducibility.
    Handles Enums and other common types.
    """
    def _default_serializer(obj):
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    # Use sort_keys=True and a consistent separator for reproducibility
    canonical = json.dumps(
        data, 
        default=_default_serializer,
        sort_keys=True, 
        separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()
