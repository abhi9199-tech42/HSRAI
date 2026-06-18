from isre.types import EdgeType, IntentType, SemanticType


class TestIntentType:
    def test_goal_value(self):
        assert IntentType.GOAL.value == "goal"

    def test_context_value(self):
        assert IntentType.CONTEXT.value == "context"

    def test_query_value(self):
        assert IntentType.QUERY.value == "query"

    def test_constraint_value(self):
        assert IntentType.CONSTRAINT.value == "constraint"

    def test_emotion_value(self):
        assert IntentType.EMOTION.value == "emotion"

    def test_behavioral_pattern_exists(self):
        assert hasattr(IntentType, "BEHAVIORAL_PATTERN")

    def test_behavioral_pattern_value(self):
        assert IntentType.BEHAVIORAL_PATTERN.value == "behavioral_pattern"


class TestEdgeType:
    def test_causal_value(self):
        assert EdgeType.CAUSAL.value == "causal"

    def test_temporal_value(self):
        assert EdgeType.TEMPORAL.value == "temporal"

    def test_logical_value(self):
        assert EdgeType.LOGICAL.value == "logical"

    def test_priority_value(self):
        assert EdgeType.PRIORITY.value == "priority"

    def test_trust_based_exists(self):
        assert hasattr(EdgeType, "TRUST_BASED")

    def test_trust_based_value(self):
        assert EdgeType.TRUST_BASED.value == "trust_based"


class TestSemanticType:
    def test_concept_value(self):
        assert SemanticType.CONCEPT.value == "concept"

    def test_action_value(self):
        assert SemanticType.ACTION.value == "action"

    def test_attribute_value(self):
        assert SemanticType.ATTRIBUTE.value == "attribute"

    def test_relation_value(self):
        assert SemanticType.RELATION.value == "relation"

    def test_entity_value(self):
        assert SemanticType.ENTITY.value == "entity"
