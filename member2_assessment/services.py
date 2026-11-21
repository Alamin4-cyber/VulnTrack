from itertools import combinations
from .models import FindingCorrelation, VulnerabilityFinding

# ===== WEEK 3 =====
def _evaluate(a, b):
    high = {"critical", "high"}
    # If both are High/Critical
    if a.severity in high and b.severity in high:
        return ("shared_host_critical_chain", f"Both affect {a.host.hostname}; chaining increases impact.", 85)
    
    # If at least one is High/Critical
    if a.severity in high or b.severity in high:
        return ("shared_host_exposure", f"Share host {a.host.hostname}; review together.", 55)
        
    return (None, "", 0)


def correlate_scan(scan_id):
    FindingCorrelation.objects.filter(primary__scan_id=scan_id).delete()
    findings = list(VulnerabilityFinding.objects.filter(scan_id=scan_id).select_related("host"))
    created = 0
    for a, b in combinations(findings, 2):
        # Only correlate if they are on the same host
        if not a.host_id or a.host_id != b.host_id:
            continue
        rel, note, score = _evaluate(a, b)
        if rel:
            FindingCorrelation.objects.get_or_create(
                primary=a, related=b,
                defaults={"relationship": rel, "risk_note": note, "score": score},
            )
            created += 1
    return created