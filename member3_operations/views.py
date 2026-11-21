from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from member1_core.utils import role_required, visible_targets

from .forms import ScanJobForm
from .models import ScanJob
from .services.queue import enqueue_scan
from member2_assessment.models import VulnerabilityFinding
from .forms import EvidenceForm, RemediationForm
from .models import Evidence, Remediation
from django.db.models import Count
from .models import Notification, Report
from .services.ai import build_ai_explanation
from .services.reporting import generate_report


@login_required
def scan_list(request):
    return render(request, "member3_operations/scan_list.html", {
        "scans": ScanJob.objects.filter(target__in=visible_targets(request.user)).select_related(
            "target", "profile", "initiated_by")
    })


@role_required("admin", "analyst")
def scan_create(request):
    form = ScanJobForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        scan = ScanJob.objects.create(
            target=form.cleaned_data["target"],
            profile=form.cleaned_data.get("profile"),
            initiated_by=request.user,
        )
        messages.success(request, f"Scan #{scan.id} queued.")
        return redirect("member3_operations:scan_detail", pk=scan.pk)
    return render(request, "shared/form.html", {
        "form": form, "title": "Start a new scan",
        "cancel_url": reverse("member3_operations:scan_list"),
    })


def _get_scan(user, pk):
    s = get_object_or_404(ScanJob.objects.select_related("target", "profile", "initiated_by"), pk=pk)
    if not visible_targets(user).filter(pk=s.target_id).exists():
        raise PermissionDenied
    return s


@login_required
def scan_detail(request, pk):
    s = _get_scan(request.user, pk)
    from member2_assessment.models import VulnerabilityFinding
    return render(request, "member3_operations/scan_detail.html", {
        "scan": s,
        "logs": s.logs.all()[:40],
        "scan_findings": VulnerabilityFinding.objects.filter(scan_id=s.id).select_related("host"),
    })



@role_required("admin", "analyst")
def scan_run(request, pk):
    s = _get_scan(request.user, pk)
    if request.method != "POST":
        return redirect("member3_operations:scan_detail", pk=s.pk)
    if not s.target.is_authorized:
        messages.error(request, "Target not authorized.")
        return redirect("member3_operations:scan_detail", pk=s.pk)
    if s.status == "running":
        messages.warning(request, "Scan already running.")
        return redirect("member3_operations:scan_detail", pk=s.pk)
    s.status = "pending"
    s.progress = 0
    s.current_stage = "Queued"
    s.save()
    enqueue_scan(s.id)
    messages.success(request, "Scan executed.")
    return redirect("member3_operations:scan_detail", pk=s.pk)


@login_required
def scan_progress(request, pk):
    s = _get_scan(request.user, pk)
    return JsonResponse({
        "status": s.status, "status_display": s.get_status_display(),
        "progress": s.progress, "stage": s.current_stage,
    })


@role_required("admin", "analyst")
def evidence_create(request, finding_id):
    f = get_object_or_404(VulnerabilityFinding.objects.select_related("target"), pk=finding_id)
    if not visible_targets(request.user).filter(pk=f.target_id).exists():
        raise PermissionDenied
    form = EvidenceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        e = form.save(commit=False)
        e.finding = f
        e.save()
        messages.success(request, "Evidence added.")
        return redirect("member2_assessment:finding_detail", pk=f.pk)
    return render(request, "shared/form.html", {
        "form": form, "title": f"Add evidence — {f.title}",
        "cancel_url": reverse("member2_assessment:finding_detail", args=[f.pk]),
    })


@role_required("admin", "analyst")
def evidence_edit(request, pk):
    e = get_object_or_404(Evidence.objects.select_related("finding", "finding__target"), pk=pk)
    if not visible_targets(request.user).filter(pk=e.finding.target_id).exists():
        raise PermissionDenied
    form = EvidenceForm(request.POST or None, instance=e)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evidence updated.")
        return redirect("member2_assessment:finding_detail", pk=e.finding_id)
    return render(request, "shared/form.html", {
        "form": form, "title": "Edit evidence",
        "cancel_url": reverse("member2_assessment:finding_detail", args=[e.finding_id]),
    })


@role_required("admin", "analyst")
def remediation_edit(request, finding_id):
    f = get_object_or_404(VulnerabilityFinding.objects.select_related("target"), pk=finding_id)
    if not visible_targets(request.user).filter(pk=f.target_id).exists():
        raise PermissionDenied
    r, _ = Remediation.objects.get_or_create(
        finding=f, defaults={"recommendation": "Describe the fix.", "priority": f.severity})
    form = RemediationForm(request.POST or None, instance=r)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Remediation saved.")
        return redirect("member2_assessment:finding_detail", pk=f.pk)
    return render(request, "shared/form.html", {
        "form": form, "title": f"Remediation — {f.title}",
        "cancel_url": reverse("member2_assessment:finding_detail", args=[f.pk]),
    })


@login_required
def dashboard(request):
    targets = visible_targets(request.user)
    scans = ScanJob.objects.filter(target__in=targets)
    ids = list(scans.values_list("id", flat=True))
    findings = VulnerabilityFinding.objects.filter(scan_id__in=ids)
    sev = {r["severity"]: r["total"] for r in findings.values("severity").annotate(total=Count("id"))}
    return render(request, "member3_operations/dashboard.html", {
        "target_count": targets.count(), "scan_count": scans.count(),
        "finding_count": findings.count(),
        "open_finding_count": findings.filter(status="open").count(),
        "critical_count": sev.get("critical", 0), "high_count": sev.get("high", 0),
        "severity_rows": [(s.title(), sev.get(s, 0)) for s in
                          ["critical", "high", "medium", "low", "info"]],
        "recent_scans": scans.select_related("target").order_by("-created_at")[:6],
        "recent_findings": findings.select_related("target", "host").order_by("-created_at")[:8],
        "notifications": request.user.notifications.filter(is_read=False)[:5],
    })


@login_required
def notification_list(request):
    return render(request, "member3_operations/notifications.html", {
        "notifications": request.user.notifications.all()[:100]})


@login_required
def notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == "POST":
        n.is_read = True
        n.save()
    return redirect(n.link or "member3_operations:notification_list")


@login_required
def report_list(request):
    return render(request, "member3_operations/report_list.html", {
        "reports": Report.objects.filter(scan__target__in=visible_targets(request.user))
                                  .select_related("scan", "generated_by")})


@role_required("admin", "analyst")
def report_generate(request, scan_id):
    s = _get_scan(request.user, scan_id)
    if request.method != "POST":
        return redirect("member3_operations:scan_detail", pk=s.pk)
    report = generate_report(s, request.user)
    messages.success(request, f"Report: {report.title}")
    return redirect("member3_operations:report_list")


@role_required("admin", "analyst")
def remediation_ai(request, pk):
    r = get_object_or_404(Remediation.objects.select_related("finding", "finding__target"), pk=pk)
    if not visible_targets(request.user).filter(pk=r.finding.target_id).exists():
        raise PermissionDenied
    r.ai_explanation = build_ai_explanation(r.finding)
    r.ai_generated = True
    r.save()
    messages.success(request, "AI explanation generated.")
    return redirect("member2_assessment:finding_detail", pk=r.finding_id)
