from django.utils import timezone

from member1_core.models import DNSRecord, Subdomain
from member2_assessment.models import Endpoint, Host, Port, Technology, VulnerabilityFinding
from member3_operations.models import Evidence, Notification, Remediation, ScanJob, ScanLog

DEMO_PREFIXES = ["www", "api", "mail"]

COMMON_FINDINGS = [
    {"title": "Missing Content-Security-Policy header",
     "vuln_type": "security_misconfiguration", "severity": "medium", "confidence": "certain",
     "description": "The HTTP response lacks a CSP header.",
     "template_id": "headers-csp-missing",
     "recommendation": "Define a restrictive Content-Security-Policy header.",
     "references": "https://owasp.org/www-project-secure-headers/",
     "request": "GET / HTTP/1.1", "response": "HTTP/1.1 200 OK\n(no CSP)"},
    {"title": "Missing Strict-Transport-Security header",
     "vuln_type": "security_misconfiguration", "severity": "low", "confidence": "certain",
     "description": "HSTS not enabled.",
     "template_id": "headers-hsts-missing",
     "recommendation": "Enable HSTS.", "references": "https://developer.mozilla.org/",
     "request": "GET / HTTP/1.1", "response": "HTTP/1.1 200 OK\n(no HSTS)"},
]

EXTRA_FINDINGS = [
    {"title": "Exposed .git directory", "vuln_type": "exposed_sensitive_file",
     "severity": "high", "confidence": "firm",
     "description": "/.git/ is publicly accessible.",
     "template_id": "exposed-git-config",
     "recommendation": "Block .git at web server.", "references": "https://owasp.org/",
     "path": "/.git/config", "request": "GET /.git/config HTTP/1.1",
     "response": "HTTP/1.1 200 OK\n[core]"},
    {"title": "Reflected XSS", "vuln_type": "xss",
     "severity": "high", "confidence": "firm",
     "description": "User input reflected without encoding.",
     "template_id": "xss-reflected",
     "recommendation": "Encode output, add CSP.",
     "references": "https://owasp.org/www-community/attacks/xss/",
     "path": "/?q=<script>", "request": "GET /?q=<script>alert(1)</script>",
     "response": "HTTP/1.1 200 OK\n<html>...<script>..."},
]


def _log(scan, msg, level="info"):
    ScanLog.objects.create(scan=scan, message=msg, level=level)


def _stage(scan, progress, stage):
    scan.progress = progress
    scan.current_stage = stage
    scan.save(update_fields=["progress", "current_stage"])
    _log(scan, f"{stage} ({progress}%)")


def _create_finding(scan, target, host, spec):
    f = VulnerabilityFinding.objects.create(
        scan_id=scan.id, target=target, host=host,
        title=spec["title"], vuln_type=spec["vuln_type"],
        severity=spec["severity"], confidence=spec["confidence"],
        description=spec["description"],
        matched_at=f"http://{host.hostname}{spec.get('path', '/')}",
        template_id=spec.get("template_id", ""))
    Evidence.objects.create(finding=f,
        request_data=f"{spec.get('request','GET / HTTP/1.1')}\nHost: {host.hostname}",
        response_data=spec.get("response", "HTTP/1.1 200 OK"),
        notes="Demo scan evidence.")
    Remediation.objects.create(finding=f, recommendation=spec["recommendation"],
        references=spec.get("references", ""), priority=spec["severity"])
    return f


def execute_scan(scan_id):
    scan = ScanJob.objects.select_related("target", "initiated_by").get(pk=scan_id)
    target = scan.target
    try:
        if not target.is_authorized:
            raise ValueError("Target not authorized.")
        scan.status = "running"
        scan.started_at = timezone.now()
        scan.progress = 0
        scan.current_stage = "Starting"
        scan.error_message = ""
        scan.summary = ""
        scan.save()

        VulnerabilityFinding.objects.filter(scan_id=scan.id).delete()
        Host.objects.filter(scan_id=scan.id).delete()

        domain = target.domain.lower()
        _stage(scan, 10, "Subdomain enumeration")
        names = [domain] + [f"{p}.{domain}" for p in DEMO_PREFIXES]
        for i, name in enumerate(names):
            sub, created = Subdomain.objects.update_or_create(
                target=target, name=name,
                defaults={"ip_address": f"192.0.2.{10+i}", "source": "subfinder (demo)",
                          "is_active": True, "last_scan_id": scan.id})
            if created:
                Subdomain.objects.filter(pk=sub.pk).update(first_scan_id=scan.id)

        for i, name in enumerate(names):
            DNSRecord.objects.update_or_create(
                target=target, name=name, record_type="A",
                defaults={"value": f"192.0.2.{10+i}", "ttl": 300, "scan_id": scan.id})

        _stage(scan, 35, "Port and service discovery")
        hosts = []
        for i, name in enumerate(names):
            host, _ = Host.objects.update_or_create(
                scan_id=scan.id, hostname=name,
                defaults={"target": target, "ip_address": f"192.0.2.{10+i}", "is_alive": True})
            hosts.append(host)
            for p in [22, 80, 443]:
                svc = {22: "ssh", 80: "http", 443: "https"}[p]
                Port.objects.create(host=host, number=p, protocol="tcp", service=svc,
                                    version="OpenSSH 8.2" if p == 22 else "nginx 1.18", state="open")
            Technology.objects.create(host=host, name="nginx", version="1.18", category="web server")
            Endpoint.objects.create(host=host, url=f"http://{name}/", method="GET", status_code=200)

        _stage(scan, 65, "Vulnerability assessment")
        for i, host in enumerate(hosts):
            for spec in COMMON_FINDINGS:
                _create_finding(scan, target, host, spec)
            if i == 0:
                for spec in EXTRA_FINDINGS:
                    _create_finding(scan, target, host, spec)

        count = VulnerabilityFinding.objects.filter(scan_id=scan.id).count()
        scan.status = "completed"
        scan.progress = 100
        scan.current_stage = "Completed"
        scan.finished_at = timezone.now()
        scan.summary = f"{count} findings across {len(hosts)} hosts."
        scan.save()
        _log(scan, "Scan completed.", "success")
        if scan.initiated_by_id:
            Notification.objects.create(
                user=scan.initiated_by, title=f"Scan #{scan.id} completed",
                message=scan.summary, level="success", link=f"/scans/{scan.id}/")
        return scan
    except Exception as exc:
        scan.status = "failed"
        scan.error_message = str(exc)
        scan.finished_at = timezone.now()
        scan.save()
        _log(scan, f"Failed: {exc}", "error")
        return scan
