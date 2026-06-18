import pytest

from isre.compression.text import ConceptMapper
from isre.models.primitives import SemanticPrimitive


class TestConceptMapper:
    def test_init_defaults(self):
        mapper = ConceptMapper()
        assert mapper.modality == "text"
        assert len(mapper._semantic_map) > 0

    def test_compress_returns_list(self):
        mapper = ConceptMapper()
        result = mapper.compress("hello")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_compress_returns_primitive(self):
        mapper = ConceptMapper()
        result = mapper.compress("apple")
        assert isinstance(result[0], SemanticPrimitive)

    def test_compress_known_word(self):
        mapper = ConceptMapper()
        result = mapper.compress("apple")
        assert result[0].concept == "fruit"

    def test_compress_cross_language(self):
        mapper = ConceptMapper()
        result = mapper.compress("pomme")
        assert result[0].concept == "fruit"

    def test_compress_unknown_word_fallback(self):
        mapper = ConceptMapper()
        result = mapper.compress("xyzunknown")
        assert result[0].concept == "xyzunknown"

    def test_compress_multiple_words(self):
        mapper = ConceptMapper()
        result = mapper.compress("run quickly")
        assert len(result) == 2
        concepts = [p.concept for p in result]
        assert "action_move_fast" in concepts
        assert "attribute_fast" in concepts

    def test_compress_empty_string(self):
        mapper = ConceptMapper()
        result = mapper.compress("")
        assert result == []

    def test_compress_non_string_raises(self):
        mapper = ConceptMapper()
        with pytest.raises(ValueError):
            mapper.compress(123)

    def test_compress_punctuation_stripped(self):
        mapper = ConceptMapper()
        result = mapper.compress("apple.")
        assert result[0].concept == "fruit"

    def test_deterministic_id(self):
        mapper = ConceptMapper()
        a = mapper.compress("apple")
        b = mapper.compress("apple")
        assert a[0].id == b[0].id

    def test_custom_semantic_map(self):
        custom = {"foo": "bar"}
        mapper = ConceptMapper(semantic_map=custom)
        result = mapper.compress("foo")
        assert result[0].concept == "bar"
