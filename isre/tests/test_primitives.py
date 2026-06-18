from hsrai.common.types import SemanticType
from isre.models.primitives import SemanticPrimitive


class TestSemanticPrimitive:
    def test_valid_construction(self):
        sp = SemanticPrimitive(id="sp_1", concept="test_concept")
        assert sp.id == "sp_1"
        assert sp.concept == "test_concept"
        assert sp.type == SemanticType.CONCEPT
        assert sp.semantic_weight == 1.0
        assert sp.modality == "text"

    def test_construction_with_explicit_fields(self):
        sp = SemanticPrimitive(
            id="sp_2",
            concept="action_move",
            type=SemanticType.ACTION,
            semantic_weight=0.8,
            modality="speech",
        )
        assert sp.type == SemanticType.ACTION
        assert sp.semantic_weight == 0.8
        assert sp.modality == "speech"

    def test_hash_equality_same_id(self):
        a = SemanticPrimitive(id="sp_x", concept="alpha")
        b = SemanticPrimitive(id="sp_x", concept="beta")
        assert hash(a) == hash(b)
        assert a == b

    def test_inequality_different_id(self):
        a = SemanticPrimitive(id="sp_1", concept="alpha")
        b = SemanticPrimitive(id="sp_2", concept="alpha")
        assert a != b

    def test_inequality_non_primitive(self):
        sp = SemanticPrimitive(id="sp_1", concept="alpha")
        assert sp != "sp_1"

    def test_default_compression_metadata(self):
        sp = SemanticPrimitive(id="sp_3", concept="x")
        assert sp.compression_metadata == {}
