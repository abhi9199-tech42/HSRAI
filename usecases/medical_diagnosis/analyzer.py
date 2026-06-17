"""
HSRAI Medical Diagnosis Engine — Auditable Clinical Decision Support.

Demonstrates HSRAI reasoning for healthcare: symptom analysis,
differential diagnosis, drug safety checks, and trust-certified assessments.

DISCLAIMER: This is for demonstration only. Not for actual medical use.
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

from usecases.medical_diagnosis.knowledge import (
    MedicalKnowledgeGraph, Symptom, Severity, Condition, Drug
)

logger = logging.getLogger(__name__)


@dataclass
class Patient:
    """Patient data for diagnosis."""
    patient_id: str
    age: int
    sex: str
    symptoms: List[Symptom]
    existing_conditions: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    vital_signs: Dict[str, float] = field(default_factory=dict)
    lab_results: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosisAssessment:
    """Result of medical diagnosis analysis."""
    patient_id: str
    differential_diagnoses: List[Dict[str, Any]]  # (condition, score, explanation)
    primary_diagnosis: Optional[str]
    confidence: float
    risk_level: str  # "low", "moderate", "high", "critical"
    urgency: str     # "routine", "urgent", "emergent"
    drug_warnings: List[str]
    drug_interactions: List[Dict[str, str]]
    recommendations: List[str]
    reasoning_path: Optional[ReasoningPath] = None
    trust_certificate_id: Optional[str] = None
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MedicalDiagnosisEngine:
    """
    Production-grade clinical decision support using HSRAI.
    
    Pipeline:
    1. NLP Compression — Embed patient description
    2. Knowledge Graph — Match symptoms to conditions
    3. Intent Graph — Build diagnostic reasoning graph
    4. Hybrid Reasoning — Oscillatory convergence on diagnosis
    5. Drug Safety — Check interactions and contraindications
    6. Trust Certificate — Sign the assessment cryptographically
    """
    
    URGENCY_THRESHOLDS = {
        "critical_signs": {"fever", "hypotension", "tachycardia", "confusion", "st_elevation"},
        "severe_symptoms": {"chest_pain", "severe_dyspnea", "altered_mental_status"},
        "moderate_symptoms": {"high_fever", "persistent_vomiting", "dehydration"},
    }
    
    def __init__(self):
        self.nlp = NLPCompressor()
        self.trust_manager = TrustManager()
        self.medical_kb = MedicalKnowledgeGraph()
        self._request_count = 0
    
    def diagnose(self, patient: Patient) -> DiagnosisAssessment:
        """
        Analyze patient data and produce a diagnostic assessment.
        
        Returns a deterministic, auditable DiagnosisAssessment with
        a cryptographic trust certificate.
        """
        start_time = time.perf_counter()
        self._request_count += 1
        
        # Step 1: Compress patient description with NLP
        primitive = self._compress_patient(patient)
        
        # Step 2: Query medical knowledge graph
        symptom_names = [s.name for s in patient.symptoms]
        candidate_conditions = self.medical_kb.find_conditions(symptom_names)
        
        # Step 3: Build diagnostic reasoning graph
        graph = self._build_graph(patient, primitive, candidate_conditions)
        
        # Step 4: Run hybrid reasoning
        path = self._reason(graph)
        
        # Step 5: Format differential diagnoses
        differential = []
        for condition, score in candidate_conditions[:5]:
            explanation = self._explain_diagnosis(condition, patient)
            differential.append({
                "condition": condition.name,
                "icd_code": condition.icd_code,
                "probability": round(score, 3),
                "explanation": explanation,
                "required_symptoms_met": len(
                    set(condition.required_symptoms) & set(symptom_names)
                ),
                "total_required": len(condition.required_symptoms),
            })
        
        # Step 6: Primary diagnosis
        primary = differential[0] if differential else None
        primary_name = primary["condition"] if primary else None
        confidence = primary["probability"] if primary else 0.0
        
        # Step 7: Risk and urgency assessment
        risk_level = self._assess_risk(patient, differential)
        urgency = self._assess_urgency(patient)
        
        # Step 8: Drug safety checks
        drug_warnings = []
        for med in patient.current_medications:
            warnings = self.medical_kb.check_contraindications(med, patient.existing_conditions)
            drug_warnings.extend(warnings)
        
        interactions = self.medical_kb.check_drug_interactions(patient.current_medications)
        interaction_dicts = [
            {"drugs": f"{i.drug_a} + {i.drug_b}", "severity": i.severity.value, "description": i.description}
            for i in interactions
        ]
        
        # Step 9: Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, urgency, primary, drug_warnings, interaction_dicts
        )
        
        # Step 10: Trust certificate
        cert = self.trust_manager.generate_certificate(
            f"Diagnosis: {patient.patient_id} -> {primary_name} ({confidence:.3f})",
            f"diag_{patient.patient_id}"
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return DiagnosisAssessment(
            patient_id=patient.patient_id,
            differential_diagnoses=differential,
            primary_diagnosis=primary_name,
            confidence=confidence,
            risk_level=risk_level,
            urgency=urgency,
            drug_warnings=drug_warnings,
            drug_interactions=interaction_dicts,
            recommendations=recommendations,
            reasoning_path=path,
            trust_certificate_id=cert.certificate_id,
            processing_time_ms=elapsed_ms,
            metadata={
                "age": patient.age,
                "sex": patient.sex,
                "symptom_count": len(patient.symptoms),
                "model": self.nlp.model_name,
                "knowledge_base": "medical_v1",
            }
        )
    
    def _compress_patient(self, patient: Patient) -> SemanticPrimitive:
        """NLP compression of patient data."""
        symptom_text = ", ".join([s.name.replace("_", " ") for s in patient.symptoms])
        description = (
            f"Patient {patient.patient_id}: {patient.age}yo {patient.sex}. "
            f"Symptoms: {symptom_text}. "
            f"Vitals: {patient.vital_signs}"
        )
        return self.nlp.compress_to_primitive(description, source_id=patient.patient_id)
    
    def _build_graph(self, patient: Patient, primitive: SemanticPrimitive,
                    candidates: List[tuple]) -> IntentGraph:
        """Build diagnostic reasoning graph."""
        builder = IntentGraphBuilder()
        
        # Patient node
        patient_node = builder.create_node(
            IntentType.CONTEXT,
            [primitive],
            behavioral_score=primitive.semantic_weight
        )
        
        # Goal: determine diagnosis
        goal_node = builder.create_node(
            IntentType.GOAL,
            [SemanticPrimitive(
                id=f"diag_goal_{patient.patient_id}",
                concept="Determine primary diagnosis",
                type=SemanticType.CONCEPT,
                semantic_weight=1.0
            )]
        )
        
        # Add top candidate diagnoses as context
        for condition, score in candidates[:3]:
            cond_node = builder.create_node(
                IntentType.CONTEXT,
                [SemanticPrimitive(
                    id=f"cond_{condition.icd_code}",
                    concept=f"{condition.name} (score: {score:.2f})",
                    type=SemanticType.CONCEPT,
                    semantic_weight=score
                )]
            )
            builder.connect_nodes(cond_node.id, goal_node.id, EdgeType.LOGICAL, weight=score)
        
        # Add risk constraints
        symptom_names = [s.name for s in patient.symptoms]
        
        # Critical symptoms trigger constraint
        critical = self.URGENCY_THRESHOLDS["critical_signs"]
        if set(symptom_names) & critical:
            constraint = builder.create_node(
                IntentType.CONSTRAINT,
                [SemanticPrimitive(
                    id=f"critical_{patient.patient_id}",
                    concept="Critical symptoms present - immediate action required",
                    type=SemanticType.CONCEPT,
                    semantic_weight=0.95
                )]
            )
            builder.connect_nodes(constraint.id, goal_node.id, EdgeType.PRIORITY, weight=0.95)
        
        # Drug interaction constraints
        if patient.current_medications:
            interactions = self.medical_kb.check_drug_interactions(patient.current_medications)
            if interactions:
                constraint = builder.create_node(
                    IntentType.CONSTRAINT,
                    [SemanticPrimitive(
                        id=f"drug_interact_{patient.patient_id}",
                        concept=f"Drug interactions detected: {len(interactions)}",
                        type=SemanticType.CONCEPT,
                        semantic_weight=0.8
                    )]
                )
                builder.connect_nodes(constraint.id, goal_node.id, EdgeType.PRIORITY, weight=0.8)
        
        # Connect patient to goal
        builder.connect_nodes(patient_node.id, goal_node.id, EdgeType.LOGICAL, weight=0.9)
        
        builder.get_graph()
        return builder.get_graph()
    
    def _reason(self, graph: IntentGraph) -> Optional[ReasoningPath]:
        """Run hybrid reasoning engine."""
        engine = HybridReasoningEngine(graph)
        nodes = list(graph.nodes.values())
        if len(nodes) < 2:
            return None
        
        engine.find_paths(nodes[0].id, nodes[-1].id)
        
        for _ in range(30):
            path = engine.step(dt=0.1)
            if path:
                return path
        
        from hsrai.reasoning.hybrid_engine import ReasoningPath as RP
        return RP(nodes=nodes, edges=[], mu_stability=0.5)
    
    def _explain_diagnosis(self, condition: Condition, patient: Patient) -> str:
        """Generate human-readable explanation for a diagnosis."""
        symptom_names = [s.name for s in patient.symptoms]
        
        matched_required = set(condition.required_symptoms) & set(symptom_names)
        matched_optional = set(condition.optional_symptoms) & set(symptom_names)
        
        parts = []
        parts.append(f"Matches {len(matched_required)}/{len(condition.required_symptoms)} required symptoms")
        
        if matched_required:
            parts.append(f"({', '.join(matched_required)})")
        
        if matched_optional:
            parts.append(f"plus {len(matched_optional)} optional symptoms")
        
        risk_matches = set(condition.risk_factors) & {
            "obesity" if patient.metadata.get("bmi", 0) > 30 else "",
            "age_over_45" if patient.age > 45 else "",
            "age_over_50" if patient.age > 50 else "",
            "age_over_65" if patient.age > 65 else "",
            "smoking" if patient.metadata.get("smoker", False) else "",
            "family_history" if patient.metadata.get("family_history", False) else "",
            "female" if patient.sex.lower() == "f" else "",
            "male" if patient.sex.lower() == "m" else "",
        }
        risk_matches.discard("")
        
        if risk_matches:
            parts.append(f"Risk factors present: {', '.join(risk_matches)}")
        
        return ". ".join(parts)
    
    def _assess_risk(self, patient: Patient, differential: List[Dict]) -> str:
        """Assess overall patient risk level."""
        if not differential:
            return "low"
        
        top_score = differential[0]["probability"]
        
        # Check for critical conditions
        critical_conditions = {"Acute Myocardial Infarction", "Sepsis"}
        for d in differential:
            if d["condition"] in critical_conditions and d["probability"] > 0.3:
                return "critical"
        
        # Check vital signs
        vitals = patient.vital_signs
        if vitals.get("heart_rate", 70) > 120 or vitals.get("heart_rate", 70) < 40:
            return "critical"
        if vitals.get("systolic_bp", 120) < 90 or vitals.get("systolic_bp", 120) > 200:
            return "critical"
        if vitals.get("temperature", 37) > 39.5:
            return "high"
        if vitals.get("o2_saturation", 100) < 90:
            return "critical"
        
        if top_score > 0.7:
            return "high"
        elif top_score > 0.4:
            return "moderate"
        return "low"
    
    def _assess_urgency(self, patient: Patient) -> str:
        """Assess how urgently the patient needs care."""
        symptom_names = {s.name for s in patient.symptoms}
        
        # Critical signs = emergent
        if symptom_names & self.URGENCY_THRESHOLDS["critical_signs"]:
            return "emergent"
        
        # Severe symptoms = urgent
        if symptom_names & self.URGENCY_THRESHOLDS["severe_symptoms"]:
            return "urgent"
        
        # Moderate symptoms = urgent
        if symptom_names & self.URGENCY_THRESHOLDS["moderate_symptoms"]:
            return "urgent"
        
        return "routine"
    
    def _generate_recommendations(self, risk_level: str, urgency: str,
                                  primary: Optional[Dict], drug_warnings: List[str],
                                  interactions: List[Dict]) -> List[str]:
        """Generate clinical recommendations."""
        recs = []
        
        if urgency == "emergent":
            recs.append("EMERGENT: Initiate immediate medical intervention")
            recs.append("Activate rapid response team")
        elif urgency == "urgent":
            recs.append("URGENT: Prioritize this patient for immediate evaluation")
        
        if primary:
            prob = primary["probability"]
            recs.append(f"Primary diagnosis: {primary['condition']} (confidence: {prob:.0%})")
            
            if prob < 0.5:
                recs.append("Low confidence — consider additional diagnostic tests")
            
            recs.append(f"ICD-10 code: {primary['icd_code']}")
        
        if drug_warnings:
            recs.append(f"DRUG WARNINGS ({len(drug_warnings)}):")
            for w in drug_warnings:
                recs.append(f"  ! {w}")
        
        if interactions:
            recs.append(f"DRUG INTERACTIONS ({len(interactions)}):")
            for i in interactions:
                recs.append(f"  ! {i['drugs']}: {i['description']} ({i['severity']})")
        
        if risk_level == "critical":
            recs.append("Recommend ICU admission or close monitoring")
        elif risk_level == "high":
            recs.append("Recommend inpatient admission")
        
        if not recs:
            recs.append("Continue current management")
            recs.append("Follow up in 1-2 weeks")
        
        return recs
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "model": self.nlp.model_name,
            "embedding_dim": self.nlp.embedding_dim,
            "conditions_in_kb": len(self.medical_kb.conditions),
            "drugs_in_kb": len(self.medical_kb.drugs),
            "interactions_in_kb": len(self.medical_kb.interactions),
            "requests_processed": self._request_count,
        }
