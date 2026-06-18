from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from hsrai.core.models import TrustCertificate


@dataclass
class GeneratedOutput:
    """Output produced by the reasoning engine with optional trust verification."""
    content: str
    format: str # "text", "code", "action_plan"
    trust_certificate: Optional[TrustCertificate] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
