
import pytest

from hsrai.trust.reporting import ComplianceReporter
from hsrai.trust.verifier import TrustManager


@pytest.fixture
def trust_manager():
    return TrustManager(issuer_id="TEST_ISSUER")


@pytest.fixture
def reporter(trust_manager):
    return ComplianceReporter(trust_manager)


@pytest.fixture
def sample_certificates(trust_manager):
    certs = []
    for subject in ["agent_a", "agent_b", "agent_c"]:
        cert = trust_manager.generate_certificate(subject, subject)
        certs.append(cert)
    return certs


class TestComplianceReporter:
    def test_generate_audit_report_returns_string(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert isinstance(result, str)

    def test_report_contains_heading(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "# HSRAI Compliance Audit Report" in result

    def test_report_contains_verification_chain_section(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "## Verification Chain" in result

    def test_report_contains_summary_section(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "## Summary" in result

    def test_report_contains_issuer_id(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "TEST_ISSUER" in result

    def test_report_contains_certificate_count(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "Total Certificates:** 3" in result

    def test_report_contains_valid_status(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "✅ Valid" in result

    def test_report_compliant_verdict(self, reporter, sample_certificates):
        result = reporter.generate_audit_report(sample_certificates)
        assert "COMPLIANT" in result

    def test_export_json_returns_valid_json(self, reporter, sample_certificates):
        import json
        result = reporter.export_json(sample_certificates)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_export_json_contains_expected_fields(self, reporter, sample_certificates):
        import json
        result = reporter.export_json(sample_certificates)
        data = json.loads(result)
        for entry in data:
            assert "id" in entry
            assert "subject" in entry
            assert "score" in entry
            assert "signature" in entry
            assert "verified" in entry
