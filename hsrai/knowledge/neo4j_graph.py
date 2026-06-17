"""
Neo4j-backed knowledge graph for HSRAI.

Provides a real graph database backend for knowledge storage and retrieval,
replacing the in-memory dictionary with persistent, queryable relationships.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from hsrai.core.utils import deterministic_id
from hsrai.knowledge.models import KnowledgeEntry, KnowledgeSourceType

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"
    max_connection_pool_size: int = 50


class Neo4jKnowledgeGraph:
    """
    Neo4j-backed knowledge graph implementing the KnowledgeSource protocol.

    Stores knowledge as nodes and relationships in a graph database,
    enabling complex queries like:
    - "Find all entities related to this transaction"
    - "What are the risk factors connected to this account?"
    - "Trace the path between two entities"

    Falls back to in-memory storage if Neo4j is not available.
    """

    def __init__(self, config: Neo4jConfig = None, source_type: KnowledgeSourceType = None):
        self.config = config or Neo4jConfig()
        self.source_type = source_type or KnowledgeSourceType.INTERNAL_DB
        self.default_trust = 0.95
        self._driver = None
        self._fallback_data: Dict[str, Any] = {}
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to Neo4j. Returns True if successful, falls back to memory.
        """
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password),
                max_connection_pool_size=self.config.max_connection_pool_size,
            )
            # Verify connection
            self._driver.verify_connectivity()
            self._connected = True
            logger.info("Connected to Neo4j at %s", self.config.uri)
            self._create_indexes()
            return True
        except Exception as e:
            logger.warning("Neo4j unavailable, using in-memory fallback: %s", e)
            self._connected = False
            return False

    def _create_indexes(self):
        """Create indexes for efficient querying."""
        if not self._connected:
            return
        with self._driver.session(database=self.config.database) as session:
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (t:Transaction) ON (t.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (a:Account) ON (a.id)")

    def close(self):
        if self._driver:
            self._driver.close()

    def add_entity(self, name: str, entity_type: str, properties: Dict[str, Any] = None):
        """Add an entity node to the graph."""
        if not self._connected:
            key = f"{entity_type}:{name}"
            self._fallback_data[key] = properties or {}
            return

        props = properties or {}
        props["name"] = name
        props["type"] = entity_type

        with self._driver.session(database=self.config.database) as session:
            session.run(
                f"MERGE (n:{entity_type} {{name: $name}}) SET n += $props",
                name=name, props=props
            )

    def add_relationship(self, from_name: str, to_name: str, rel_type: str, properties: Dict[str, Any] = None):
        """Add a relationship between two entities."""
        if not self._connected:
            return

        props = properties or {}
        with self._driver.session(database=self.config.database) as session:
            session.run(
                f"MATCH (a {{name: $from_name}}), (b {{name: $to_name}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props",
                from_name=from_name, to_name=to_name, props=props
            )

    def add_transaction(self, tx_id: str, amount: float, merchant: str,
                       account_id: str, timestamp: str, properties: Dict[str, Any] = None):
        """Add a transaction node with relationships."""
        props = properties or {}
        props.update({
            "id": tx_id,
            "amount": amount,
            "merchant": merchant,
            "timestamp": timestamp,
        })

        self.add_entity(tx_id, "Transaction", props)
        self.add_entity(account_id, "Account", {"id": account_id})
        self.add_relationship(account_id, tx_id, "MADE_TRANSACTION", {"amount": amount})
        self.add_entity(merchant, "Merchant", {"name": merchant})
        self.add_relationship(tx_id, merchant, "SENT_TO")

    def query(self, query_string: str, **kwargs) -> List[KnowledgeEntry]:
        """
        Query the knowledge graph. Supports:
        - Entity name lookup
        - Relationship traversal
        - Pattern matching
        """
        results = []

        if not self._connected:
            # Fallback: substring search
            for key, value in self._fallback_data.items():
                if query_string.lower() in key.lower():
                    entry = KnowledgeEntry(
                        id=f"entry_{deterministic_id({'key': key})[:8]}",
                        content=value,
                        source_type=self.source_type,
                        source_id=self.source_type.value,
                        trust_rating=self.default_trust,
                        metadata={"key": key, "backend": "memory"}
                    )
                    results.append(entry)
            return results

        with self._driver.session(database=self.config.database) as session:
            # Try entity name match
            result = session.run(
                "MATCH (n) WHERE n.name CONTAINS $query OR n.id CONTAINS $query "
                "RETURN n LIMIT 10",
                query=query_string
            )
            for record in result:
                node = record["n"]
                entry = KnowledgeEntry(
                    id=f"entry_{deterministic_id({'node': dict(node)})[:8]}",
                    content=dict(node),
                    source_type=self.source_type,
                    source_id=self.source_type.value,
                    trust_rating=self.default_trust,
                    metadata={"node_id": node.element_id if hasattr(node, 'element_id') else None}
                )
                results.append(entry)

        return results

    def get_trust_rating(self) -> float:
        return self.default_trust

    def get_entity_neighbors(self, entity_name: str, depth: int = 1) -> List[Dict]:
        """Get neighboring entities up to given depth."""
        if not self._connected:
            return []

        with self._driver.session(database=self.config.database) as session:
            result = session.run(
                "MATCH (n {name: $name})-[r*1..$depth]-(m) "
                "RETURN DISTINCT m.name AS name, m.type AS type LIMIT 20",
                name=entity_name, depth=depth
            )
            return [dict(record) for record in result]

    def get_risk_factors(self, account_id: str) -> List[Dict]:
        """Get risk factors associated with an account."""
        if not self._connected:
            return []

        with self._driver.session(database=self.config.database) as session:
            result = session.run(
                "MATCH (a:Account {id: $account_id})-[:MADE_TRANSACTION]->(t:Transaction) "
                "WHERE t.amount > 10000 OR t.flagged = true "
                "RETURN t.id AS tx_id, t.amount AS amount, t.merchant AS merchant "
                "ORDER BY t.amount DESC LIMIT 10",
                account_id=account_id
            )
            return [dict(record) for record in result]

    def seed_fraud_data(self):
        """Seed the graph with sample fraud detection data."""
        # Accounts
        self.add_entity("ACC001", "Account", {"balance": 50000, "risk_score": 0.2})
        self.add_entity("ACC002", "Account", {"balance": 12000, "risk_score": 0.8})
        self.add_entity("ACC003", "Account", {"balance": 95000, "risk_score": 0.1})

        # Merchants
        self.add_entity("OnlineShopX", "Merchant", {"category": "electronics", "country": "NG"})
        self.add_entity("LocalGrocery", "Merchant", {"category": "grocery", "country": "US"})
        self.add_entity("WireTransferSvc", "Merchant", {"category": "finance", "country": "RU"})

        # Transactions
        self.add_transaction("TX001", 250.00, "LocalGrocery", "ACC001", "2026-01-15")
        self.add_transaction("TX002", 15000.00, "OnlineShopX", "ACC002", "2026-01-16")
        self.add_transaction("TX003", 8500.00, "WireTransferSvc", "ACC002", "2026-01-16")
        self.add_transaction("TX004", 50.00, "LocalGrocery", "ACC003", "2026-01-17")

        # Risk relationships
        self.add_entity("HighRiskPattern", "RiskFactor", {"pattern": "rapid_high_value", "severity": 0.9})
        self.add_entity("GeoAnomaly", "RiskFactor", {"pattern": "foreign_merchant", "severity": 0.6})
        self.add_relationship("ACC002", "HighRiskPattern", "EXHIBITS")
        self.add_relationship("TX002", "GeoAnomaly", "TRIGGERS")
