from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from hsrai.core.models import TrustCertificate

@dataclass
class GeneratedOutput:
    content: str
    format: str # "text", "code", "action_plan"
    trust_certificate: Optional[TrustCertificate] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
