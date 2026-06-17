import time
import numpy as np
import statistics

class HSRABenchmark:
    """Performance benchmarks for the HSRAI system."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_compression(self, iterations=100):
        """Benchmark semantic compression (text → SemanticPrimitive)."""
        from hsrai.compression.multimodal import MultiModalProcessor
        processor = MultiModalProcessor()
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            processor.process_text("Analyze the risk of this financial transaction for compliance")
            times.append(time.perf_counter() - start)
        self.results["compression"] = {
            "iterations": iterations,
            "mean_ms": statistics.mean(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
            "p95_ms": sorted(times)[int(iterations * 0.95)] * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
        }
    
    def benchmark_graph_construction(self, iterations=100):
        """Benchmark intent graph construction."""
        from hsrai.graph.builder import IntentGraphBuilder
        from hsrai.core.types import IntentType, EdgeType
        from hsrai.core.models import SemanticPrimitive
        from hsrai.core.types import SemanticType
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            builder = IntentGraphBuilder()
            p = SemanticPrimitive(id="p1", concept="test", type=SemanticType.CONCEPT)
            n1 = builder.create_node(IntentType.GOAL, [p])
            n2 = builder.create_node(IntentType.CONTEXT, [p])
            builder.connect_nodes(n2.id, n1.id, EdgeType.LOGICAL)
            times.append(time.perf_counter() - start)
        self.results["graph_construction"] = {"iterations": iterations, "mean_ms": statistics.mean(times) * 1000}
    
    def benchmark_reasoning(self, iterations=50):
        """Benchmark hybrid reasoning engine."""
        from hsrai.reasoning.hybrid_engine import HybridReasoningEngine
        from hsrai.graph.models import IntentGraph, IntentNode, IntentEdge
        from hsrai.core.types import IntentType, EdgeType
        from hsrai.core.models import SemanticPrimitive
        from hsrai.core.types import SemanticType
        # Build a small graph
        graph = IntentGraph()
        nodes = []
        for i in range(5):
            p = SemanticPrimitive(id=f"p{i}", concept=f"concept_{i}", type=SemanticType.CONCEPT, semantic_weight=0.8)
            node = IntentNode(id=f"n{i}", type=IntentType.GOAL, semantic_payload=[p])
            graph.add_node(node)
            nodes.append(node)
        for i in range(4):
            edge = IntentEdge(source_id=nodes[i].id, target_id=nodes[i+1].id, relationship_type=EdgeType.LOGICAL, weight=0.9)
            graph.add_edge(edge)
        times = []
        for _ in range(iterations):
            engine = HybridReasoningEngine(graph)
            engine.find_paths(nodes[0].id, nodes[4].id)
            start = time.perf_counter()
            for _ in range(20):
                engine.step(dt=0.1)
            times.append(time.perf_counter() - start)
        self.results["reasoning"] = {"iterations": iterations, "mean_ms": statistics.mean(times) * 1000}
    
    def benchmark_trust(self, iterations=100):
        """Benchmark trust certificate generation and verification."""
        from hsrai.trust.verifier import TrustManager
        mgr = TrustManager()
        times_gen = []
        times_verify = []
        for _ in range(iterations):
            start = time.perf_counter()
            cert = mgr.generate_certificate("test content for trust", "out_test")
            times_gen.append(time.perf_counter() - start)
            start = time.perf_counter()
            mgr.verify_certificate(cert)
            times_verify.append(time.perf_counter() - start)
        self.results["trust_generation"] = {"iterations": iterations, "mean_ms": statistics.mean(times_gen) * 1000}
        self.results["trust_verification"] = {"iterations": iterations, "mean_ms": statistics.mean(times_verify) * 1000}
    
    def benchmark_phoneme_mapping(self, iterations=100):
        """Benchmark phoneme to frequency mapping."""
        from hsrai.compression.mapper import PhonemeFrequencyMapper, PhonemeSequence
        mapper = PhonemeFrequencyMapper()
        seq = PhonemeSequence(phonemes=["k", "a", "t", "a"], source_text="kata")
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            mapper.map_sequence(seq)
            times.append(time.perf_counter() - start)
        self.results["phoneme_mapping"] = {"iterations": iterations, "mean_ms": statistics.mean(times) * 1000}
    
    def benchmark_oscillatory_gating(self, iterations=1000):
        """Benchmark oscillatory gating application."""
        from hsrai.reasoning.oscillatory import OscillatoryGating
        gating = OscillatoryGating()
        vec = np.ones(64) * 0.5
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            gating.apply_gating(vec, dt=0.01)
            times.append(time.perf_counter() - start)
        self.results["oscillatory_gating"] = {"iterations": iterations, "mean_ms": statistics.mean(times) * 1000}
    
    def run_all(self):
        print("Running HSRAI Benchmarks...")
        print("=" * 60)
        self.benchmark_compression()
        self.benchmark_graph_construction()
        self.benchmark_reasoning()
        self.benchmark_trust()
        self.benchmark_phoneme_mapping()
        self.benchmark_oscillatory_gating()
        self._print_results()
    
    def _print_results(self):
        print(f"\n{'Benchmark':<30} {'Mean (ms)':<12} {'Median (ms)':<12} {'Iterations':<12}")
        print("-" * 66)
        for name, data in self.results.items():
            mean = data.get('mean_ms', 0)
            median = data.get('median_ms', mean)
            iters = data.get('iterations', 0)
            print(f"{name:<30} {mean:<12.3f} {median:<12.3f} {iters:<12}")
        print("=" * 66)
        print("Benchmarks complete.")

if __name__ == "__main__":
    bench = HSRABenchmark()
    bench.run_all()
