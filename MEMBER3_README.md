# Member 3 — member3_operations (VulnTrack, SE-331)

Owner: Member 3 (Shaon). Push ONLY this folder's contents into the shared repo
(`member3_operations/` + `templates/member3_operations/`).

## What Member 3 owns

- **Scans (W1):** `ScanJob`, `ScanLog`, scan create/list/detail/run/progress,
  minimal demo scanner, Celery task stub (`tasks.py`, `services/queue.py`).
- **Recon + findings engine (W2):** full `services/scanner.py` (subdomains, DNS,
  hosts, ports, technologies, endpoints, findings, evidence, remediation),
  `Evidence` + `Remediation` models/forms/views.
- **Dashboard, reports, AI (W3):** `Notification`, `Report`, dashboard (`/`),
  notifications, PDF reports (`services/reporting.py`, ReportLab),
  AI remediation explanations (`services/ai.py`, template-based, not a live LLM).

## Files

- `member3_operations/` — `__init__.py`, `apps.py`, `models.py`, `forms.py`,
  `views.py`, `urls.py`, `admin.py`, `tasks.py`,
  `services/__init__.py`, `services/scanner.py`, `services/queue.py`,
  `services/reporting.py`, `services/ai.py`,
  `migrations/0001_initial.py` (generated from the final W3 models).
- `templates/member3_operations/` — `scan_list.html`, `scan_detail.html`,
  `dashboard.html`, `notifications.html`, `report_list.html`.

## THE one-line fix — read before pushing

The spec as printed does NOT run. Spec file `project_code_0_ix7i.txt`,
line 1826 (Week 2, `member3_operations/views.py` — "Top - ADD imports"):

```python
from member2_assessment.models import Remediation, VulnerabilityFinding
```

`Remediation` is NOT in `member2_assessment.models` — it is defined in
`member3_operations/models.py` (line 64). As printed, Django fails at startup:

```
File ".../member3_operations/views.py", line 13, in <module>
    from member2_assessment.models import Remediation, VulnerabilityFinding
ImportError: cannot import name 'Remediation' from 'member2_assessment.models'
```

Fixed in this push, `member3_operations/views.py` lines 13 + 15:

```python
from member2_assessment.models import VulnerabilityFinding
from .models import Evidence, Remediation
```

That is the ONLY change from the printed spec in this folder. If the shared
repo is merged with the printed import, the whole project fails at startup —
this is Member 3's own file, so the fix belongs in this push.

## Dependencies (must already exist in the repo — NOT in this push)

- `member1_core`: `Target` model, `BootstrapMixin` (forms),
  `role_required` / `visible_targets` (utils), `Subdomain`, `DNSRecord`.
- `member2_assessment`: `ScanProfile`, `VulnerabilityFinding`, `Host`, `Port`,
  `Technology`, `Endpoint` (scanner + views import them).
- Root/Lead files (`manage.py`, `vulntrack/settings.py`, `urls.py`,
  `templates/base.html`, `templates/shared/form.html`) are not included.

## Test (in the full project, fresh DB, 2026-11-06)

```bash
python manage.py check            # System check identified no issues (0 silenced).
python manage.py makemigrations member3_operations   # No changes detected
python manage.py migrate          # all three apps OK
python manage.py runserver        # login 200; / and /scans/ anon -> 302 to login
```

Logged-in smoke test (analyst user, authorized target, scan profile):
`/ ` dashboard 200, `/scans/` 200, create scan 302, run scan 302,
scan completed — **10 findings across 4 hosts** (12 ports; high x2, medium x4,
low x4), `/scans/1/` 200, `/scans/1/progress/` 200, `/reports/` 200,
POST `/reports/generate/1/` 302 — PDF report 4,799 bytes, `%PDF-`,
download URL 200 `application/pdf`, `/notifications/` 200 (1 notification),
`/remediation/10/ai/` 302 — `ai_generated=True`, explanation 220 chars,
`/findings/10/evidence/add/` 200. Member 2 dependency pages
(`/assessment/profiles/`, `/findings/`, `/correlations/`,
`/assessment/results/1/`, finding detail) all 200.

## Other notes / gaps

- `services/ai.py` is a template lookup by `vuln_type`, not a live LLM call —
  do not present it as real AI.
- The scanner is a demo engine (fixed `192.0.2.x` IPs, `subfinder (demo)`
  source, hardcoded finding templates) — it does not do real network
  scanning. Only scan targets you are authorised to scan.
- Migrations are a single `0001_initial.py` from the final W3 models,
  not one per week. Final DB state is equivalent.
- No other Member 3 bugs were found in this verification.
