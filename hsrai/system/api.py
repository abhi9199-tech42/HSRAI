from typing import Protocol, Any, Optional
from hsrai.graph.models import IntentGraph
from hsrai.reasoning.hybrid_engine import ReasoningPath
from hsrai.system.controller import SystemController

class GraphObserver(Protocol):
    """Protocol for observing graph construction and reasoning events."""
    def on_graph_built(self, graph: IntentGraph, request_id: str) -> None:
        """Called when the intent graph is constructed, before reasoning."""
        ...
    
    def on_path_found(self, path: ReasoningPath, request_id: str) -> None:
        """Called when a reasoning path is found."""
        ...

class HSRAIApi:
    """
    Public API for HSRAI system integration.
    Allows inspection and modification via observers.
    """
    
    def __init__(self, controller: SystemController):
        self.controller = controller
        
    def register_observer(self, observer: GraphObserver) -> None:
        """Register an observer to receive graph events."""
        self.controller.add_observer(observer)
        
    async def process(self, text: str) -> Any:
        """Process a text request."""
        return await self.controller.process_request(text)
