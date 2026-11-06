from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "member1_core"

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/profile/", views.profile, name="profile"),

    path("targets/", views.target_list, name="target_list"),
    path("targets/add/", views.target_create, name="target_create"),
    path("targets/<int:pk>/", views.target_detail, name="target_detail"),
    path("targets/<int:pk>/edit/", views.target_edit, name="target_edit"),
    path("targets/<int:pk>/delete/", views.target_delete, name="target_delete"),
    path("targets/<int:pk>/verify/", views.target_verify, name="target_verify"),
]