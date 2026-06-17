"""
Medical Diagnosis Demo — Run end-to-end analysis on sample patients.
"""

from usecases.medical_diagnosis.analyzer import MedicalDiagnosisEngine, Patient
from usecases.medical_diagnosis.knowledge import Symptom, Severity


def main():
    print("=" * 70)
    print("HSRAI Medical Diagnosis System - Demo")
    print("=" * 70)
    print("DISCLAIMER: For demonstration only. Not for actual medical use.")
    print()
    
    engine = MedicalDiagnosisEngine()
    
    patients = [
        # Patient 1: Likely Type 2 Diabetes
        Patient(
            patient_id="PAT001",
            age=52,
            sex="M",
            symptoms=[
                Symptom("polyuria", Severity.MODERATE, duration_days=30),
                Symptom("polydipsia", Severity.MODERATE, duration_days=30),
                Symptom("fatigue", Severity.MILD, duration_days=60),
                Symptom("blurred_vision", Severity.MILD, duration_days=14),
            ],
            existing_conditions=["hypertension"],
            current_medications=["lisinopril"],
            vital_signs={"systolic_bp": 145, "diastolic_bp": 92, "heart_rate": 78, "temperature": 36.8},
            lab_results={"fasting_glucose": 186, "hba1c": 8.2},
            metadata={"bmi": 31.2, "smoker": False, "family_history": True},
        ),
        
        # Patient 2: Possible Pneumonia
        Patient(
            patient_id="PAT002",
            age=68,
            sex="F",
            symptoms=[
                Symptom("cough", Severity.MODERATE, duration_days=5),
                Symptom("fever", Severity.SEVERE, duration_days=3),
                Symptom("dyspnea", Severity.MODERATE, duration_days=3),
                Symptom("sputum_production", Severity.MODERATE, duration_days=5),
                Symptom("chest_pain", Severity.MILD, duration_days=3),
            ],
            existing_conditions=["copd"],
            current_medications=["albuterol", "pantoprazole"],
            vital_signs={"systolic_bp": 118, "diastolic_bp": 72, "heart_rate": 102, "temperature": 38.9, "o2_saturation": 91},
            metadata={"bmi": 24.1, "smoker": True, "family_history": False},
        ),
        
        # Patient 3: Possible Heart Attack
        Patient(
            patient_id="PAT003",
            age=58,
            sex="M",
            symptoms=[
                Symptom("chest_pain", Severity.SEVERE, duration_days=0),
                Symptom("dyspnea", Severity.MODERATE, duration_days=0),
                Symptom("diaphoresis", Severity.MODERATE, duration_days=0),
                Symptom("nausea", Severity.MILD, duration_days=0),
                Symptom("arm_pain", Severity.MODERATE, duration_days=0),
            ],
            existing_conditions=["hypertension", "diabetes"],
            current_medications=["lisinopril", "metformin", "atorvastatin"],
            vital_signs={"systolic_bp": 95, "diastolic_bp": 60, "heart_rate": 115, "temperature": 36.5, "o2_saturation": 93},
            lab_results={"troponin": 0.42, "st_elevation": 1},
            metadata={"bmi": 28.5, "smoker": True, "family_history": True},
        ),
        
        # Patient 4: UTI (routine)
        Patient(
            patient_id="PAT004",
            age=28,
            sex="F",
            symptoms=[
                Symptom("dysuria", Severity.MILD, duration_days=2),
                Symptom("urinary_frequency", Severity.MILD, duration_days=2),
                Symptom("urinary_urgency", Severity.MILD, duration_days=2),
            ],
            existing_conditions=[],
            current_medications=[],
            vital_signs={"systolic_bp": 115, "diastolic_bp": 70, "heart_rate": 72, "temperature": 37.0},
            metadata={"bmi": 22.0, "smoker": False, "family_history": False},
        ),
        
        # Patient 5: Sepsis (critical)
        Patient(
            patient_id="PAT005",
            age=72,
            sex="M",
            symptoms=[
                Symptom("fever", Severity.CRITICAL, duration_days=1),
                Symptom("tachycardia", Severity.CRITICAL, duration_days=1),
                Symptom("hypotension", Severity.CRITICAL, duration_days=1),
                Symptom("confusion", Severity.SEVERE, duration_days=1),
                Symptom("tachypnea", Severity.MODERATE, duration_days=1),
                Symptom("decreased_urine_output", Severity.MODERATE, duration_days=1),
            ],
            existing_conditions=["diabetes"],
            current_medications=["metformin"],
            vital_signs={"systolic_bp": 78, "diastolic_bp": 45, "heart_rate": 128, "temperature": 39.8, "o2_saturation": 88},
            lab_results={"wbc": 18500, "lactate": 4.2},
            metadata={"bmi": 26.0, "smoker": False, "family_history": False},
        ),
    ]
    
    for patient in patients:
        result = engine.diagnose(patient)
        
        print("-" * 70)
        print(f"Patient: {result.patient_id} ({patient.age}yo {patient.sex})")
        print(f"Symptoms: {', '.join([s.name.replace('_', ' ') for s in patient.symptoms])}")
        print(f"Vitals: {patient.vital_signs}")
        print()
        
        print(f"  RISK LEVEL:    {result.risk_level.upper()}")
        print(f"  URGENCY:       {result.urgency.upper()}")
        print(f"  CONFIDENCE:    {result.confidence:.0%}")
        print()
        
        print("  Differential Diagnoses:")
        for i, d in enumerate(result.differential_diagnoses, 1):
            print(f"    {i}. {d['condition']} ({d['icd_code']})")
            print(f"       Probability: {d['probability']:.1%}")
            print(f"       {d['explanation']}")
        
        if result.drug_warnings:
            print()
            print("  DRUG WARNINGS:")
            for w in result.drug_warnings:
                print(f"    ! {w}")
        
        if result.drug_interactions:
            print()
            print("  DRUG INTERACTIONS:")
            for i in result.drug_interactions:
                print(f"    ! {i['drugs']}: {i['description']} ({i['severity']})")
        
        print()
        print("  Recommendations:")
        for rec in result.recommendations:
            print(f"    > {rec}")
        
        print(f"  Trust Certificate: {result.trust_certificate_id}")
        print(f"  Processing Time:   {result.processing_time_ms:.2f}ms")
        print()
    
    print("=" * 70)
    print("System Summary:")
    summary = engine.get_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("=" * 70)


if __name__ == "__main__":
    main()
