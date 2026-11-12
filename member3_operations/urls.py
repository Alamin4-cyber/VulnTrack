from django.urls import path
from . import views

app_name = "member3_operations"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("scans/", views.scan_list, name="scan_list"),
    path("scans/new/", views.scan_create, name="scan_create"),
    path("scans/<int:pk>/", views.scan_detail, name="scan_detail"),
    path("scans/<int:pk>/run/", views.scan_run, name="scan_run"),
    path("scans/<int:pk>/progress/", views.scan_progress, name="scan_progress"),

    path("findings/<int:finding_id>/evidence/add/", views.evidence_create, name="evidence_create"),
    path("evidence/<int:pk>/edit/", views.evidence_edit, name="evidence_edit"),
    path("findings/<int:finding_id>/remediation/", views.remediation_edit, name="remediation_edit"),
    path("remediation/<int:pk>/ai/", views.remediation_ai, name="remediation_ai"),

    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", views.notification_read, name="notification_read"),

    path("reports/", views.report_list, name="report_list"),
    path("reports/generate/<int:scan_id>/", views.report_generate, name="report_generate"),
]
