from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "member2_assessment"

urlpatterns = [
    # Optional: Redirect /assessment/ to /assessment/profiles/
    path("", RedirectView.as_view(pattern_name="member2_assessment:profile_list", permanent=False)),

    # ===== WEEK 1 URLS =====
    path("profiles/", views.profile_list, name="profile_list"),
    path("profiles/add/", views.profile_create, name="profile_create"),
    path("profiles/<int:pk>/edit/", views.profile_edit, name="profile_edit"),

    path("targets/<int:target_id>/scopes/", views.scope_list, name="scope_list"),
    path("targets/<int:target_id>/scopes/add/", views.scope_create, name="scope_create"),
    path("scopes/<int:pk>/edit/", views.scope_edit, name="scope_edit"),
    path("scopes/<int:pk>/delete/", views.scope_delete, name="scope_delete"),

    # ===== WEEK 2 URLS =====
    path("results/<int:scan_id>/", views.results, name="results"),
    path("findings/", views.finding_list, name="finding_list"),
    path("findings/<int:pk>/", views.finding_detail, name="finding_detail"),

    # ===== WEEK 3 URLS =====
    path("correlations/", views.correlation_list, name="correlations"),
    path("correlations/rebuild/<int:scan_id>/", views.rebuild_correlations, name="rebuild_correlations"),
]