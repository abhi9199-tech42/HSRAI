"""
Unified μ-Resonance Cognitive Mesh (URCM) - A frequency-based reasoning system.

This package implements a revolutionary artificial reasoning system that replaces 
discrete token-based processing with continuous frequency-based representations.
"""

__version__ = "0.1.0"
__author__ = "URCM Development Team"

from .core.data_models import AttractorState, MeshSignal, ReasoningPath, ResonanceState
from hsrai.common.phoneme import FrequencyPath, PhonemeSequence

__all__ = [
    "PhonemeSequence",
    "FrequencyPath",
    "ResonanceState",
    "AttractorState",
    "ReasoningPath",
    "MeshSignal"
]
