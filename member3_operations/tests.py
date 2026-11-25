"""Tests for Member 3 (member3_operations) — Modules 1, 2 and 3.

Covers: scan creation + authorization guards, scan run guards,
progress JSON, dashboard counts, evidence/remediation, AI explanation
(template lookup), notifications, PDF report generation, re-run
idempotency, and the scanner-error handling (scan must fail cleanly,
never 500).

The live crt.sh lookup is mocked out so the suite is fast and
deterministic; one test asserts the real lookup uses a 5s timeout.
"""

from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from member1_core.models import Target
from member2_assessment.models import ScanProfile, VulnerabilityFinding
from member3_operations.models import (
    Evidence,
    Notification,
    Remediation,
    Report,
    ScanJob,
)


class Member3TestBase(TestCase):
    def setUp(self):
        self.analyst = User.objects.create_user("analyst", password="pw")
        self.student = User.objects.create_user("student", password="pw")
        self.student.profile.role = "student"
        self.student.profile.save()

        self.target = Target.objects.create(
            owner=self.analyst, name="Example", domain="example.local",
            is_authorized=True, is_active=True,
        )
        self.unauth_target = Target.objects.create(
            owner=self.analyst, name="NoAuth", domain="noauth.local",
            is_authorized=False, is_active=True,
        )
        self.profile = ScanProfile.objects.create(name="Quick Scan")
        self.client = Client()

    def login_analyst(self):
        self.client.force_login(self.analyst)

    def login_student(self):
        self.client.force_login(self.student)

    def make_scan(self, target=None):
        return ScanJob.objects.create(
            target=target or self.target,
            profile=self.profile,
            initiated_by=self.analyst,
        )

    def run_scan(self, scan):
        """Run a scan with the live crt.sh lookup mocked to no results."""
        with patch(
            "member3_operations.services.scanner.fetch_subdomains_from_crtsh",
            return_value=[],
        ):
            return self.client.post(
                reverse("member3_operations:scan_run", args=[scan.pk])
            )


class ScanCreateTests(Member3TestBase):
    def test_anon_scan_list_redirects_to_login(self):
        response = self.client.get(reverse("member3_operations:scan_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_form_shows_only_authorized_targets(self):
        self.login_analyst()
        response = self.client.get(reverse("member3_operations:scan_create"))
        self.assertEqual(response.status_code, 200)
        qs = response.context["form"].fields["target"].queryset
        self.assertEqual(list(qs), [self.target])

    def test_create_with_unauthorized_target_rejected(self):
        self.login_analyst()
        response = self.client.post(
            reverse("member3_operations:scan_create"),
            {"target": self.unauth_target.pk, "profile": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ScanJob.objects.count(), 0)

    def test_create_as_student_forbidden(self):
        self.login_student()
        response = self.client.post(
            reverse("member3_operations:scan_create"),
            {"target": self.target.pk, "profile": ""},
        )
        self.assertEqual(response.status_code, 403)

    def test_create_ok_redirects_to_detail(self):
        self.login_analyst()
        response = self.client.post(
            reverse("member3_operations:scan_create"),
            {"target": self.target.pk, "profile": self.profile.pk},
        )
        scan = ScanJob.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"/scans/{scan.pk}/")
        self.assertEqual(scan.status, "pending")
        self.assertEqual(scan.initiated_by, self.analyst)


class ScanRunTests(Member3TestBase):
    def test_detail_forbidden_for_other_user(self):
        scan = self.make_scan()
        self.login_student()
        response = self.client.get(
            reverse("member3_operations:scan_detail", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_run_get_redirects_without_running(self):
        scan = self.make_scan()
        self.login_analyst()
        response = self.client.get(
            reverse("member3_operations:scan_run", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 302)
        scan.refresh_from_db()
        self.assertEqual(scan.status, "pending")

    def test_run_unauthorized_target_stays_pending(self):
        scan = self.make_scan(target=self.unauth_target)
        self.login_analyst()
        response = self.client.post(
            reverse("member3_operations:scan_run", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 302)
        scan.refresh_from_db()
        self.assertEqual(scan.status, "pending")

    def test_run_already_running_warns_and_keeps_running(self):
        scan = self.make_scan()
        scan.status = "running"
        scan.save()
        self.login_analyst()
        response = self.client.post(
            reverse("member3_operations:scan_run", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 302)
        scan.refresh_from_db()
        self.assertEqual(scan.status, "running")

    def test_scanner_error_marks_scan_failed_not_500(self):
        """Regression test: a scanner crash must not 500 the run page."""
        scan = self.make_scan()
        self.login_analyst()
        with patch(
            "member3_operations.services.scanner.execute_scan",
            side_effect=RuntimeError("boom"),
        ):
            response = self.client.post(
                reverse("member3_operations:scan_run", args=[scan.pk])
            )
        self.assertEqual(response.status_code, 302)
        scan.refresh_from_db()
        self.assertEqual(scan.status, "failed")
        self.assertEqual(scan.error_message, "boom")

    def test_full_run_creates_findings_evidence_remediation_notification(self):
        scan = self.make_scan()
        self.login_analyst()
        response = self.run_scan(scan)
        self.assertEqual(response.status_code, 302)
        scan.refresh_from_db()
        self.assertEqual(scan.status, "completed")
        self.assertEqual(scan.progress, 100)
        # Fixed plural: "1 host", not "1 hosts".
        self.assertEqual(scan.summary, "4 findings across 1 host.")
        findings = VulnerabilityFinding.objects.filter(scan_id=scan.pk)
        self.assertEqual(findings.count(), 4)
        self.assertEqual(
            sorted(findings.values_list("severity", flat=True)),
            ["high", "high", "low", "medium"],
        )
        self.assertEqual(Evidence.objects.count(), 4)
        self.assertEqual(Remediation.objects.count(), 4)
        self.assertEqual(Notification.objects.count(), 1)

    def test_progress_json_after_completed_run(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        response = self.client.get(
            reverse("member3_operations:scan_progress", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "completed",
            "status_display": "Completed",
            "progress": 100,
            "stage": "Completed",
        })

    def test_re_run_does_not_duplicate_findings(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        self.run_scan(scan)
        findings = VulnerabilityFinding.objects.filter(scan_id=scan.pk)
        self.assertEqual(findings.count(), 4)


class DashboardTests(Member3TestBase):
    def test_dashboard_counts_after_run(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        response = self.client.get(reverse("member3_operations:dashboard"))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        # Analyst sees ALL targets (authorized + unauthorized) via
        # visible_targets, so target_count is 2 even though only 1
        # target was scanned.
        self.assertEqual(ctx["target_count"], 2)
        self.assertEqual(ctx["scan_count"], 1)
        self.assertEqual(ctx["finding_count"], 4)
        self.assertEqual(ctx["critical_count"], 0)
        self.assertEqual(ctx["high_count"], 2)


class EvidenceRemediationAiTests(Member3TestBase):
    def _completed_scan_with_finding(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        finding = VulnerabilityFinding.objects.filter(
            scan_id=scan.pk, vuln_type="security_misconfiguration"
        ).first()
        return scan, finding

    def test_evidence_create(self):
        _, finding = self._completed_scan_with_finding()
        before = Evidence.objects.filter(finding=finding).count()
        response = self.client.post(
            reverse("member3_operations:evidence_create", args=[finding.pk]),
            {"request_data": "GET / HTTP/1.1",
             "response_data": "HTTP/1.1 200 OK",
             "notes": "manual proof"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Evidence.objects.filter(finding=finding).count(), before + 1
        )

    def test_remediation_ai_generates_from_template(self):
        _, finding = self._completed_scan_with_finding()
        remediation = Remediation.objects.get(finding=finding)
        response = self.client.post(
            reverse("member3_operations:remediation_ai",
                    args=[remediation.pk])
        )
        self.assertEqual(response.status_code, 302)
        remediation.refresh_from_db()
        self.assertTrue(remediation.ai_generated)
        self.assertIn("CSP", remediation.ai_explanation)

    def test_notification_read(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        note = Notification.objects.get(user=self.analyst)
        self.assertFalse(note.is_read)
        response = self.client.post(
            reverse("member3_operations:notification_read", args=[note.pk])
        )
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertTrue(note.is_read)


class ReportTests(Member3TestBase):
    def test_report_generate_get_does_not_create(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        response = self.client.get(
            reverse("member3_operations:report_generate", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.count(), 0)

    def test_report_generate_post_creates_valid_pdf(self):
        scan = self.make_scan()
        self.login_analyst()
        self.run_scan(scan)
        response = self.client.post(
            reverse("member3_operations:report_generate", args=[scan.pk])
        )
        self.assertEqual(response.status_code, 302)
        report = Report.objects.get()
        self.assertTrue(report.file.name.endswith(".pdf"))
        with report.file.open("rb") as f:
            self.assertEqual(f.read(5), b"%PDF-")


class ScannerTests(Member3TestBase):
    @patch("member3_operations.services.scanner.requests.get")
    def test_crtsh_lookup_uses_5s_timeout(self, mock_get):
        from member3_operations.services.scanner import (
            fetch_subdomains_from_crtsh,
        )

        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp
        fetch_subdomains_from_crtsh("example.local")
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs.get("timeout"), 5)
