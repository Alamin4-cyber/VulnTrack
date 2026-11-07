from django.urls import path
from . import views

app_name = "member2_assessment"

urlpatterns = [
    path("profiles/", views.profile_list, name="profile_list"),
    path("profiles/add/", views.profile_create, name="profile_create"),
    path("profiles/<int:pk>/edit/", views.profile_edit, name="profile_edit"),

    path("targets/<int:target_id>/scopes/", views.scope_list, name="scope_list"),
    path("targets/<int:target_id>/scopes/add/", views.scope_create, name="scope_create"),
    path("scopes/<int:pk>/edit/", views.scope_edit, name="scope_edit"),
    path("scopes/<int:pk>/delete/", views.scope_delete, name="scope_delete"),
]