import pytest
from hypothesis import given, strategies as st
from hsrai.core.models import SemanticPrimitive
from hsrai.graph.models import IntentNode
from hsrai.core.types import IntentType, SemanticType
from hsrai.trust.verifier import TrustManager, BehavioralVerifier

class TestTrustVerification:
    
    def setup_method(self):
        self.manager = TrustManager()
        self.verifier = BehavioralVerifier()

    def test_certificate_generation(self):
        """Verify certificate structure and generation"""
        node = IntentNode(
            id="test_node",
            type=IntentType.GOAL,
            semantic_payload=[]
        )
        
        cert = self.manager.generate_certificate(node, node.id)
        
        assert cert.issuer_id == self.manager.issuer_id
        assert cert.subject_id == node.id
        assert 0.0 <= cert.trust_score <= 1.0
        assert len(cert.signature) > 64 # ECDSA signature (base64) is longer than 64 chars

    def test_behavioral_scoring(self):
        """Verify behavioral alignment scoring"""
        # Normal node
        normal_node = IntentNode(
            id="normal",
            type=IntentType.GOAL,
            semantic_payload=[]
        )
        score_normal = self.verifier.calculate_alignment_score(normal_node)
        assert score_normal == 1.0
        
        # Anomalous node (High intensity emotion)
        anomalous_node = IntentNode(
            id="intense",
            type=IntentType.EMOTION,
            semantic_payload=[
                SemanticPrimitive(id="p1", concept="rage", type=SemanticType.ATTRIBUTE, semantic_weight=1.0)
            ]
        )
        # Note: The threshold in code is 0.95, so 1.0 triggers penalty
        score_anomalous = self.verifier.calculate_alignment_score(anomalous_node)
        assert score_anomalous < 1.0

    def test_trust_verification_valid(self):
        """Verify that a legitimately generated certificate validates"""
        node = IntentNode(
            id="test_valid",
            type=IntentType.GOAL,
            semantic_payload=[]
        )
        cert = self.manager.generate_certificate(node, node.id)
        assert self.manager.verify_certificate(cert)

    def test_trust_verification_tampered(self):
        """Verify that a tampered certificate fails verification"""
        node = IntentNode(
            id="test_tamper",
            type=IntentType.GOAL,
            semantic_payload=[]
        )
        cert = self.manager.generate_certificate(node, node.id)
        
        # Tamper with the score
        cert.trust_score = 0.5 # Change score
        # Signature should now be invalid for this payload
        assert not self.manager.verify_certificate(cert)

    def test_invalid_certificate(self):
        """Verify rejection of invalid certificates"""
        import uuid
        import time
        from hsrai.core.models import TrustCertificate
        
        # Invalid score
        with pytest.raises(ValueError):
             TrustCertificate(
                certificate_id=str(uuid.uuid4()),
                issuer_id="TEST",
                subject_id="SUB",
                trust_score=1.5, # Invalid
                timestamp=time.time(),
                signature="valid_looking_signature"
            )
            
        # Invalid signature content (garbage base64 or non-base64)
        cert_bad_sig = TrustCertificate(
            certificate_id=str(uuid.uuid4()),
            issuer_id="TEST",
            subject_id="SUB",
            trust_score=0.5,
            timestamp=time.time(),
            signature="not_a_valid_base64_signature"
        )
        
        assert not self.manager.verify_certificate(cert_bad_sig)
