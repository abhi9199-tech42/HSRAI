
import pytest

from hsrai.core.types import IntentType
from hsrai.graph.models import IntentGraph, IntentNode
from hsrai.system.api import HSRAIApi
from hsrai.system.controller import SystemController


class MockObserver:
    def __init__(self):
        self.graph_captured = None
        self.path_captured = None
        self.request_id = None

    def on_graph_built(self, graph: IntentGraph, request_id: str) -> None:
        self.graph_captured = graph
        self.request_id = request_id
        # Modification test: Add a node
        graph.nodes["injected"] = IntentNode(
            id="injected",
            type=IntentType.CONSTRAINT,
            semantic_payload=[],
            behavioral_score=1.0
        )

    def on_path_found(self, path, request_id: str) -> None:
        self.path_captured = path

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_api_inspection_modification():
    """Verify API allows inspection and modification of the graph."""
    controller = SystemController()
    api = HSRAIApi(controller)
    observer = MockObserver()

    api.register_observer(observer)

    # Run request
    await api.process("Hello world")

    # Verify inspection
    assert observer.graph_captured is not None
    assert observer.path_captured is not None
    assert observer.request_id is not None

    # Verify modification (injected node should exist in the captured graph)
    assert "injected" in observer.graph_captured.nodes

    # Note: Whether the injected node affects reasoning depends on the engine,
    # but the graph object itself should retain the modification.
