from typing import Protocol, Any, List, Optional, Dict
from hsrai.core.models import SemanticPrimitive
from hsrai.graph.models import IntentGraph
from hsrai.reasoning.hybrid_engine import ReasoningPath
from hsrai.output.models import GeneratedOutput

class Plugin(Protocol):
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        ...

    def shutdown(self) -> None:
        """Clean up resources."""
        ...

class CompressionPlugin(Plugin):
    def process(self, input_data: Any, source_id: str) -> SemanticPrimitive:
        """Convert raw input to semantic primitive."""
        ...

class ReasoningPlugin(Plugin):
    def reason(self, graph: IntentGraph) -> Optional[ReasoningPath]:
        """Find a reasoning path in the graph."""
        ...

class OutputPlugin(Plugin):
    def generate(self, path: ReasoningPath) -> GeneratedOutput:
        """Generate output from reasoning path."""
        ...
