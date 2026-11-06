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