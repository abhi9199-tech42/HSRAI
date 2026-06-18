import base64
import logging
import os
from datetime import datetime
from typing import Any, List, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from hsrai.core.models import SemanticPrimitive, TrustCertificate
from hsrai.core.types import IntentType, SemanticType
from hsrai.core.utils import deterministic_id
from hsrai.graph.models import IntentNode

logger = logging.getLogger(__name__)

DEFAULT_KEY_PATH = os.environ.get(
    "HSRAI_KEY_PATH",
    os.path.join(os.path.expanduser("~"), ".hsrai", "keys", "ecdsa.pem"),
)

class BehavioralVerifier:
    """
    Verifies alignment with human behavioral patterns and detects anomalies.
    """

    def __init__(self):
        # Baseline heuristics for "human-like" behavior
        # e.g., acceptable intensity ranges for emotions
        self.emotion_intensity_limit = 0.95

    def calculate_alignment_score(self, node: IntentNode) -> float:
        """
        Calculate how well a node aligns with expected behavioral patterns.
        Returns a score between 0.0 (anomalous) and 1.0 (aligned).
        """
        score = 1.0

        # Check for emotional intensity anomalies
        if node.type == IntentType.EMOTION:
            # High intensity emotions might be anomalous or unstable
            # Assume payload has primitives with weights
            max_intensity = max([p.semantic_weight for p in node.semantic_payload], default=0.0)
            if max_intensity > self.emotion_intensity_limit:
                score *= 0.8 # Penalty for extreme intensity

        # Check for non-human semantic types in behavioral contexts
        # (Placeholder logic)

        return score

    def detect_anomalies(self, primitives: List[SemanticPrimitive]) -> List[str]:
        """
        Detect specific anomalies in a list of primitives.
        """
        anomalies = []
        for p in primitives:
            if p.type == SemanticType.ACTION and p.semantic_weight > 1.0:
                anomalies.append(f"Hyper-intense action: {p.id}")
            # Add more heuristics
        return anomalies

class TrustManager:
    """
    Manages cryptographic attestation and trust verification.
    Supports persistent key storage via key_path.
    """

    def __init__(self, issuer_id: str = "HSRAI_CORE", key_path: Optional[str] = None):
        self.issuer_id = issuer_id
        self.key_path = key_path or DEFAULT_KEY_PATH
        self.verifier = BehavioralVerifier()
        self.certificate_chain: List[TrustCertificate] = []

        if self.key_path and os.path.exists(self.key_path):
            self._load_key(self.key_path)
            logger.info("Loaded ECDSA key from %s", self.key_path)
        else:
            self._private_key = ec.generate_private_key(ec.SECP256R1())
            if self.key_path:
                self.save_keys()
                logger.info("Generated and saved new ECDSA key to %s", self.key_path)

        self.public_key = self._private_key.public_key()

    def _load_key(self, path: str) -> None:
        """Load a private key from a PEM file."""
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        with open(path, 'rb') as f:
            self._private_key = load_pem_private_key(f.read(), password=None)

    def save_keys(self) -> None:
        """Save the current private key to key_path."""
        if not self.key_path:
            raise ValueError("No key_path configured; cannot save keys")
        os.makedirs(os.path.dirname(self.key_path) or '.', exist_ok=True)
        with open(self.key_path, 'wb') as f:
            f.write(self._private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption(),
            ))

    def rotate_keys(self) -> None:
        """Generate a new key pair, replacing the current one."""
        self._private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self._private_key.public_key()
        if self.key_path:
            self.save_keys()

    def save_keys_if_configured(self) -> None:
        """Save keys only if a key_path is configured."""
        if self.key_path:
            try:
                self.save_keys()
            except Exception as e:
                logger.warning("Failed to save keys: %s", e)

    def generate_certificate(self, subject: Any, subject_id: str) -> TrustCertificate:
        """
        Generate a TrustCertificate for a given subject (Node, Path, etc.).
        """
        # Calculate Trust Score
        if isinstance(subject, IntentNode):
            trust_score = self.verifier.calculate_alignment_score(subject)
        else:
            trust_score = 1.0 # Default for other objects

        # Create Payload for Signing
        timestamp = datetime.now().timestamp()
        payload = f"{subject_id}:{trust_score}:{timestamp}".encode('utf-8')

        # Sign with Private Key
        signature_bytes = self._private_key.sign(
            payload,
            ec.ECDSA(hashes.SHA256())
        )
        signature = base64.b64encode(signature_bytes).decode('utf-8')

        # Deterministic Certificate ID
        cert_data = {
            "issuer": self.issuer_id,
            "subject": subject_id,
            "score": trust_score,
            "timestamp": timestamp,
            "signature": signature
        }
        cert_id = f"cert_{deterministic_id(cert_data)[:8]}"

        cert = TrustCertificate(
            certificate_id=cert_id,
            issuer_id=self.issuer_id,
            subject_id=subject_id,
            trust_score=trust_score,
            timestamp=timestamp,
            signature=signature,
            claims={"type": str(type(subject))}
        )

        self.certificate_chain.append(cert)
        return cert

    def verify_certificate(self, cert: TrustCertificate) -> bool:
        """
        Verify the validity of a certificate using the public key.
        """
        # 1. Check Trust Score range
        if not (0.0 <= cert.trust_score <= 1.0):
            return False

        # 2. Verify Cryptographic Signature
        try:
            payload = f"{cert.subject_id}:{cert.trust_score}:{cert.timestamp}".encode('utf-8')
            signature_bytes = base64.b64decode(cert.signature)

            self.public_key.verify(
                signature_bytes,
                payload,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except (InvalidSignature, Exception):
            return False
