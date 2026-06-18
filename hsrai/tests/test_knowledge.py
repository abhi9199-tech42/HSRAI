from hypothesis import given
from hypothesis import strategies as st

from hsrai.knowledge.models import KnowledgeSourceType
from hsrai.knowledge.query import InMemoryKnowledgeBase, KnowledgeQueryEngine


class TestKnowledgeIntegration:

    def setup_method(self):
        self.engine = KnowledgeQueryEngine()

        # Populate some data
        self.engine.behavioral_library.add_entry("greeting", "Hello, how can I help?")
        self.engine.behavioral_library.add_entry("anger_response", "I understand you are upset.")
        self.engine.physics_engine.add_entry("gravity", "9.81 m/s^2")

    @given(st.text(min_size=1))
    def test_source_verification(self, query):
        """Property 11: Knowledge source verification"""
        # If we query something, results should have valid source types and trust ratings
        results = self.engine.query(query)

        for result in results:
            assert isinstance(result.source_type, KnowledgeSourceType)
            assert 0.0 <= result.trust_rating <= 1.0
            assert result.content is not None

    def test_gap_detection_accuracy(self):
        """Property 12: Gap detection accuracy"""
        # Case 1: Known info
        results = self.engine.query("gravity")
        gaps = self.engine.detect_gaps("gravity", results)
        assert len(gaps) == 0 or (len(gaps) == 1 and gaps[0].description != "No information found for 'gravity'")

        # Case 2: Unknown info
        results_unknown = self.engine.query("quantum_flux_capacitor_specs")
        gaps_unknown = self.engine.detect_gaps("quantum_flux_capacitor_specs", results_unknown)

        assert len(gaps_unknown) > 0
        assert "No information found" in gaps_unknown[0].description
        assert gaps_unknown[0].criticality > 0.0

    def test_trust_filtering(self):
        """Verify trust-based filtering"""
        # Add a low trust source
        low_trust_source = InMemoryKnowledgeBase(KnowledgeSourceType.USER_INPUT, default_trust=0.2)
        low_trust_source.add_entry("rumor", "The sky is green")
        self.engine.register_source("untrusted", low_trust_source)

        # Query with high requirement
        results_strict = self.engine.query("rumor", required_trust=0.8)
        assert len(results_strict) == 0

        # Query with low requirement
        results_lax = self.engine.query("rumor", required_trust=0.1)
        assert len(results_lax) == 1
        assert results_lax[0].content == "The sky is green"
