from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from member1_core.utils import role_required, visible_targets

from .forms import ScanProfileForm, ScopeRuleForm
from .models import ScanProfile, ScopeRule
from .models import Host, VulnerabilityFinding
from django.core.exceptions import PermissionDenied


@login_required
def profile_list(request):
    profiles = ScanProfile.objects.select_related("created_by")
    return render(request, "member2_assessment/profile_list.html", {"profiles": profiles})


@role_required("admin", "analyst")
def profile_create(request):
    form = ScanProfileForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.created_by = request.user
        profile.save()
        messages.success(request, "Scan profile created.")
        return redirect("member2_assessment:profile_list")
    return render(request, "shared/form.html", {
        "form": form, "title": "Create scan profile",
        "cancel_url": reverse("member2_assessment:profile_list"),
    })


@role_required("admin", "analyst")
def profile_edit(request, pk):
    profile = get_object_or_404(ScanProfile, pk=pk)
    form = ScanProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Scan profile updated.")
        return redirect("member2_assessment:profile_list")
    return render(request, "shared/form.html", {
        "form": form, "title": "Edit scan profile",
        "cancel_url": reverse("member2_assessment:profile_list"),
    })


@login_required
def scope_list(request, target_id):
    target = get_object_or_404(visible_targets(request.user), pk=target_id)
    rules = target.scope_rules.select_related("created_by")
    return render(request, "member2_assessment/scope_list.html", {"target": target, "rules": rules})


@role_required("admin", "analyst")
def scope_create(request, target_id):
    target = get_object_or_404(visible_targets(request.user), pk=target_id)
    form = ScopeRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        rule = form.save(commit=False)
        rule.target = target
        rule.created_by = request.user
        rule.save()
        messages.success(request, "Scope rule added.")
        return redirect("member2_assessment:scope_list", target_id=target.id)
    return render(request, "shared/form.html", {
        "form": form, "title": f"Add scope rule — {target.name}",
        "cancel_url": reverse("member2_assessment:scope_list", args=[target.id]),
    })


@role_required("admin", "analyst")
def scope_edit(request, pk):
    rule = get_object_or_404(ScopeRule.objects.select_related("target"), pk=pk)
    form = ScopeRuleForm(request.POST or None, instance=rule)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Scope rule updated.")
        return redirect("member2_assessment:scope_list", target_id=rule.target_id)
    return render(request, "shared/form.html", {
        "form": form, "title": "Edit scope rule",
        "cancel_url": reverse("member2_assessment:scope_list", args=[rule.target_id]),
    })


@role_required("admin", "analyst")
def scope_delete(request, pk):
    rule = get_object_or_404(ScopeRule, pk=pk)
    target_id = rule.target_id
    if request.method == "POST":
        rule.delete()
        messages.success(request, "Scope rule deleted.")
    return redirect("member2_assessment:scope_list", target_id=target_id)
@login_required
def results(request, scan_id):
    from member3_operations.models import ScanJob
    scan = get_object_or_404(ScanJob.objects.select_related("target", "profile"), pk=scan_id)
    
    if not visible_targets(request.user).filter(pk=scan.target_id).exists():
        raise PermissionDenied
        
    hosts = Host.objects.filter(scan_id=scan.id).prefetch_related("ports", "technologies", "endpoints")
    findings = VulnerabilityFinding.objects.filter(scan_id=scan.id).select_related("host")
    
    return render(request, "member2_assessment/results.html", {
        "scan": scan, "hosts": hosts, "findings": findings
    })
@login_required
def finding_detail(request, pk):
    # Fetch the finding and ensure the user has permission to see it
    finding = get_object_or_404(
        VulnerabilityFinding.objects.filter(target__in=visible_targets(request.user)).select_related("target", "host", "endpoint"),
        pk=pk,
    )
    return render(request, "member2_assessment/finding_detail.html", {"finding": finding})