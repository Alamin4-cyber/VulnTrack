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