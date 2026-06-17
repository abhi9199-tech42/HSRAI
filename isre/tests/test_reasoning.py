import pytest
from isre.models.reasoning import ReasoningPath, ReasoningDecision
from isre.models.intent import IntentNode
from hsrai.common.types import IntentType, SemanticType
from hsrai.common.models import SemanticPrimitive


def _make_node(nid="n1", ntype=IntentType.GOAL):
    return IntentNode(
        id=nid,
        type=ntype,
        semantic_payload=[SemanticPrimitive(id=f"p_{nid}", concept="test", type=SemanticType.CONCEPT)],
    )


class TestReasoningPath:
    def test_construction_minimal(self):
        path = ReasoningPath(id="path_1", steps=[])
        assert path.id == "path_1"
        assert path.steps == []
        assert path.intent_satisfaction_score == 0.0
        assert path.constraint_compliance_score == 0.0
        assert path.semantic_coherence_score == 0.0
        assert path.oscillation_state == {}
        assert path.metadata == {}

    def test_construction_with_steps(self):
        nodes = [_make_node("n1"), _make_node("n2")]
        path = ReasoningPath(
            id="path_2",
            steps=nodes,
            intent_satisfaction_score=0.8,
            constraint_compliance_score=0.9,
            semantic_coherence_score=0.7,
        )
        assert len(path.steps) == 2
        assert path.intent_satisfaction_score == 0.8
        assert path.constraint_compliance_score == 0.9
        assert path.semantic_coherence_score == 0.7

    def test_construction_with_metadata(self):
        path = ReasoningPath(
            id="path_3",
            steps=[_make_node("n1")],
            metadata={"strategy": "Direct Execution", "scale": 1.0},
            oscillation_state={"phase": 0.5, "frequency": 2.0},
        )
        assert path.metadata["strategy"] == "Direct Execution"
        assert path.oscillation_state["phase"] == 0.5


class TestReasoningDecision:
    def test_construction(self):
        path = ReasoningPath(id="path_1", steps=[_make_node("n1")])
        decision = ReasoningDecision(
            selected_path=path,
            justification="Best path based on coherence",
            confidence=0.85,
            alternative_paths=[],
        )
        assert decision.selected_path.id == "path_1"
        assert decision.justification == "Best path based on coherence"
        assert decision.confidence == 0.85
        assert decision.alternative_paths == []

    def test_construction_with_alternatives(self):
        p1 = ReasoningPath(id="path_1", steps=[_make_node("n1")])
        p2 = ReasoningPath(id="path_2", steps=[_make_node("n2")])
        decision = ReasoningDecision(
            selected_path=p1,
            justification="Selected",
            confidence=0.7,
            alternative_paths=[p2],
            convergence_metadata={"oscillation_steps": 10},
        )
        assert len(decision.alternative_paths) == 1
        assert decision.convergence_metadata["oscillation_steps"] == 10
