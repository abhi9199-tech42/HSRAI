"""
NLP-powered semantic compression using sentence-transformers.

Converts raw text into high-dimensional semantic embeddings that capture
meaning beyond surface-level text matching.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List

import numpy as np

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import SemanticType
from hsrai.core.utils import deterministic_id

logger = logging.getLogger(__name__)


class NLPCompressor:
    """
    Real NLP compression using sentence-transformers.

    Converts text to 384-dimensional semantic embeddings using the
    all-MiniLM-L6-v2 model (or any sentence-transformers model).

    This replaces the trivial text[:50] truncation with actual
    semantic understanding.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize the NLP compressor.

        Args:
            model_name: Sentence-transformers model name
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        self._embedding_dim = None
        self._load_lock = asyncio.Lock()

    def _load_model(self):
        """Lazy load the sentence-transformers model (thread-safe)."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device=self.device)
            self._embedding_dim = self._model.get_embedding_dimension()
            logger.info("Loaded NLP model: %s (dim=%d)", self.model_name, self._embedding_dim)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for NLP compression. "
                "Install with: pip install sentence-transformers"
            )

    async def _load_model_async(self):
        """Thread-safe async lazy load."""
        async with self._load_lock:
            if self._model is not None:
                return
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device=self.device)
                self._embedding_dim = self._model.get_embedding_dimension()
                logger.info("Loaded NLP model: %s (dim=%d)", self.model_name, self._embedding_dim)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for NLP compression. "
                    "Install with: pip install sentence-transformers"
                )

    @property
    def embedding_dim(self) -> int:
        self._load_model()
        return self._embedding_dim

    def embed(self, text: str) -> np.ndarray:
        """
        Convert text to a semantic embedding vector.

        Args:
            text: Input text

        Returns:
            Normalized embedding vector of shape (embedding_dim,)
        """
        self._load_model()
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple texts to embeddings.

        Args:
            texts: List of input texts

        Returns:
            Array of shape (n_texts, embedding_dim)
        """
        self._load_model()
        embeddings = self._model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings

    def similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Similarity score in [-1, 1]
        """
        emb_a = self.embed(text_a)
        emb_b = self.embed(text_b)
        return float(np.dot(emb_a, emb_b))

    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify the intent of a text using semantic similarity to
        predefined intent categories.

        Returns:
            Dict mapping intent labels to confidence scores
        """
        intent_labels = {
            "question": "What is the meaning of life?",
            "command": "Execute the following task immediately.",
            "statement": "The sky is blue today.",
            "request": "Could you please help me with this?",
        }

        text_emb = self.embed(text)
        scores = {}
        for label, example in intent_labels.items():
            example_emb = self.embed(example)
            scores[label] = float(np.dot(text_emb, example_emb))

        # Normalize to probabilities via softmax
        exp_scores = {k: np.exp(v) for k, v in scores.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Simple entity extraction using pattern matching.
        For production, use spaCy NER.

        Returns:
            List of dicts with 'text' and 'label' keys
        """
        import re
        entities = []

        # Extract numbers (potential amounts, IDs)
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            entities.append({"text": match.group(), "label": "NUMBER"})

        # Extract capitalized words (potential names, places)
        for match in re.finditer(r'\b[A-Z][a-z]+\b', text):
            entities.append({"text": match.group(), "label": "ENTITY"})

        # Extract dates
        for match in re.finditer(r'\b\d{4}-\d{2}-\d{2}\b', text):
            entities.append({"text": match.group(), "label": "DATE"})

        # Extract email addresses
        for match in re.finditer(r'\b[\w.-]+@[\w.-]+\.\w+\b', text):
            entities.append({"text": match.group(), "label": "EMAIL"})

        return entities

    def compress_to_primitive(self, text: str, source_id: str = "user") -> SemanticPrimitive:
        """
        Full compression pipeline: text → embedding → SemanticPrimitive.

        The embedding is stored in compression_metadata for downstream
        reasoning engines to use.
        """
        embedding = self.embed(text)
        entities = self.extract_entities(text)
        intents = self.classify_intent(text)

        # Deterministic ID
        id_data = {
            "type": SemanticType.CONCEPT.value,
            "concept": text[:100],
            "modality": "text",
            "source_id": source_id,
            "embedding_hash": hashlib.sha256(embedding.tobytes()).hexdigest(),
        }
        sem_id = f"nlp_{deterministic_id(id_data)[:12]}"

        # Determine primary intent
        primary_intent = max(intents, key=intents.get)

        # Map intent to SemanticType
        intent_type_map = {
            "question": SemanticType.CONCEPT,
            "command": SemanticType.ACTION,
            "statement": SemanticType.CONCEPT,
            "request": SemanticType.ACTION,
        }

        return SemanticPrimitive(
            id=sem_id,
            concept=text[:100],
            type=intent_type_map.get(primary_intent, SemanticType.CONCEPT),
            semantic_weight=float(np.linalg.norm(embedding)),
            modality="text",
            compression_metadata={
                "source_length": len(text),
                "source_id": source_id,
                "timestamp": datetime.now().isoformat(),
                "embedding": embedding.tolist(),
                "embedding_dim": len(embedding),
                "model": self.model_name,
                "entities": entities,
                "intents": intents,
                "primary_intent": primary_intent,
            }
        )
