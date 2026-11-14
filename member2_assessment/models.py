from django.contrib.auth.models import User
from django.db import models

from member1_core.models import Target


class ScopeRule(models.Model):
    RULE_TYPES = (("allow", "Allowed"), ("exclude", "Excluded"))
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="scope_rules")
    rule_type = models.CharField(max_length=10, choices=RULE_TYPES, default="allow")
    pattern = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["rule_type", "pattern"]

    def __str__(self):
        return f"{self.rule_type}: {self.pattern}"


class ScanProfile(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    enable_subdomain_enum = models.BooleanField(default=True)
    enable_dns_enum = models.BooleanField(default=True)
    enable_port_scan = models.BooleanField(default=True)
    enable_http_probe = models.BooleanField(default=True)
    enable_vuln_scan = models.BooleanField(default=True)
    port_range = models.CharField(max_length=50, default="1-1000")
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    # ===== WEEK 2 MODELS =====
class Host(models.Model):
    scan_id = models.IntegerField(db_index=True)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="hosts")
    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["hostname"]

    def __str__(self):
        return self.hostname


class Port(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="ports")
    number = models.PositiveIntegerField()
    protocol = models.CharField(max_length=10, default="tcp")
    service = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=20, default="open")

    class Meta:
        ordering = ["number"]


class Technology(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="technologies")
    name = models.CharField(max_length=120)
    version = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["name"]


class Endpoint(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="endpoints")
    url = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default="GET")
    status_code = models.IntegerField(null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["url"]


class VulnerabilityFinding(models.Model):
    SEVERITY_CHOICES = (
        ("critical", "Critical"), ("high", "High"), ("medium", "Medium"),
        ("low", "Low"), ("info", "Informational"),
    )
    CONFIDENCE_CHOICES = (
        ("certain", "Certain"), ("firm", "Firm"), ("tentative", "Tentative"),
    )
    STATUS_CHOICES = (
        ("open", "Open"), ("in_review", "In review"),
        ("resolved", "Resolved"), ("accepted", "Accepted risk"),
    )
    scan_id = models.IntegerField(db_index=True)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="findings")
    host = models.ForeignKey(Host, null=True, blank=True, on_delete=models.SET_NULL, related_name="findings")
    endpoint = models.ForeignKey(Endpoint, null=True, blank=True, on_delete=models.SET_NULL, related_name="findings")
    title = models.CharField(max_length=255)
    vuln_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_CHOICES, default="firm")
    description = models.TextField(blank=True)
    matched_at = models.CharField(max_length=500, blank=True)
    template_id = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def severity_css(self):
        return {"critical": "danger", "high": "warning", "medium": "info", "low": "secondary", "info": "secondary"}.get(self.severity, "secondary")

    