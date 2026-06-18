from hypothesis import given
from hypothesis import strategies as st

from hsrai.compression.multimodal import MultiModalProcessor
from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import SemanticType

# --- Strategies ---

@st.composite
def voice_input_strategy(draw):
    phonemes = draw(st.lists(st.text(min_size=1, max_size=2, alphabet="abcdef"), min_size=1))
    source_text = draw(st.text(min_size=1))
    return phonemes, source_text

# --- Tests ---

class TestMultiModalProcessing:

    def setup_method(self):
        self.processor = MultiModalProcessor()

    @given(st.text(min_size=1))
    def test_text_processing_consistency(self, text):
        """Property 3: Cross-modal semantic consistency - Text"""
        primitive = self.processor.process_text(text)

        assert isinstance(primitive, SemanticPrimitive)
        assert primitive.modality == "text"
        assert primitive.type == SemanticType.CONCEPT
        assert primitive.concept == text[:50]
        assert "source_length" in primitive.compression_metadata
        assert primitive.compression_metadata["source_length"] == len(text)

    @given(voice_input_strategy())
    def test_voice_processing_consistency(self, input_data):
        """Property 3: Cross-modal semantic consistency - Voice"""
        phonemes, source_text = input_data
        primitive = self.processor.process_voice(phonemes, source_text)

        assert isinstance(primitive, SemanticPrimitive)
        assert primitive.modality == "voice"
        assert primitive.type == SemanticType.ACTION
        assert 0.0 <= primitive.semantic_weight <= 1.0
        assert "phoneme_count" in primitive.compression_metadata
        assert primitive.compression_metadata["phoneme_count"] == len(phonemes)

    @given(st.text(min_size=1), st.floats(min_value=0.0, max_value=1.0))
    def test_behavior_processing_consistency(self, signal, intensity):
        """Property 3: Cross-modal semantic consistency - Behavior"""
        primitive = self.processor.process_behavior(signal, intensity)

        assert isinstance(primitive, SemanticPrimitive)
        assert primitive.modality == "behavior"
        assert primitive.type == SemanticType.ATTRIBUTE
        assert primitive.semantic_weight == intensity
        assert primitive.concept == signal

    @given(st.text(min_size=1), st.floats(allow_nan=True))
    def test_sensor_processing_consistency(self, sensor_id, value):
        """Property 3: Cross-modal semantic consistency - Sensor"""
        primitive = self.processor.process_sensor(sensor_id, value)

        assert isinstance(primitive, SemanticPrimitive)
        assert primitive.modality == "sensor"
        assert primitive.type == SemanticType.ENTITY
        assert primitive.semantic_weight == 1.0

        # Handle NaN comparison
        import math
        stored_value = primitive.compression_metadata["value"]
        if math.isnan(value):
            assert math.isnan(stored_value)
        else:
            assert stored_value == value
