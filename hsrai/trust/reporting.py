import json
from datetime import datetime
from typing import List

from hsrai.core.models import TrustCertificate
from hsrai.trust.verifier import TrustManager


class ComplianceReporter:
    """
    Generates audit-ready compliance reports from TrustCertificates.
    """

    def __init__(self, trust_manager: TrustManager):
        self.trust_manager = trust_manager

    def generate_audit_report(self, certificates: List[TrustCertificate]) -> str:
        """
        Generate a Markdown formatted audit report for a chain of certificates.
        Verifies each certificate against the TrustManager's public key.
        """
        report = []
        report.append("# HSRAI Compliance Audit Report")
        report.append(f"**Date:** {datetime.now().isoformat()}")
        report.append(f"**Issuer ID:** {self.trust_manager.issuer_id}")
        report.append(f"**Total Certificates:** {len(certificates)}")
        report.append("")

        report.append("## Verification Chain")
        report.append("| Certificate ID | Subject | Trust Score | Signature Status | Timestamp |")
        report.append("|---|---|---|---|---|")

        valid_count = 0

        for cert in certificates:
            # Verify signature
            is_valid = self.trust_manager.verify_certificate(cert)
            status_icon = "✅ Valid" if is_valid else "❌ INVALID"
            if is_valid:
                valid_count += 1

            timestamp_str = datetime.fromtimestamp(cert.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            report.append(f"| `{cert.certificate_id}` | `{cert.subject_id}` | {cert.trust_score:.4f} | {status_icon} | {timestamp_str} |")

        report.append("")
        report.append("## Summary")
        report.append(f"- **Success Rate:** {valid_count}/{len(certificates)} certificates verified")

        if valid_count == len(certificates):
            report.append("\n**VERDICT:** ✅ COMPLIANT - All actions cryptographically verified.")
        else:
            report.append("\n**VERDICT:** ❌ NON-COMPLIANT - Tampering or unauthorized actions detected.")

        return "\n".join(report)

    def export_json(self, certificates: List[TrustCertificate]) -> str:
        """
        Export certificates as a JSON string for machine consumption.
        """
        data = []
        for cert in certificates:
            data.append({
                "id": cert.certificate_id,
                "subject": cert.subject_id,
                "score": cert.trust_score,
                "signature": cert.signature,
                "verified": self.trust_manager.verify_certificate(cert)
            })
        return json.dumps(data, indent=2)
