import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import composite
import numpy as np
import math

from hsrai.core.models import SemanticPrimitive, ResonanceState, TrustCertificate
from hsrai.core.types import IntentType, EdgeType, SemanticType
from hsrai.graph.models import IntentNode, IntentEdge

# --- Strategies ---

@composite
def semantic_primitive_strategy(draw):
    return SemanticPrimitive(
        id=draw(st.text(min_size=1)),
        concept=draw(st.text(min_size=1)),
        type=draw(st.sampled_from(SemanticType)),
        semantic_weight=draw(st.floats(min_value=0.0, max_value=1.0)),
        modality=draw(st.sampled_from(["text", "voice", "sensor"])),
        compression_metadata=draw(st.dictionaries(st.text(), st.text()))
    )

@composite
def resonance_state_strategy(draw):
    dim = draw(st.integers(min_value=16, max_value=64))
    rho = draw(st.floats(min_value=0.0, max_value=100.0))
    chi = draw(st.floats(min_value=0.1, max_value=100.0)) # Avoid 0 division
    
    # Calculate mu approx to pass validation
    mu_calc = rho / (chi + 1e-9)
    
    return ResonanceState(
        resonance_vector=np.array(draw(st.lists(st.floats(min_value=-1, max_value=1), min_size=dim, max_size=dim))),
        mu_value=mu_calc, 
        rho_density=rho,
        chi_cost=chi,
        stability_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        oscillation_phase=draw(st.floats(min_value=0.0, max_value=2*math.pi)),
        timestamp=draw(st.floats(min_value=0.0))
    )

@composite
def trust_certificate_strategy(draw):
    return TrustCertificate(
        certificate_id=draw(st.text(min_size=1)),
        issuer_id=draw(st.text(min_size=1)),
        subject_id=draw(st.text(min_size=1)),
        trust_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        timestamp=draw(st.floats(min_value=0.0)),
        signature=draw(st.text(min_size=10)),
        claims=draw(st.dictionaries(st.text(), st.text()))
    )

@composite
def intent_node_strategy(draw):
    return IntentNode(
        id=draw(st.text(min_size=1)),
        type=draw(st.sampled_from(IntentType)),
        semantic_payload=draw(st.lists(semantic_primitive_strategy(), max_size=5)),
        activation_level=draw(st.floats(min_value=0.0, max_value=1.0)),
        behavioral_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        conflict_markers=draw(st.lists(st.dictionaries(st.text(), st.text()), max_size=3))
    )

# --- Tests ---

class TestCoreDataModels:
    
    @given(semantic_primitive_strategy())
    def test_semantic_primitive_properties(self, primitive):
        """Property 1: Data model validation consistency - SemanticPrimitive"""
        assert isinstance(primitive.id, str)
        assert len(primitive.id) > 0
        assert isinstance(primitive.type, SemanticType)
        assert 0.0 <= primitive.semantic_weight <= 1.0

    @given(resonance_state_strategy())
    def test_resonance_state_consistency(self, state):
        """Property 1: Data model validation consistency - ResonanceState"""
        # Verify Mu calculation constraint: mu = rho / chi
        expected_mu = state.rho_density / (state.chi_cost + 1e-9)
        assert np.isclose(state.mu_value, expected_mu, rtol=1e-3)
        
        # Verify Phase constraint
        assert 0 <= state.oscillation_phase <= 2 * np.pi
        
        # Verify vector dimensions
        assert state.resonance_vector.ndim == 1

    @given(trust_certificate_strategy())
    def test_trust_certificate_validity(self, cert):
        """Property 1: Data model validation consistency - TrustCertificate"""
        assert 0.0 <= cert.trust_score <= 1.0
        assert len(cert.signature) > 0

    @given(intent_node_strategy())
    def test_intent_node_properties(self, node):
        """Property 1: Data model validation consistency - IntentNode"""
        assert isinstance(node.id, str)
        assert isinstance(node.type, IntentType)
        
        # Check payload integrity
        for primitive in node.semantic_payload:
            assert isinstance(primitive, SemanticPrimitive)

    @given(st.floats(min_value=-1.0, max_value=2.0))
    def test_trust_certificate_validation_logic(self, score):
        """Verify that invalid trust scores raise ValueError"""
        if score < 0.0 or score > 1.0:
            with pytest.raises(ValueError):
                TrustCertificate(
                    certificate_id="test",
                    issuer_id="me",
                    subject_id="you",
                    trust_score=score,
                    timestamp=1.0,
                    signature="sig"
                )
