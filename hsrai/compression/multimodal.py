from typing import List, Dict, Any, Union
import numpy as np
from datetime import datetime

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import SemanticType
from hsrai.core.utils import deterministic_id
from hsrai.compression.mapper import PhonemeFrequencyMapper, PhonemeSequence

class MultiModalProcessor:
    """
    Unified processor for handling multi-modal inputs (text, voice, behavior, sensor)
    and converting them into standard SemanticPrimitives.
    """
    
    def __init__(self, phoneme_mapper: PhonemeFrequencyMapper = None):
        self.phoneme_mapper = phoneme_mapper or PhonemeFrequencyMapper()
        
    def process_text(self, text: str, source_id: str = "user") -> SemanticPrimitive:
        """
        Process raw text input into a SemanticPrimitive.
        """
        # In a full implementation, this would involve NLP/NER.
        # Here we perform basic extraction.
        
        # Deterministic ID generation
        id_data = {
            "type": SemanticType.CONCEPT.value,
            "concept": text[:50],
            "modality": "text",
            "source_id": source_id,
            "source_length": len(text)
        }
        sem_id = f"text_{deterministic_id(id_data)[:8]}"
        
        return SemanticPrimitive(
            id=sem_id,
            concept=text[:50], # Truncate for concept label
            type=SemanticType.CONCEPT,
            semantic_weight=1.0,
            modality="text",
            compression_metadata={
                "source_length": len(text),
                "source_id": source_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    def process_voice(self, phonemes: List[str], source_text: str = "", source_id: str = "user") -> SemanticPrimitive:
        """
        Process phoneme sequence from voice input.
        """
        sequence = PhonemeSequence(phonemes=phonemes, source_text=source_text or "voice_input")
        freq_path = self.phoneme_mapper.map_sequence(sequence)
        
        # Calculate semantic density based on path smoothness
        # Smoother paths (lower score) might indicate higher coherence? 
        # For now, we normalize smoothness to a weight.
        normalized_weight = 1.0 / (1.0 + freq_path.smoothness_score)
        
        # Deterministic ID generation
        id_data = {
            "type": SemanticType.ACTION.value,
            "concept": source_text[:50] or "voice_command",
            "modality": "voice",
            "source_id": source_id,
            "phonemes": phonemes
        }
        sem_id = f"voice_{deterministic_id(id_data)[:8]}"
        
        return SemanticPrimitive(
            id=sem_id,
            concept=source_text[:50] or "voice_command",
            type=SemanticType.ACTION, # Voice is often action-oriented
            semantic_weight=normalized_weight,
            modality="voice",
            compression_metadata={
                "phoneme_count": len(phonemes),
                "smoothness": freq_path.smoothness_score,
                "frequency_dim": self.phoneme_mapper.K,
                "source_id": source_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    def process_behavior(self, signal_type: str, intensity: float, context: Dict[str, Any] = None) -> SemanticPrimitive:
        """
        Process behavioral signals (e.g., gaze, gesture, tone).
        """
        # Deterministic ID generation
        id_data = {
            "type": SemanticType.ATTRIBUTE.value,
            "concept": signal_type,
            "modality": "behavior",
            "intensity": intensity,
            "context": context or {}
        }
        sem_id = f"behav_{deterministic_id(id_data)[:8]}"

        return SemanticPrimitive(
            id=sem_id,
            concept=signal_type,
            type=SemanticType.ATTRIBUTE, # Behavioral signals often modify context
            semantic_weight=max(0.0, min(1.0, intensity)),
            modality="behavior",
            compression_metadata={
                "signal_type": signal_type,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
        )

    def process_sensor(self, sensor_id: str, value: float, unit: str = "") -> SemanticPrimitive:
        """
        Process raw sensor data.
        """
        # Deterministic ID generation
        id_data = {
            "type": SemanticType.ENTITY.value,
            "concept": f"{sensor_id}_{value}",
            "modality": "sensor",
            "sensor_id": sensor_id,
            "value": value,
            "unit": unit
        }
        sem_id = f"sens_{deterministic_id(id_data)[:8]}"

        return SemanticPrimitive(
            id=sem_id,
            concept=f"{sensor_id}_{value}",
            type=SemanticType.ENTITY, # Sensors represent physical entities/states
            semantic_weight=1.0, # Sensor data is usually "ground truth"
            modality="sensor",
            compression_metadata={
                "sensor_id": sensor_id,
                "value": value,
                "unit": unit,
                "timestamp": datetime.now().isoformat()
            }
        )
