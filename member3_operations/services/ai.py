TEMPLATES = {
    "xss": "Reflected XSS allows attacker JavaScript. Encode output contextually, validate input, add CSP.",
    "security_misconfiguration": "Add CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.",
    "exposed_sensitive_file": "Block access to sensitive files at web server and redeploy without secrets.",
}


def build_ai_explanation(finding):
    base = TEMPLATES.get(finding.vuln_type, "Review the evidence and apply OWASP guidance.")
    return (f"{base}\n\nSeverity: {finding.get_severity_display()} | "
            f"Confidence: {finding.get_confidence_display()}\n"
            f"Affected: {finding.matched_at or finding.target.domain}\n\n"
            "Next steps:\n1. Reproduce in safe env.\n2. Apply fix.\n3. Re-scan to confirm.")
