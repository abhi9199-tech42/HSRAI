import logging
from typing import Any, Dict, List, Protocol

from hsrai.core.utils import deterministic_id

logger = logging.getLogger(__name__)
from hsrai.knowledge.models import KnowledgeEntry, KnowledgeGap, KnowledgeSourceType
from hsrai.trust.verifier import TrustManager


class KnowledgeSource(Protocol):
    def query(self, query_string: str, **kwargs) -> List[KnowledgeEntry]:
        ...

    def get_trust_rating(self) -> float:
        ...

class InMemoryKnowledgeBase:
    def __init__(self, source_type: KnowledgeSourceType, default_trust: float = 1.0):
        self.data: Dict[str, Any] = {}
        self.source_type = source_type
        self.default_trust = default_trust

    def add_entry(self, key: str, value: Any):
        self.data[key] = value

    def query(self, query_string: str, **kwargs) -> List[KnowledgeEntry]:
        # Simple exact match or substring search for simulation
        results = []
        for key, value in self.data.items():
            if query_string.lower() in key.lower() or query_string.lower() in str(value).lower():
                # Deterministic ID
                entry_id = f"entry_{deterministic_id({'content': str(value), 'key': key, 'source': self.source_type.value})[:8]}"
                entry = KnowledgeEntry(
                    id=entry_id,
                    content=value,
                    source_type=self.source_type,
                    source_id=self.source_type.value,
                    trust_rating=self.default_trust,
                    metadata={"key": key}
                )
                results.append(entry)
        return results

    def get_trust_rating(self) -> float:
        return self.default_trust

class KnowledgeQueryEngine:
    """
    Central hub for querying various knowledge sources.
    """

    def __init__(self, trust_manager: TrustManager = None):
        self.sources: Dict[str, KnowledgeSource] = {}
        self.trust_manager = trust_manager or TrustManager()

        # Initialize default sources
        self.behavioral_library = InMemoryKnowledgeBase(KnowledgeSourceType.BEHAVIORAL_LIBRARY, default_trust=0.95)
        self.physics_engine = InMemoryKnowledgeBase(KnowledgeSourceType.PHYSICS_ENGINE, default_trust=0.99)

        self.register_source("behavioral_lib", self.behavioral_library)
        self.register_source("physics_engine", self.physics_engine)

    def register_source(self, source_id: str, source: KnowledgeSource):
        self.sources[source_id] = source

    def query(self, query_string: str, required_trust: float = 0.0) -> List[KnowledgeEntry]:
        """
        Query all registered sources and filter by trust rating.
        """
        all_results = []
        for source in self.sources.values():
            if source.get_trust_rating() >= required_trust:
                try:
                    results = source.query(query_string)
                    all_results.extend(results)
                except Exception as e:
                    logger.warning("Error querying source: %s", e)

        return all_results

    def detect_gaps(self, query_string: str, results: List[KnowledgeEntry]) -> List[KnowledgeGap]:
        """
        Analyze query and results to detect missing information.
        (Simplified heuristic implementation)
        """
        gaps = []

        # Heuristic: If no results found, it's a gap
        if not results:
            gaps.append(KnowledgeGap(
                description=f"No information found for '{query_string}'",
                missing_fields=["all"],
                criticality=0.8,
                trust_implication=0.5
            ))
            return gaps

        # Check if results come from trusted sources
        max_trust = max([r.trust_rating for r in results])
        if max_trust < 0.5:
            gaps.append(KnowledgeGap(
                description="Information found but trust rating is low",
                missing_fields=["verification"],
                criticality=0.6,
                trust_implication=0.9
            ))

        return gaps
