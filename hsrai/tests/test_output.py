import pytest
from hypothesis import given, strategies as st
from hsrai.output.generator import OutputGenerator
from hsrai.output.models import GeneratedOutput
from hsrai.reasoning.hybrid_engine import ReasoningPath
from hsrai.graph.models import IntentNode, IntentEdge
from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import IntentType, SemanticType, EdgeType

class TestOutputReconstruction:
    
    def setup_method(self):
        self.generator = OutputGenerator()
        
        # Create a dummy path
        p1 = SemanticPrimitive(id="p1", concept="analyze_data", type=SemanticType.ACTION)
        p2 = SemanticPrimitive(id="p2", concept="secure_connection", type=SemanticType.CONCEPT)
        
        n1 = IntentNode(id="n1", type=IntentType.GOAL, semantic_payload=[p1])
        n2 = IntentNode(id="n2", type=IntentType.CONSTRAINT, semantic_payload=[p2])
        
        edge = IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.LOGICAL)
        
        self.path = ReasoningPath(nodes=[n1, n2], edges=[edge])

    def test_text_generation_consistency(self):
        """Property 13: Multi-format semantic equivalence - Text"""
        output = self.generator.generate_text(self.path)
        
        assert isinstance(output, GeneratedOutput)
        assert output.format == "text"
        # Check semantic preservation
        assert "analyze_data" in output.content
        assert "secure_connection" in output.content
        assert "[goal]" in output.content.lower() or "[constraint]" in output.content.lower()

    def test_code_generation_consistency(self):
        """Property 13: Multi-format semantic equivalence - Code"""
        output = self.generator.generate_code(self.path)
        
        assert output.format == "code"
        # Actions should become calls
        assert "analyze_data()" in output.content
        # Concepts should be comments
        assert "# Process secure_connection" in output.content

    def test_trust_certificate_integrity(self):
        """Property 14: Trust certificate integrity"""
        output = self.generator.generate_text(self.path)
        
        assert output.trust_certificate is not None
        assert output.trust_certificate.issuer_id == "HSRAI_CORE"
        # Verify the certificate using the generator's trust manager
        assert self.generator.trust_manager.verify_certificate(output.trust_certificate)

    @given(st.text(min_size=1))
    def test_arbitrary_content_cert_generation(self, text):
        """Verify cert generation works for arbitrary content"""
        # Manually invoke internal method or similar path if possible, 
        # or just create a path with random text
        
        p = SemanticPrimitive(id="p", concept=text, type=SemanticType.CONCEPT)
        n = IntentNode(id="n", type=IntentType.GOAL, semantic_payload=[p])
        path = ReasoningPath(nodes=[n], edges=[])
        
        output = self.generator.generate_text(path)
        
        assert output.trust_certificate is not None
        assert self.generator.trust_manager.verify_certificate(output.trust_certificate)
