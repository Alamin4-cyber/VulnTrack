from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("admin", "System Administrator"),
        ("analyst", "Security Analyst"),
        ("owner", "Website Owner"),
        ("developer", "Development Team"),
        ("student", "Student / Researcher"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="analyst")
    organization = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Target(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="targets")
    name = models.CharField(max_length=120)
    domain = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_authorized = models.BooleanField(default=False)
    authorization_reference = models.CharField(max_length=255, blank=True)
    authorized_at = models.DateTimeField(null=True, blank=True)
    authorized_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="authorized_targets"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.domain})"

# ===== WEEK 2 MODELS =====
class Subdomain(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="subdomains")
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    first_scan_id = models.IntegerField(null=True, blank=True)
    last_scan_id = models.IntegerField(null=True, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("target", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class DNSRecord(models.Model):
    RECORD_TYPES = (
        ("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"),
        ("MX", "MX"), ("TXT", "TXT"), ("NS", "NS"),
    )
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="dns_records")
    name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES, default="A")
    value = models.CharField(max_length=500)
    ttl = models.IntegerField(default=300)
    scan_id = models.IntegerField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "record_type"]

    def __str__(self):
        return f"{self.name} {self.record_type} {self.value}"