import asyncio
import logging
import time
from typing import List, Optional

from hsrai.core.utils import deterministic_id
from hsrai.compression.multimodal import MultiModalProcessor
from hsrai.compression.mapper import PhonemeFrequencyMapper
from hsrai.graph.builder import IntentGraphBuilder
from hsrai.graph.models import IntentGraph
from hsrai.core.types import IntentType, EdgeType
from hsrai.reasoning.hybrid_engine import HybridReasoningEngine, ReasoningPath
from hsrai.output.generator import OutputGenerator, GeneratedOutput
from hsrai.trust.verifier import TrustManager
from hsrai.knowledge.query import KnowledgeQueryEngine
from hsrai.system.config import SystemConfig
from hsrai.plugins.manager import PluginManager

logger = logging.getLogger(__name__)


class ObserverManager:
    """Manages observer notifications for graph and reasoning events."""

    def __init__(self):
        self.observers: List = []

    def add(self, observer):
        self.observers.append(observer)

    def notify_graph_built(self, graph: IntentGraph, request_id: str):
        for observer in self.observers:
            if hasattr(observer, 'on_graph_built'):
                try:
                    observer.on_graph_built(graph, request_id)
                except Exception as e:
                    logger.warning("Observer error: %s", e)

    def notify_path_found(self, path: ReasoningPath, request_id: str):
        for observer in self.observers:
            if hasattr(observer, 'on_path_found'):
                try:
                    observer.on_path_found(path, request_id)
                except Exception as e:
                    logger.warning("Observer error: %s", e)


class SystemController:
    """
    Main controller for the HSRAI system.
    Orchestrates the pipeline from input to output.
    """

    def __init__(self, config: SystemConfig = None, plugin_manager: PluginManager = None):
        self.config = config or SystemConfig()
        self.plugin_manager = plugin_manager or PluginManager()

        self.phoneme_mapper = PhonemeFrequencyMapper()
        self.multimodal = MultiModalProcessor(self.phoneme_mapper)
        self.trust_manager = TrustManager()
        self.knowledge_engine = KnowledgeQueryEngine(self.trust_manager)
        self.output_generator = OutputGenerator(self.trust_manager)

        self.observer_mgr = ObserverManager()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

    def add_observer(self, observer):
        self.observer_mgr.add(observer)

    async def process_request(self, input_text: str, request_id: str = None) -> GeneratedOutput:
        if not input_text or not input_text.strip():
            return self._error("Input text cannot be empty", request_id or "empty")

        if request_id is None:
            request_id = f"req_{deterministic_id({'input': input_text})[:8]}"

        async with self.semaphore:
            try:
                return await asyncio.wait_for(
                    self._run_pipeline(input_text, request_id),
                    timeout=self.config.timeout_ms / 1000.0,
                )
            except asyncio.TimeoutError:
                return self._error("Request timed out", request_id)
            except Exception as e:
                return self._error(f"System error: {e}", request_id)

    async def _run_pipeline(self, input_text: str, request_id: str) -> GeneratedOutput:
        primitive = await self._compress(input_text, request_id)
        builder, context_node, goal_node = await self._build_graph(primitive, request_id)
        path = await self._reason(builder, context_node, goal_node, request_id)
        return await self._generate_output(path, request_id)

    async def _compress(self, input_text: str, source_id: str):
        await asyncio.sleep(0.001)
        plugin = self.plugin_manager.get_compression()
        if plugin:
            return plugin.process(input_text, source_id=source_id)
        return self.multimodal.process_text(input_text, source_id=source_id)

    async def _build_graph(self, primitive, request_id: str):
        await asyncio.sleep(0.001)
        builder = IntentGraphBuilder()
        goal_node = builder.create_node(IntentType.GOAL, [primitive])

        context_node = None
        results = self.knowledge_engine.query(primitive.concept)
        if results:
            ctx_prims = [
                self.multimodal.process_text(k.content, source_id="knowledge")
                for k in results[:3]
            ]
            context_node = builder.create_node(IntentType.CONTEXT, ctx_prims)
            builder.connect_nodes(context_node.id, goal_node.id, EdgeType.LOGICAL)

        self.observer_mgr.notify_graph_built(builder.get_graph(), request_id)
        return builder, context_node, goal_node

    async def _reason(self, builder, context_node, goal_node, request_id: str) -> ReasoningPath:
        plugin = self.plugin_manager.get_reasoning()
        if plugin:
            path = plugin.reason(builder.get_graph())
            if path:
                self.observer_mgr.notify_path_found(path, request_id)
                return path

        engine = HybridReasoningEngine(builder.get_graph())
        start_id = context_node.id if context_node else None
        end_id = goal_node.id

        if start_id:
            engine.find_paths(start_id, end_id)
            for _ in range(50):
                converged = engine.step(dt=0.1)
                if converged:
                    self.observer_mgr.notify_path_found(converged, request_id)
                    return converged

        path = ReasoningPath(nodes=[goal_node], edges=[], mu_stability=1.0)
        self.observer_mgr.notify_path_found(path, request_id)
        return path

    async def _generate_output(self, path: ReasoningPath, request_id: str) -> GeneratedOutput:
        plugin = self.plugin_manager.get_output()
        if plugin:
            output = plugin.generate(path)
        else:
            output = self.output_generator.generate_text(path)

        output.metadata["request_id"] = request_id
        output.metadata["processing_time"] = time.time()
        return output

    def _error(self, message: str, request_id: str) -> GeneratedOutput:
        return GeneratedOutput(
            content=f"Error: {message}",
            format="text",
            metadata={"error": True, "request_id": request_id},
        )
