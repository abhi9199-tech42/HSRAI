import asyncio
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from hsrai.core.utils import deterministic_id
from hsrai.compression.multimodal import MultiModalProcessor
from hsrai.compression.mapper import PhonemeFrequencyMapper
from hsrai.graph.builder import IntentGraphBuilder
from hsrai.core.types import IntentType, SemanticType
from hsrai.reasoning.hybrid_engine import HybridReasoningEngine
from hsrai.output.generator import OutputGenerator, GeneratedOutput
from hsrai.trust.verifier import TrustManager
from hsrai.knowledge.query import KnowledgeQueryEngine

from hsrai.system.config import SystemConfig
from hsrai.plugins.manager import PluginManager

logger = logging.getLogger(__name__)

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
        
        self.observers = []
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
    def add_observer(self, observer):
        """Add a graph observer for inspection/modification."""
        self.observers.append(observer)
        
    async def process_request(self, input_text: str, request_id: str = None) -> GeneratedOutput:
        """
        Process a text request through the full pipeline.
        """
        if not input_text or not input_text.strip():
            return self._create_error_response("Input text cannot be empty", request_id or "empty")
        
        if request_id is None:
            # Deterministic Request ID based on input content
            # This ensures that the same input produces the same trace and semantic artifacts
            request_id = f"req_{deterministic_id({'input': input_text})[:8]}"
            
        async with self.semaphore:
            try:
                # Enforce timeout
                return await asyncio.wait_for(
                    self._process_pipeline(input_text, request_id),
                    timeout=self.config.timeout_ms / 1000.0
                )
            except asyncio.TimeoutError:
                return self._create_error_response("Request timed out", request_id)
            except Exception as e:
                return self._create_error_response(f"System error: {str(e)}", request_id)

    async def _process_pipeline(self, input_text: str, request_id: str) -> GeneratedOutput:
        # Yield control to allow cancellation/timeout checks
        await asyncio.sleep(0.001)
        
        # 1. Input Processing
        compression_plugin = self.plugin_manager.get_compression()
        if compression_plugin:
            primitive = compression_plugin.process(input_text, source_id=request_id)
        else:
            primitive = self.multimodal.process_text(input_text, source_id=request_id)
        
        await asyncio.sleep(0.001) # Yield again
        
        # 2. Graph Construction (Per-request isolation)
        builder = IntentGraphBuilder()
        
        # Create Goal Node from input
        goal_node = builder.create_node(IntentType.GOAL, [primitive])
        
        # 3. Knowledge Integration (Simulated context enrichment)
        # Query for related info
        knowledge_results = self.knowledge_engine.query(primitive.concept)
        if knowledge_results:
            # Add context node
            context_prims = [
                self.multimodal.process_text(k.content, source_id="knowledge") 
                for k in knowledge_results[:3]
            ]
            context_node = builder.create_node(IntentType.CONTEXT, context_prims)
            # Link context to goal
            from hsrai.core.types import EdgeType
            builder.connect_nodes(context_node.id, goal_node.id, EdgeType.LOGICAL)
            
        # Notify observers (Graph Inspection/Modification point)
        for observer in self.observers:
            if hasattr(observer, 'on_graph_built'):
                try:
                    observer.on_graph_built(builder.get_graph(), request_id)
                except Exception as e:
                    logger.warning("Observer error: %s", e)

        # 4. Reasoning
        reasoning_plugin = self.plugin_manager.get_reasoning()
        path = None
        
        if reasoning_plugin:
            path = reasoning_plugin.reason(builder.get_graph())
        
        if not path:
            # Default reasoning
            engine = HybridReasoningEngine(builder.get_graph())
            
            # Determine start node (Context) and end node (Goal)
            start_node_id = context_node.id if 'context_node' in locals() else None
            end_node_id = goal_node.id
            
            if start_node_id:
                # Try to find path from Context to Goal
                engine.find_paths(start_node_id, end_node_id)
                
                # Run oscillatory convergence loop
                for _ in range(50): # Max iterations
                    converged_path = engine.step(dt=0.1)
                    if converged_path:
                        path = converged_path
                        break
            
            if not path:
                # Fallback: Trivial path containing just the goal node
                from hsrai.reasoning.hybrid_engine import ReasoningPath
                path = ReasoningPath(nodes=[goal_node], edges=[], mu_stability=1.0)
        
        # Notify observers
        for observer in self.observers:
            if hasattr(observer, 'on_path_found'):
                try:
                    observer.on_path_found(path, request_id)
                except Exception as e:
                    logger.warning("Observer error: %s", e)

        # 5. Output Generation
        output_plugin = self.plugin_manager.get_output()
        if output_plugin:
            output = output_plugin.generate(path)
        else:
            # Default output generation
            output = self.output_generator.generate_text(path)
        
        # Attach trace metadata
        output.metadata["request_id"] = request_id
        output.metadata["processing_time"] = time.time()
        
        return output

    def _create_error_response(self, message: str, request_id: str) -> GeneratedOutput:
        return GeneratedOutput(
            content=f"Error: {message}",
            format="text",
            metadata={"error": True, "request_id": request_id}
        )
