import pytest
import numpy as np
from hsrai.core.models import SemanticPrimitive, ResonanceState, TrustCertificate
from hsrai.core.types import IntentType, EdgeType, SemanticType
from hsrai.graph.models import IntentNode, IntentEdge, IntentGraph
from hsrai.compression.mapper import PhonemeFrequencyMapper, PhonemeSequence
from hsrai.reasoning.oscillatory import OscillatoryGating

def test_semantic_primitive():
    primitive = SemanticPrimitive(
        id="prim_1",
        concept="test_concept",
        type=SemanticType.CONCEPT
    )
    assert primitive.id == "prim_1"
    assert primitive.concept == "test_concept"

def test_resonance_state():
    state = ResonanceState(
        resonance_vector=np.zeros(10),
        mu_value=0.5,
        rho_density=1.0,
        chi_cost=2.0,
        stability_score=0.8,
        oscillation_phase=np.pi,
        timestamp=100.0
    )
    assert state.mu_value == 0.5
    assert state.oscillation_phase == np.pi

def test_intent_graph():
    graph = IntentGraph()
    node = IntentNode(
        id="node_1",
        type=IntentType.GOAL,
        semantic_payload=[]
    )
    graph.add_node(node)
    assert "node_1" in graph.nodes

def test_phoneme_mapper():
    mapper = PhonemeFrequencyMapper(frequency_dim=24)
    seq = PhonemeSequence(phonemes=['a', 'k', 'a'], source_text="aka")
    path = mapper.map_sequence(seq)
    assert path.vectors.shape == (3, 24)

def test_oscillatory_gating():
    gating = OscillatoryGating(resonance_dim=24)
    vec = np.ones(24)
    gated = gating.apply_gating(vec)
    assert gated.shape == (24,)

if __name__ == "__main__":
    test_semantic_primitive()
    test_resonance_state()
    test_intent_graph()
    test_phoneme_mapper()
    test_oscillatory_gating()
    print("All structure tests passed!")
