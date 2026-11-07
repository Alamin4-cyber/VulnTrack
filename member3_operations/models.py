from django.contrib.auth.models import User
from django.db import models

from member1_core.models import Target
from member2_assessment.models import ScanProfile


class ScanJob(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="scans")
    profile = models.ForeignKey(ScanProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="scans")
    initiated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="scans")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    progress = models.PositiveSmallIntegerField(default=0)
    current_stage = models.CharField(max_length=120, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Scan #{self.id} — {self.target.name}"

    @property
    def status_css(self):
        return {"pending": "secondary", "running": "primary", "completed": "success",
                "failed": "danger", "cancelled": "warning"}.get(self.status, "secondary")


class ScanLog(models.Model):
    LEVEL_CHOICES = (("info", "Info"), ("success", "Success"),
                     ("warning", "Warning"), ("error", "Error"))
    scan = models.ForeignKey(ScanJob, on_delete=models.CASCADE, related_name="logs")
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="info")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Evidence(models.Model):
    finding = models.ForeignKey("member2_assessment.VulnerabilityFinding",
                                on_delete=models.CASCADE, related_name="evidences")
    request_data = models.TextField(blank=True)
    response_data = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-captured_at"]


class Remediation(models.Model):
    finding = models.OneToOneField("member2_assessment.VulnerabilityFinding",
                                   on_delete=models.CASCADE, related_name="remediation")
    recommendation = models.TextField()
    references = models.TextField(blank=True)
    priority = models.CharField(max_length=20, default="medium")
    ai_explanation = models.TextField(blank=True)
    ai_generated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    LEVEL_CHOICES = (("info", "Info"), ("success", "Success"),
                     ("warning", "Warning"), ("danger", "Danger"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="info")
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Report(models.Model):
    scan = models.ForeignKey(ScanJob, on_delete=models.CASCADE, related_name="reports")
    generated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="reports/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
