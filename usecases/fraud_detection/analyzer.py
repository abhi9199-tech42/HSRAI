"""
HSRAI Fraud Detection Engine.

Demonstrates real-world usage of the HSRAI reasoning pipeline
for financial transaction fraud detection.

Uses deterministic reasoning + knowledge graph + NLP compression
to analyze transactions and produce auditable risk assessments.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import numpy as np

from hsrai.compression.nlp import NLPCompressor
from hsrai.graph.builder import IntentGraphBuilder
from hsrai.graph.models import IntentGraph
from hsrai.core.types import IntentType, EdgeType, SemanticType
from hsrai.core.models import SemanticPrimitive
from hsrai.reasoning.hybrid_engine import HybridReasoningEngine, ReasoningPath
from hsrai.knowledge.neo4j_graph import Neo4jKnowledgeGraph, Neo4jConfig
from hsrai.trust.verifier import TrustManager
from hsrai.output.models import GeneratedOutput

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """A financial transaction to analyze."""
    tx_id: str
    amount: float
    merchant: str
    merchant_category: str
    country: str
    account_id: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Result of fraud analysis on a transaction."""
    transaction_id: str
    risk_score: float  # 0.0 (safe) to 1.0 (fraud)
    risk_level: str  # "low", "medium", "high", "critical"
    risk_factors: List[str]
    reasoning_path: Optional[ReasoningPath] = None
    recommendations: List[str] = field(default_factory=list)
    trust_certificate_id: Optional[str] = None
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class FraudDetector:
    """
    Production-grade fraud detection using HSRAI reasoning pipeline.
    
    Pipeline:
    1. NLP Compression — Embed transaction description + context
    2. Knowledge Graph — Pull account history, merchant risk, patterns
    3. Intent Graph — Build reasoning graph with risk constraints
    4. Hybrid Reasoning — Oscillatory convergence on risk assessment
    5. Trust Certificate — Cryptographically sign the assessment
    """
    
    # Risk thresholds
    THRESHOLDS = {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.8,
        "critical": 0.95,
    }
    
    # Fraud rules (weight, description)
    RULES = [
        (0.3, "High-value transaction (>$10,000)"),
        (0.2, "Foreign merchant in high-risk country"),
        (0.25, "Multiple transactions in short time window"),
        (0.15, "Merchant category mismatch with account history"),
        (0.1, "Transaction amount deviates from account average"),
        (0.35, "Known fraud pattern match"),
    ]
    
    HIGH_RISK_COUNTRIES = {"NG", "RU", "CN", "PK", "IR"}
    
    def __init__(self, neo4j_config: Neo4jConfig = None):
        self.nlp = NLPCompressor()
        self.trust_manager = TrustManager()
        self.knowledge = Neo4jKnowledgeGraph(config=neo4j_config)
        self.knowledge.connect()
        self.knowledge.seed_fraud_data()
        self._request_count = 0
    
    def analyze(self, transaction: Transaction) -> RiskAssessment:
        """
        Analyze a transaction for fraud risk.
        
        Returns a deterministic, auditable RiskAssessment with
        a cryptographic trust certificate.
        """
        start_time = time.perf_counter()
        self._request_count += 1
        
        # Step 1: Compress transaction with NLP
        primitive = self._compress_transaction(transaction)
        
        # Step 2: Query knowledge graph for context
        context = self._query_knowledge(transaction)
        
        # Step 3: Build reasoning graph
        graph, risk_factors = self._build_graph(transaction, primitive, context)
        
        # Step 4: Run hybrid reasoning
        path = self._reason(graph, risk_factors)
        
        # Step 5: Calculate risk score
        risk_score = self._calculate_risk(transaction, risk_factors, path)
        risk_level = self._classify_risk(risk_score)
        recommendations = self._generate_recommendations(risk_level, transaction)
        
        # Step 6: Generate trust certificate
        cert = self.trust_manager.generate_certificate(
            f"Fraud assessment: {transaction.tx_id} -> {risk_level} ({risk_score:.3f})",
            f"fraud_{transaction.tx_id}"
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return RiskAssessment(
            transaction_id=transaction.tx_id,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            reasoning_path=path,
            recommendations=recommendations,
            trust_certificate_id=cert.certificate_id,
            processing_time_ms=elapsed_ms,
            metadata={
                "account_id": transaction.account_id,
                "amount": transaction.amount,
                "merchant": transaction.merchant,
                "model": self.nlp.model_name,
                "knowledge_backend": "neo4j" if self.knowledge._connected else "memory",
            }
        )
    
    def analyze_batch(self, transactions: List[Transaction]) -> List[RiskAssessment]:
        """Analyze multiple transactions."""
        return [self.analyze(tx) for tx in transactions]
    
    def _compress_transaction(self, tx: Transaction) -> SemanticPrimitive:
        """NLP compression of transaction into semantic primitive."""
        description = (
            f"Transaction {tx.tx_id}: ${tx.amount:.2f} at {tx.merchant} "
            f"({tx.merchant_category}) in {tx.country} by account {tx.account_id}"
        )
        return self.nlp.compress_to_primitive(description, source_id=tx.account_id)
    
    def _query_knowledge(self, tx: Transaction) -> Dict[str, Any]:
        """Query knowledge graph for transaction context."""
        context = {
            "account_history": [],
            "merchant_risk": [],
            "similar_fraud": [],
        }
        
        # Query account transactions
        account_results = self.knowledge.query(tx.account_id)
        context["account_history"] = account_results
        
        # Query merchant
        merchant_results = self.knowledge.query(tx.merchant)
        context["merchant_risk"] = merchant_results
        
        # Get risk factors
        risk_factors = self.knowledge.get_risk_factors(tx.account_id)
        context["similar_fraud"] = risk_factors
        
        return context
    
    def _build_graph(self, tx: Transaction, primitive: SemanticPrimitive, 
                     context: Dict) -> tuple:
        """Build intent graph with risk constraints."""
        builder = IntentGraphBuilder()
        risk_factors = []
        
        # Transaction node
        tx_node = builder.create_node(
            IntentType.CONTEXT,
            [primitive],
            behavioral_score=primitive.semantic_weight
        )
        
        # Goal: determine if fraudulent
        goal_node = builder.create_node(
            IntentType.GOAL,
            [SemanticPrimitive(
                id=f"goal_{tx.tx_id}",
                concept="Determine transaction fraud risk",
                type=SemanticType.CONCEPT,
                semantic_weight=1.0
            )]
        )
        
        # Rule 1: High-value transaction
        if tx.amount > 10000:
            risk_factors.append(self.RULES[0])
            constraint = builder.create_node(
                IntentType.CONSTRAINT,
                [SemanticPrimitive(
                    id=f"rule_high_value_{tx.tx_id}",
                    concept="High-value transaction detected",
                    type=SemanticType.CONCEPT,
                    semantic_weight=0.8
                )]
            )
            builder.connect_nodes(constraint.id, goal_node.id, EdgeType.PRIORITY, weight=0.9)
        
        # Rule 2: Foreign high-risk country
        if tx.country in self.HIGH_RISK_COUNTRIES:
            risk_factors.append(self.RULES[1])
            constraint = builder.create_node(
                IntentType.CONSTRAINT,
                [SemanticPrimitive(
                    id=f"rule_foreign_{tx.tx_id}",
                    concept=f"Foreign merchant in {tx.country}",
                    type=SemanticType.CONCEPT,
                    semantic_weight=0.7
                )]
            )
            builder.connect_nodes(constraint.id, goal_node.id, EdgeType.PRIORITY, weight=0.7)
        
        # Rule 6: Known fraud pattern
        if context.get("similar_fraud"):
            risk_factors.append(self.RULES[5])
            constraint = builder.create_node(
                IntentType.CONSTRAINT,
                [SemanticPrimitive(
                    id=f"rule_pattern_{tx.tx_id}",
                    concept="Known fraud pattern match found",
                    type=SemanticType.CONCEPT,
                    semantic_weight=0.9
                )]
            )
            builder.connect_nodes(constraint.id, goal_node.id, EdgeType.PRIORITY, weight=0.95)
        
        # Connect transaction to goal
        builder.connect_nodes(tx_node.id, goal_node.id, EdgeType.LOGICAL, weight=0.8)
        
        # Notify observers
        builder.get_graph()
        
        return builder.get_graph(), risk_factors
    
    def _reason(self, graph: IntentGraph, risk_factors: list) -> Optional[ReasoningPath]:
        """Run hybrid reasoning engine."""
        engine = HybridReasoningEngine(graph)
        
        # Find goal node (last created) and context node (first)
        nodes = list(graph.nodes.values())
        if len(nodes) < 2:
            return None
        
        goal_node = None
        context_node = None
        for node in nodes:
            if node.type == IntentType.GOAL:
                goal_node = node
            elif context_node is None:
                context_node = node
        
        if goal_node is None:
            goal_node = nodes[-1]
        if context_node is None:
            context_node = nodes[0]
        
        start_id = context_node.id
        end_id = goal_node.id
        
        engine.find_paths(start_id, end_id)
        
        # Run convergence
        for _ in range(30):
            path = engine.step(dt=0.1)
            if path:
                return path
        
        # Fallback
        from hsrai.reasoning.hybrid_engine import ReasoningPath as RP
        return RP(nodes=nodes, edges=[], mu_stability=0.5)
    
    def _calculate_risk(self, tx: Transaction, risk_factors: list, 
                       path: Optional[ReasoningPath]) -> float:
        """Calculate composite risk score."""
        base_score = 0.0
        
        # Add rule-based scores
        for weight, _ in risk_factors:
            base_score += weight
        
        # Factor in amount (log scale)
        amount_score = min(1.0, np.log1p(tx.amount) / np.log1p(100000))
        base_score += amount_score * 0.2
        
        # Factor in reasoning path stability
        if path and path.mu_stability > 0:
            # Higher mu = more confident reasoning = adjust score
            stability_factor = min(0.2, path.mu_stability * 0.1)
            base_score += stability_factor
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, base_score))
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk score into level."""
        if score >= self.THRESHOLDS["critical"]:
            return "critical"
        elif score >= self.THRESHOLDS["high"]:
            return "high"
        elif score >= self.THRESHOLDS["medium"]:
            return "medium"
        return "low"
    
    def _generate_recommendations(self, risk_level: str, tx: Transaction) -> List[str]:
        """Generate action recommendations based on risk level."""
        recs = {
            "low": ["Approve transaction", "Log for monitoring"],
            "medium": ["Flag for review", "Send alert to compliance team"],
            "high": ["Block transaction", "Request additional verification", "Notify account holder"],
            "critical": ["Immediately freeze account", "File suspicious activity report",
                        "Notify law enforcement", "Preserve all evidence"],
        }
        return recs.get(risk_level, ["Review manually"])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "model": self.nlp.model_name,
            "embedding_dim": self.nlp.embedding_dim,
            "knowledge_backend": "neo4j" if self.knowledge._connected else "memory",
            "requests_processed": self._request_count,
        }