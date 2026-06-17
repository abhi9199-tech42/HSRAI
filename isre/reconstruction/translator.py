from typing import Dict, Any, Type
from .base import OutputReconstructor
from .language import LanguageGenerator
from .code import CodeGenerator
from .action import ActionPlanner
from ..models.reasoning import ReasoningDecision

class MultiFormatTranslator:
    """
    Coordinator for generating output in multiple formats simultaneously.
    Requirement 5.2: Support multiple output languages/formats.
    Requirement 5.3: Express same decision in different formats.
    """
    
    def __init__(self):
        self._reconstructors: Dict[str, OutputReconstructor] = {}
        # Register defaults
        self.register(LanguageGenerator())
        self.register(CodeGenerator())
        self.register(ActionPlanner())

    def register(self, reconstructor: OutputReconstructor):
        self._reconstructors[reconstructor.format_type] = reconstructor

    def translate(self, decision: ReasoningDecision, formats: list[str] = None) -> Dict[str, Any]:
        """
        Translates a single decision into multiple requested formats.
        """
        if formats is None:
            formats = list(self._reconstructors.keys())
            
        results = {}
        for fmt in formats:
            if fmt in self._reconstructors:
                results[fmt] = self._reconstructors[fmt].reconstruct(decision)
            else:
                results[fmt] = f"Error: Format '{fmt}' not supported"
        
        return results
