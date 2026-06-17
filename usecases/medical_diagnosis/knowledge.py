"""
Medical Knowledge Graph — Conditions, Symptoms, Drugs, and Relationships.

This is a simplified medical knowledge base for demonstration.
In production, this would connect to SNOMED CT, ICD-10, DrugBank, etc.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum


class Severity(Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class Symptom:
    name: str
    severity: Severity
    duration_days: int = 0
    body_system: str = ""


@dataclass
class Condition:
    name: str
    icd_code: str
    required_symptoms: List[str]       # Must have
    optional_symptoms: List[str]       # May have
    risk_factors: List[str]            # Increases likelihood
    body_system: str = ""
    prevalence: float = 0.0            # 0-1, how common
    mortality_rate: float = 0.0        # 0-1, if untreated


@dataclass
class Drug:
    name: str
    drug_class: str
    contraindications: List[str]       # Conditions where drug is dangerous
    side_effects: List[str]
    interactions: List[str]            # Other drugs that interact
    dosage_range: str = ""


@dataclass
class DrugInteraction:
    drug_a: str
    drug_b: str
    severity: Severity
    description: str


class MedicalKnowledgeGraph:
    """
    In-memory medical knowledge graph.
    
    Stores relationships between symptoms, conditions, and drugs
    for clinical reasoning support.
    
    NOTE: This is for demonstration only. Not for actual medical use.
    """
    
    def __init__(self):
        self.conditions: Dict[str, Condition] = {}
        self.drugs: Dict[str, Drug] = {}
        self.interactions: List[DrugInteraction] = []
        self._build_knowledge()
    
    def _build_knowledge(self):
        """Build the medical knowledge base."""
        
        # === CONDITIONS ===
        self.conditions["type2_diabetes"] = Condition(
            name="Type 2 Diabetes Mellitus",
            icd_code="E11",
            required_symptoms=["hyperglycemia", "polyuria"],
            optional_symptoms=["polydipsia", "weight_loss", "fatigue", "blurred_vision"],
            risk_factors=["obesity", "family_history", "age_over_45", "sedentary_lifestyle"],
            body_system="endocrine",
            prevalence=0.11,
            mortality_rate=0.02,
        )
        
        self.conditions["hypertension"] = Condition(
            name="Hypertension",
            icd_code="I10",
            required_symptoms=["elevated_blood_pressure"],
            optional_symptoms=["headache", "dizziness", "blurred_vision", "nosebleed"],
            risk_factors=["obesity", "high_sodium_diet", "family_history", "age_over_40", "smoking"],
            body_system="cardiovascular",
            prevalence=0.30,
            mortality_rate=0.01,
        )
        
        self.conditions["pneumonia"] = Condition(
            name="Community-Acquired Pneumonia",
            icd_code="J18.9",
            required_symptoms=["cough", "fever"],
            optional_symptoms=["dyspnea", "chest_pain", "sputum_production", "fatigue"],
            risk_factors=["age_over_65", "immunocompromised", "smoking", "chronic_lung_disease"],
            body_system="respiratory",
            prevalence=0.015,
            mortality_rate=0.05,
        )
        
        self.conditions["acute_myocardial_infarction"] = Condition(
            name="Acute Myocardial Infarction",
            icd_code="I21",
            required_symptoms=["chest_pain", "st_elevation"],
            optional_symptoms=["dyspnea", "diaphoresis", "nausea", "arm_pain", "jaw_pain"],
            risk_factors=["age_over_45_male", "smoking", "hypertension", "diabetes", "high_cholesterol"],
            body_system="cardiovascular",
            prevalence=0.003,
            mortality_rate=0.15,
        )
        
        self.conditions["copd"] = Condition(
            name="Chronic Obstructive Pulmonary Disease",
            icd_code="J44",
            required_symptoms=["chronic_cough", "dyspnea"],
            optional_symptoms=["sputum_production", "wheezing", "fatigue", "chest_tightness"],
            risk_factors=["smoking", "age_over_40", "occupational_exposure", "alpha1_antitrypsin_deficiency"],
            body_system="respiratory",
            prevalence=0.06,
            mortality_rate=0.03,
        )
        
        self.conditions["asthma"] = Condition(
            name="Asthma",
            icd_code="J45",
            required_symptoms=["wheezing", "dyspnea"],
            optional_symptoms=["cough", "chest_tightness", "symptom_worsening_night"],
            risk_factors=["allergies", "family_history", "childhood_onset", "exposure_to_allergens"],
            body_system="respiratory",
            prevalence=0.08,
            mortality_rate=0.001,
        )
        
        self.conditions["sepsis"] = Condition(
            name="Sepsis",
            icd_code="A41",
            required_symptoms=["fever", "tachycardia", "elevated_wbc"],
            optional_symptoms=["hypotension", "confusion", "tachypnea", "decreased_urine_output"],
            risk_factors=["immunocompromised", "recent_surgery", "indwelling_catheter", "age_over_65"],
            body_system="systemic",
            prevalence=0.005,
            mortality_rate=0.25,
        )
        
        self.conditions["hypothyroidism"] = Condition(
            name="Hypothyroidism",
            icd_code="E03",
            required_symptoms=["elevated_tsh"],
            optional_symptoms=["fatigue", "weight_gain", "cold_intolerance", "dry_skin", "constipation"],
            risk_factors=["female", "age_over_50", "family_history", "autoimmune_disease"],
            body_system="endocrine",
            prevalence=0.05,
            mortality_rate=0.001,
        )
        
        self.conditions["urinary_tract_infection"] = Condition(
            name="Urinary Tract Infection",
            icd_code="N39.0",
            required_symptoms=["dysuria", "urinary_frequency"],
            optional_symptoms=["urinary_urgency", "flank_pain", "hematuria", "fever"],
            risk_factors=["female", "sexual_activity", "immobility", "catheter_use"],
            body_system="renal",
            prevalence=0.10,
            mortality_rate=0.001,
        )
        
        self.conditions["deep_vein_thrombosis"] = Condition(
            name="Deep Vein Thrombosis",
            icd_code="I82",
            required_symptoms=["leg_swelling", "leg_pain"],
            optional_symptoms=["redness", "warmth", "dilated_veins"],
            risk_factors=["immobility", "recent_surgery", "obesity", "oral_contraceptive_use", "malignancy"],
            body_system="cardiovascular",
            prevalence=0.001,
            mortality_rate=0.05,
        )
        
        # === DRUGS ===
        self.drugs["metformin"] = Drug(
            name="Metformin",
            drug_class="biguanide",
            contraindications=["renal_impairment", "lactic_acidosis", "severe_liver_disease"],
            side_effects=["nausea", "diarrhea", "metallic_taste", "lactic_acidosis_rare"],
            interactions=["alcohol", "contrast_dye"],
            dosage_range="500-2550mg/day",
        )
        
        self.drugs["lisinopril"] = Drug(
            name="Lisinopril",
            drug_class="ACE_inhibitor",
            contraindications=["pregnancy", "angioedema_history", "bilateral_renal_artery_stenosis"],
            side_effects=["cough", "hyperkalemia", "dizziness", "angioedema_rare"],
            interactions=["potassium_supplements", "nsaids", "lithium"],
            dosage_range="5-40mg/day",
        )
        
        self.drugs["atorvastatin"] = Drug(
            name="Atorvastatin",
            drug_class="statin",
            contraindications=["active_liver_disease", "pregnancy", "breastfeeding"],
            side_effects=["myalgia", "liver_enzyme_elevation", "rhabdomyolysis_rare"],
            interactions=["fibrates", "niacin", "grapefruit_juice"],
            dosage_range="10-80mg/day",
        )
        
        self.drugs["amoxicillin"] = Drug(
            name="Amoxicillin",
            drug_class="penicillin_antibiotic",
            contraindications=["penicillin_allergy", "mononucleosis"],
            side_effects=["diarrhea", "rash", "nausea", "anaphylaxis_rare"],
            interactions=["warfarin", "methotrexate"],
            dosage_range="250-500mg TID",
        )
        
        self.drugs["albuterol"] = Drug(
            name="Albuterol",
            drug_class="beta2_agonist",
            contraindications=["severe_allergy_to_albuterol"],
            side_effects=["tremor", "tachycardia", "palpitations", "hypokalemia"],
            interactions=["beta_blockers", "digoxin", "mao_inhibitors"],
            dosage_range="2-4mg TID",
        )
        
        self.drugs["warfarin"] = Drug(
            name="Warfarin",
            drug_class="anticoagulant",
            contraindications=["active_bleeding", "pregnancy", "severe_liver_disease"],
            side_effects=["bleeding", "skin_necrosis", "purple_toe_syndrome"],
            interactions=["aspirin", "nsaids", "amiodarone", "antibiotics"],
            dosage_range="1-10mg/day (INR monitored)",
        )
        
        self.drugs["morphine"] = Drug(
            name="Morphine",
            drug_class="opioid_analgesic",
            contraindications=["respiratory_depression", "paralytic_ileus", "severe_asthma"],
            side_effects=["respiratory_depression", "constipation", "nausea", "sedation", "addiction"],
            interactions=["benzodiazepines", "alcohol", "mao_inhibitors"],
            dosage_range="2-60mg/day",
        )
        
        self.drugs["pantoprazole"] = Drug(
            name="Pantoprazole",
            drug_class="proton_pump_inhibitor",
            contraindications=[],
            side_effects=["headache", "diarrhea", "clostridium_difficile_rare"],
            interactions=["methotrexate", "clopidogrel"],
            dosage_range="20-40mg/day",
        )
        
        # === DRUG INTERACTIONS ===
        self.interactions = [
            DrugInteraction("warfarin", "aspirin", Severity.SEVERE, "Increased bleeding risk"),
            DrugInteraction("warfarin", "amoxicillin", Severity.MODERATE, "May increase INR"),
            DrugInteraction("lisinopril", "potassium_supplements", Severity.MODERATE, "Risk of hyperkalemia"),
            DrugInteraction("lisinopril", "nsaids", Severity.MILD, "Reduced antihypertensive effect"),
            DrugInteraction("metformin", "alcohol", Severity.SEVERE, "Risk of lactic acidosis"),
            DrugInteraction("atorvastatin", "grapefruit_juice", Severity.MILD, "Increased statin levels"),
            DrugInteraction("morphine", "benzodiazepines", Severity.CRITICAL, "Respiratory depression risk"),
            DrugInteraction("albuterol", "beta_blockers", Severity.MODERATE, "Reduced bronchodilation"),
        ]
    
    def find_conditions(self, symptom_names: List[str]) -> List[tuple]:
        """
        Find conditions matching given symptoms.
        Returns list of (condition, match_score) tuples.
        """
        results = []
        symptom_set = set(symptom_names)
        
        for cond_id, condition in self.conditions.items():
            required_matches = len(set(condition.required_symptoms) & symptom_set)
            required_total = len(condition.required_symptoms)
            
            if required_matches == 0:
                continue
            
            # Score = (required match ratio) * 0.7 + (optional match ratio) * 0.3
            required_score = required_matches / required_total
            
            optional_matches = len(set(condition.optional_symptoms) & symptom_set)
            optional_score = optional_matches / max(len(condition.optional_symptoms), 1)
            
            total_score = required_score * 0.7 + optional_score * 0.3
            
            # Boost by prevalence
            total_score *= (1.0 + condition.prevalence)
            
            results.append((condition, min(1.0, total_score)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def check_drug_interactions(self, drug_names: List[str]) -> List[DrugInteraction]:
        """Check for interactions between prescribed drugs."""
        found = []
        drug_set = set(drug_names)
        
        for interaction in self.interactions:
            if interaction.drug_a in drug_set and interaction.drug_b in drug_set:
                found.append(interaction)
        
        return found
    
    def get_drug_info(self, drug_name: str) -> Optional[Drug]:
        """Get drug information."""
        return self.drugs.get(drug_name)
    
    def check_contraindications(self, drug_name: str, patient_conditions: List[str]) -> List[str]:
        """Check if a drug is contraindicated for patient's conditions."""
        drug = self.drugs.get(drug_name)
        if not drug:
            return []
        
        warnings = []
        for condition in patient_conditions:
            if condition.lower() in [c.lower() for c in drug.contraindications]:
                warnings.append(f"CONTRAINDICATED: {drug_name} should not be given with {condition}")
        
        return warnings
