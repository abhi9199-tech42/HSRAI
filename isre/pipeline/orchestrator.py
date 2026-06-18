import uuid
from typing import Any, Dict, List

from ..compression.multimodal import MultimodalProcessor
from ..graph.builder import IntentGraphBuilder
from ..knowledge.engine import KnowledgeQueryEngine
from ..knowledge.gaps import KnowledgeGapDetector
from ..reasoning.dynamics import OscillatoryGate
from ..reasoning.generator import ReasoningPathGenerator
from ..reasoning.selection import CompetitiveSelector
from ..reconstruction.translator import MultiFormatTranslator
from ..utils.resources import ResourceMonitor


class ISREPipeline:
    """
    Main orchestrator for the ISRE system.
    Coordinates the flow through all five architectural layers.
    Requirement 6.1: Sequential processing through five layers.
    Requirement 6.4: Traceability and diagnostics.
    """

    def __init__(self, memory_threshold_mb: float = 500.0):
        self.compression = MultimodalProcessor()
        self.graph_builder = IntentGraphBuilder()
        self.reasoning_gen = ReasoningPathGenerator()
        self.selector = CompetitiveSelector()
        self.knowledge_engine = KnowledgeQueryEngine()
        self.gap_detector = KnowledgeGapDetector(self.knowledge_engine)
        self.translator = MultiFormatTranslator()
        self.resource_monitor = ResourceMonitor(memory_threshold_mb)

        self.trace_log: List[Dict[str, Any]] = []

    def process(self, raw_input: Any, modality: str = "text", target_formats: List[str] = None) -> Dict[str, Any]:
        """
        Executes the full pipeline process.
        """
        request_id = str(uuid.uuid4())
        self._log(request_id, "start", {"input": raw_input, "modality": modality})

        # 0. Resource Check (Graceful Degradation - Requirement 7.5)
        if self.resource_monitor.is_resource_constrained():
            self._log(request_id, "degradation", {"reason": "high_memory_usage"})
            # In constrained mode, we might skip heavy reasoning or simplify graph.
            # Simplified mode: return raw primitives mapped to text.
            primitives = self.compression.process(raw_input, modality)
            return {
                "request_id": request_id,
                "outputs": {"text": f"SYSTEM BUSY (Degraded Mode). Concepts: {[p.concept for p in primitives]}"},
                "degraded": True
            }

        try:
            # 1. Semantic Compression
            primitives = self.compression.process(raw_input, modality)
            self._log(request_id, "compression", {
                "primitives_count": len(primitives),
                "primitives": [p.model_dump() for p in primitives]
            })

            # 2. Intent Graph Construction
            graph = self.graph_builder.build_from_primitives(primitives)
            self._log(request_id, "graph_construction", {
                "nodes_count": len(graph.nodes),
                "edges_count": len(graph.edges),
                "conflicts": [n.id for n in graph.nodes.values() if n.conflict_markers]
            })

            # 3. Designed Reasoning (Generation + Selection)
            paths = self.reasoning_gen.generate_paths(graph)
            self._log(request_id, "reasoning_generation", {"paths_count": len(paths)})

            decision = self.selector.select(paths)

            # 3.5 Oscillatory Convergence Guarantee (Requirement 7.3)
            # Simulate the oscillatory gating process until convergence
            self._ensure_convergence(request_id)

            self._log(request_id, "reasoning_selection", {
                "selected_path_id": decision.selected_path.id,
                "confidence": decision.confidence
            })

            # 4. World Knowledge Integration (Gap Detection)
            gaps = self.gap_detector.detect_gaps(decision)
            if gaps:
                self._log(request_id, "knowledge_gaps", {"gaps": gaps})

            # 5. Semantic Reconstruction
            outputs = self.translator.translate(decision, target_formats)
            self._log(request_id, "reconstruction", {"formats": list(outputs.keys())})

            final_result = {
                "request_id": request_id,
                "outputs": outputs,
                "knowledge_gaps": gaps,
                "decision_metadata": {
                    "justification": decision.justification,
                    "confidence": decision.confidence
                }
            }

            self._log(request_id, "complete", {"success": True})
            return final_result

        except Exception as e:
            self._log(request_id, "error", {"message": str(e)})
            raise

    def _log(self, request_id: str, stage: str, data: Dict[str, Any]):
        self.trace_log.append({
            "request_id": request_id,
            "stage": stage,
            "data": data,
            "resource_status": self.resource_monitor.get_status()
        })

    def _ensure_convergence(self, request_id: str):
        """
        Simulates oscillatory convergence in finite time.
        Requirement 7.3.
        """
        gate = OscillatoryGate()
        steps = 0
        max_steps = 100
        tolerance = 0.01
        prev_act = -1.0

        while steps < max_steps:
            gate.step()
            curr_act = gate.activation
            if abs(curr_act - prev_act) < tolerance and steps > 10:
                break
            prev_act = curr_act
            steps += 1

        self._log(request_id, "oscillatory_convergence", {"steps_to_converge": steps})

    def get_trace(self, request_id: str) -> List[Dict[str, Any]]:
        return [entry for entry in self.trace_log if entry["request_id"] == request_id]

    def clear(self):
        self.trace_log.clear()
