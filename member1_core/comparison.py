from member2_assessment.models import VulnerabilityFinding
from .models import AssetChange

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _row(f):
    return {"title": f.title, "severity": f.severity, "host": f.host.hostname if f.host else ""}


def build_comparison_data(target, base_scan, compare_scan):
    # Fetch findings for both scans
    base = {(f.title, f.matched_at or ""): f for f in VulnerabilityFinding.objects.filter(scan_id=base_scan.id).select_related("host")}
    compare = {(f.title, f.matched_at or ""): f for f in VulnerabilityFinding.objects.filter(scan_id=compare_scan.id).select_related("host")}

    # Calculate differences
    new = [compare[k] for k in compare if k not in base]
    resolved = [base[k] for k in base if k not in compare]
    unchanged = [compare[k] for k in compare if k in base]

    # Sort by severity
    for c in (new, resolved, unchanged):
        c.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 9))

    # Fetch asset changes
    asset_new = list(AssetChange.objects.filter(target=target, scan_id=compare_scan.id, change_type="new"))
    asset_removed = list(AssetChange.objects.filter(target=target, scan_id=compare_scan.id, change_type="removed"))

    data = {
        "counts": {
            "new": len(new), "resolved": len(resolved), "unchanged": len(unchanged),
            "assets_new": len(asset_new), "assets_removed": len(asset_removed),
        },
        "findings": {
            "new": [_row(f) for f in new],
            "resolved": [_row(f) for f in resolved],
            "unchanged": [_row(f) for f in unchanged],
        },
        "assets": {
            "new": [{"type": a.asset_type, "identifier": a.identifier} for a in asset_new],
            "removed": [{"type": a.asset_type, "identifier": a.identifier} for a in asset_removed],
        },
    }
    summary = (
        f"{len(new)} new, {len(resolved)} resolved, {len(unchanged)} unchanged findings; "
        f"{len(asset_new)} new / {len(asset_removed)} removed assets."
    )
    return data, summary