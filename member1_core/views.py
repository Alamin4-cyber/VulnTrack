from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ProfileForm, RegisterForm, TargetForm
from .models import Target, UserProfile
from .utils import can_scan, visible_targets


def home(request):
    if request.user.is_authenticated:
        return redirect("member1_core:target_list")
    return redirect("member1_core:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("member1_core:target_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        p, _ = UserProfile.objects.get_or_create(user=user)
        p.role = form.cleaned_data["role"]
        p.organization = form.cleaned_data.get("organization", "")
        p.save()
        login(request, user)
        messages.success(request, "Account created.")
        return redirect("member1_core:target_list")
    return render(request, "shared/form.html", {"form": form, "title": "Register", "cancel_url": "/"})


@login_required
def profile(request):
    p, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=p)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("member1_core:profile")
    return render(request, "member1_core/profile.html", {"form": form, "profile": p})


@login_required
def target_list(request):
    targets = visible_targets(request.user).select_related("owner")
    return render(request, "member1_core/target_list.html", {"targets": targets})


@login_required
def target_create(request):
    form = TargetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        t = form.save(commit=False)
        t.owner = request.user
        if form.cleaned_data.get("authorization_confirmed"):
            t.is_authorized = True
            t.authorized_at = timezone.now()
            t.authorized_by = request.user
        t.save()
        messages.success(request, "Target added.")
        return redirect("member1_core:target_detail", pk=t.pk)
    return render(request, "shared/form.html", {
        "form": form, "title": "Add target",
        "cancel_url": reverse("member1_core:target_list"),
    })


@login_required
def target_edit(request, pk):
    t = get_object_or_404(visible_targets(request.user), pk=pk)
    if not (t.owner_id == request.user.id or can_scan(request.user)):
        raise PermissionDenied
    form = TargetForm(request.POST or None, instance=t)
    if request.method == "POST" and form.is_valid():
        t = form.save(commit=False)
        if form.cleaned_data.get("authorization_confirmed") and not t.is_authorized:
            t.is_authorized = True
            t.authorized_at = timezone.now()
            t.authorized_by = request.user
        t.save()
        messages.success(request, "Target updated.")
        return redirect("member1_core:target_detail", pk=t.pk)
    return render(request, "shared/form.html", {
        "form": form, "title": "Edit target",
        "cancel_url": reverse("member1_core:target_detail", args=[t.pk]),
    })


@login_required
def target_delete(request, pk):
    t = get_object_or_404(visible_targets(request.user), pk=pk)
    if request.method == "POST" and (t.owner_id == request.user.id or can_scan(request.user)):
        t.delete()
        messages.success(request, "Target deleted.")
    return redirect("member1_core:target_list")


@login_required
def target_verify(request, pk):
    if not can_scan(request.user):
        raise PermissionDenied
    t = get_object_or_404(visible_targets(request.user), pk=pk)
    if request.method == "POST":
        ref = (request.POST.get("reference") or "").strip()
        if not ref:
            messages.error(request, "Authorization reference required.")
        else:
            t.authorization_reference = ref
            t.is_authorized = True
            t.authorized_at = timezone.now()
            t.authorized_by = request.user
            t.save()
            messages.success(request, "Target authorization verified.")
    return redirect("member1_core:target_detail", pk=t.pk)


@login_required
def target_detail(request, pk):
    t = get_object_or_404(visible_targets(request.user).select_related("owner"), pk=pk)
    scans = t.scans.select_related("profile").order_by("-created_at")[:10]
    role = getattr(getattr(request.user, "profile", None), "role", "")
    can_manage = request.user.is_superuser or role in ("admin", "analyst") or t.owner_id == request.user.id
    return render(request, "member1_core/target_detail.html", {
        "target": t, "scans": scans, "can_manage": can_manage, "can_run": can_scan(request.user),
    })