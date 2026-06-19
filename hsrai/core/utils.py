import hashlib
import json
from enum import Enum
from typing import Any, Dict


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
            # Sort dict keys for deterministic serialization
            return {k: obj.__dict__[k] for k in sorted(obj.__dict__.keys())}
        if isinstance(obj, dict):
            return {k: obj[k] for k in sorted(obj.keys())}
        if isinstance(obj, (list, tuple, set)):
            return list(obj)
        return str(obj)

    # Use sort_keys=True and a consistent separator for reproducibility
    canonical = json.dumps(
        data,
        default=_default_serializer,
        sort_keys=True,
        separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()
