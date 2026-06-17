import ast
import os
from typing import List, Dict, Set

class ArchitecturalValidator:
    """
    Validates architectural constraints and layer separation.
    Requirement 4.4, 5.4.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        # Defined legal internal dependencies (Simplified)
        # e.g., 'reasoning' should NOT depend on 'reconstruction'
        self.forbidden_deps = {
            "isre.reasoning": {"isre.reconstruction", "isre.compression", "isre.pipeline"},
            "isre.knowledge": {"isre.reconstruction", "isre.reasoning", "isre.pipeline"},
            "isre.reconstruction": {"isre.reasoning", "isre.knowledge", "isre.compression", "isre.pipeline"}
            # Reconstruction can depend on models, but NOT the logic layers.
            # Actually, reconstruction needs ReasoningDecision (models), which is global.
        }

    def validate_layer_separation(self) -> List[str]:
        """
        Scans all files and checks for forbidden imports.
        """
        violations = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.root_dir).replace(os.sep, ".")
                    current_pkg = f"isre.{rel_path.split('.')[0]}"
                    
                    if current_pkg in self.forbidden_deps:
                        imports = self._get_imports(file_path)
                        forbidden = self.forbidden_deps[current_pkg]
                        for imp in imports:
                            for f in forbidden:
                                if imp.startswith(f):
                                    violations.append(f"Separation Violation in {file_path}: Imports {imp}")
        return violations

    def _get_imports(self, file_path: str) -> Set[str]:
        imports = set()
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return set()
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.add(n.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        return imports
