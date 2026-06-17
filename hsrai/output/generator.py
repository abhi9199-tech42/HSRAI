from typing import List, Dict, Any, Optional

from hsrai.core.models import SemanticPrimitive, TrustCertificate
from hsrai.core.types import SemanticType
from hsrai.core.utils import deterministic_id
from hsrai.reasoning.hybrid_engine import ReasoningPath
from hsrai.output.models import GeneratedOutput
from hsrai.trust.verifier import TrustManager

class OutputGenerator:
    """
    Reconstructs semantic decisions into human-readable formats 
    (Text, Code, Action Plans) and embeds trust certificates.
    """
    
    def __init__(self, trust_manager: TrustManager = None):
        self.trust_manager = trust_manager or TrustManager()
        
    def _primitives_to_text(self, primitives: List[SemanticPrimitive]) -> str:
        """Helper to convert primitives to text."""
        concepts = [p.concept for p in primitives]
        return " ".join(concepts)

    def generate_text(self, path: ReasoningPath) -> GeneratedOutput:
        """
        Generate natural language explanation of the reasoning path.
        """
        # Collect concepts from nodes
        sentences = []
        for node in path.nodes:
            text = self._primitives_to_text(node.semantic_payload)
            if text:
                sentences.append(f"[{node.type.value}]: {text}")
                
        content = "\n".join(sentences)
        
        # Generate Certificate for the output content
        out_id = f"out_{deterministic_id({'content': content, 'type': 'text'})[:8]}"
        cert = self.trust_manager.generate_certificate(content, out_id)
        
        return GeneratedOutput(
            content=content,
            format="text",
            trust_certificate=cert,
            metadata={"path_length": path.length, "mu_stability": path.mu_stability}
        )

    def generate_code(self, path: ReasoningPath, language: str = "python") -> GeneratedOutput:
        """
        Generate executable code from the reasoning path.
        """
        lines = []
        for node in path.nodes:
            # Simple heuristic: Action types -> function calls, Concepts -> variables
            for p in node.semantic_payload:
                if p.type == SemanticType.ACTION:
                    lines.append(f"{p.concept}()")
                elif p.type == SemanticType.CONCEPT:
                    lines.append(f"# Process {p.concept}")
                    
        content = "\n".join(lines)
        
        code_id = f"code_{deterministic_id({'content': content, 'type': 'code', 'language': language})[:8]}"
        cert = self.trust_manager.generate_certificate(content, code_id)
        
        return GeneratedOutput(
            content=content,
            format="code",
            trust_certificate=cert,
            metadata={"language": language}
        )

    def generate_action_plan(self, path: ReasoningPath) -> GeneratedOutput:
        """
        Generate a structured action plan.
        """
        steps = []
        for i, node in enumerate(path.nodes):
            actions = [p.concept for p in node.semantic_payload if p.type == SemanticType.ACTION]
            if actions:
                steps.append(f"Step {i+1}: {', '.join(actions)}")
                
        content = "\n".join(steps)
        
        plan_id = f"plan_{deterministic_id({'content': content, 'type': 'plan'})[:8]}"
        cert = self.trust_manager.generate_certificate(content, plan_id)
        
        return GeneratedOutput(
            content=content,
            format="action_plan",
            trust_certificate=cert,
            metadata={"steps_count": len(steps)}
        )
