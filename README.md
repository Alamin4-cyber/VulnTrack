# 🛡️ VulnTrack — Web Security Assessment Platform

VulnTrack is a web-based security assessment platform to automate reconnaissance,
discover web vulnerabilities, and monitor the status of authorized web assets — all
from a centralized dashboard.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [ Members](#-modules--members)


---

## ✨ Features

### Module 1 — User, Target and Scan Management
- User registration, login, profile, and role-based access control
- Target registration with authorization verification
- Scope rules (allow / exclude patterns)
- Scan profiles (recon, ports, HTTP probe, vulnerabilities)
- Scan jobs with progress monitoring and history

### Module 2 — Reconnaissance and Vulnerability Assessment
- Subdomain discovery and DNS record collection
- Live host, port, service, and technology detection
- Web endpoint discovery
- Vulnerability findings with severity and confidence classification
- Evidence storage (request/response)
- Remediation recommendations

### Module 3 — Monitoring, Reporting and Intelligent Assistance
- Scan comparison (new / resolved / unchanged findings)
- Attack surface change detection
- Finding correlation and risk relationships
- Centralized dashboard
- In-app notifications
- PDF security reports (ReportLab)
- AI-assisted remediation explanations

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+, JavaScript |
| Backend | Django 4.2+ |
| Frontend | Django Templates, Bootstrap 5, HTML, CSS |
| Database | SQLite (dev) / PostgreSQL / MySQL |
| Background | Celery + Redis (optional) |
| Reporting | ReportLab |
| Deployment | Linux, Docker |

### Project Structure

📦 VulnTrack/
│
├── 🐍 manage.py                                              🟢 W1 · 🧑‍💼 Lead
├── 📄 requirements.txt                                       🟢 W1 · 🧑‍💼 Lead
├── 📄 .gitignore                                             🟢 W1 · 🧑‍💼 Lead
├── 📖 README.md                                              🟢 W1 · 🧑‍💼 Lead
├── 🗄️ db.sqlite3                                             (generated after migrate)
│
├── 📁 vulntrack/                                             🟢 W1 · 🧑‍💼 Lead
│   ├── 🐍 init.py                                        🟢 W1
│   ├── ⚙️ settings.py                                        🟢 W1 · 🔵 ALL
│   ├── 🔗 urls.py                                            🟢 W1 → 🔴 W3 (M3 owns /)
│   └── 🌐 wsgi.py                                            🟢 W1
│
│  ═══════════════════════════════════════════════════════════════════════
│  👤 MEMBER 1 — member1_core/  (Users · Targets · Recon · Comparison)
│  ═══════════════════════════════════════════════════════════════════════
│
├── 📁 member1_core/
│   ├── 🐍 init.py                                        🟢 W1 · M1
│   ├── 🔧 apps.py                                            🟢 W1 · M1
│   ├── 📡 signals.py                                         🟢 W1 · M1
│   ├── 🛠️ utils.py                                           🟢 W1 · M1
│   │
│   ├── 🧩 models.py                                          🟢 W1 · M1 (partial)
│   │   ├── UserProfile                                      🟢 W1
│   │   ├── Target                                           🟢 W1
│   │   ├── Subdomain                                        🟡 W2
│   │   ├── DNSRecord                                        🟡 W2
│   │   ├── AssetChange                                      🔴 W3
│   │   └── ScanComparison                                   🔴 W3
│   │
│   ├── 📝 forms.py                                           🟢 W1 · M1 (partial)
│   │   ├── BootstrapMixin                                   🟢 W1
│   │   ├── RegisterForm                                     🟢 W1
│   │   ├── ProfileForm                                      🟢 W1
│   │   ├── TargetForm                                       🟢 W1
│   │   └── ComparisonForm                                   🔴 W3
│   │
│   ├── 👁️ views.py                                           🟢 W1 · M1 (partial)
│   │   ├── home                                             🟢 W1  (M3 replaces in W3)
│   │   ├── register / profile                               🟢 W1
│   │   ├── target_list / create / edit / delete / detail    🟢 W1
│   │   ├── target_verify                                    🟢 W1
│   │   ├── subdomain_list / dns_list                        🟡 W2
│   │   ├── target_detail (extended w/ subdomain+DNS)        🟡 W2
│   │   └── comparison_list / create / detail                🔴 W3
│   │
│   ├── 🔗 urls.py                                            🟢 W1 · M1 (partial)
│   │   ├── /accounts/*                                      🟢 W1
│   │   ├── /targets/*                                       🟢 W1
│   │   ├── /targets/<id>/subdomains/                        🟡 W2
│   │   ├── /targets/<id>/dns/                               🟡 W2
│   │   └── /comparisons/*                                   🔴 W3
│   │
│   ├── 🔍 comparison.py                                      🔴 W3 · M1
│   ├── 🎛️ admin.py                                           🟢 W1 → 🟡 W2 → 🔴 W3
│   └── 📁 migrations/                                        (generated per week)
│
│  ═══════════════════════════════════════════════════════════════════════
│  🔍 MEMBER 2 — member2_assessment/  (Scope · Profiles · Recon · Findings)
│  ═══════════════════════════════════════════════════════════════════════
│
├── 📁 member2_assessment/
│   ├── 🐍 init.py                                        🟢 W1 · M2
│   ├── 🔧 apps.py                                            🟢 W1 · M2
│   │
│   ├── 🧩 models.py                                          🟢 W1 · M2 (partial)
│   │   ├── ScopeRule                                        🟢 W1
│   │   ├── ScanProfile                                      🟢 W1
│   │   ├── Host                                             🟡 W2
│   │   ├── Port                                             🟡 W2
│   │   ├── Technology                                       🟡 W2
│   │   ├── Endpoint                                         🟡 W2
│   │   ├── VulnerabilityFinding                             🟡 W2
│   │   └── FindingCorrelation                               🔴 W3
│   │
│   ├── 📝 forms.py                                           🟢 W1 · M2
│   │   ├── ScopeRuleForm                                    🟢 W1
│   │   └── ScanProfileForm                                  🟢 W1
│   │
│   ├── 👁️ views.py                                           🟢 W1 · M2 (partial)
│   │   ├── profile_list / create / edit                     🟢 W1
│   │   ├── scope_list / create / edit / delete              🟢 W1
│   │   ├── results                                          🟡 W2
│   │   ├── finding_list / finding_detail                    🟡 W2
│   │   ├── finding_detail (extended w/ correlations)        🔴 W3
│   │   ├── correlation_list                                 🔴 W3
│   │   └── rebuild_correlations                             🔴 W3
│   │
│   ├── 🔗 urls.py                                            🟢 W1 · M2 (partial)
│   │   ├── /assessment/profiles/*                           🟢 W1
│   │   ├── /assessment/targets/<id>/scopes/*                🟢 W1
│   │   ├── /assessment/scopes/*                             🟢 W1
│   │   ├── /assessment/results/<scan_id>/                   🟡 W2
│   │   ├── /assessment/findings/*                           🟡 W2
│   │   └── /assessment/correlations/*                       🔴 W3
│   │
│   ├── ⚙️ services.py                                        🔴 W3 · M2   (correlate_scan)
│   ├── 🎛️ admin.py                                           🟢 W1 → 🟡 W2 → 🔴 W3
│   └── 📁 migrations/                                        (generated per week)
│
│  ═══════════════════════════════════════════════════════════════════════
│  🚀 MEMBER 3 — member3_operations/  (Scans · Dashboard · Reports · AI)
│  ═══════════════════════════════════════════════════════════════════════
│
├── 📁 member3_operations/
│   ├── 🐍 init.py                                        🟢 W1 · M3
│   ├── 🔧 apps.py                                            🟢 W1 · M3
│   │
│   ├── 🧩 models.py                                          🟢 W1 · M3 (partial)
│   │   ├── ScanJob                                          🟢 W1
│   │   ├── ScanLog                                          🟢 W1
│   │   ├── Evidence                                         🟡 W2
│   │   ├── Remediation                                      🟡 W2
│   │   ├── Notification                                     🔴 W3
│   │   └── Report                                           🔴 W3
│   │
│   ├── 📝 forms.py                                           🟢 W1 · M3 (partial)
│   │   ├── ScanJobForm                                      🟢 W1
│   │   ├── EvidenceForm                                     🟡 W2
│   │   └── RemediationForm                                  🟡 W2
│   │
│   ├── 👁️ views.py                                           🟢 W1 · M3 (partial)
│   │   ├── scan_list / scan_create                          🟢 W1
│   │   ├── scan_detail / scan_run / scan_progress           🟢 W1
│   │   ├── evidence_create / evidence_edit                  🟡 W2
│   │   ├── remediation_edit                                 🟡 W2
│   │   ├── dashboard                                        🔴 W3
│   │   ├── notification_list / notification_read            🔴 W3
│   │   ├── report_list / report_generate                    🔴 W3
│   │   └── remediation_ai                                   🔴 W3
│   │
│   ├── 🔗 urls.py                                            🟢 W1 → 🔴 W3
│   │   ├── /scans/                                          🟢 W1
│   │   ├── /scans/new/                                      🟢 W1
│   │   ├── /scans/<id>/                                     🟢 W1
│   │   ├── /scans/<id>/run/                                 🟢 W1
│   │   ├── /scans/<id>/progress/                            🟢 W1
│   │   ├── /findings/<id>/evidence/add/                     🟡 W2
│   │   ├── /evidence/<id>/edit/                             🟡 W2
│   │   ├── /findings/<id>/remediation/                      🟡 W2
│   │   ├── /                                              🔴 W3  (dashboard takes over)
│   │   ├── /remediation/<id>/ai/                            🔴 W3
│   │   ├── /notifications/                                  🔴 W3
│   │   ├── /notifications/<id>/read/                        🔴 W3
│   │   ├── /reports/                                        🔴 W3
│   │   └── /reports/generate/<scan_id>/                     🔴 W3
│   │
│   ├── 🎛️ admin.py                                           🟢 W1 → 🟡 W2 → 🔴 W3
│   ├── ⏱️ tasks.py                                           🟢 W1 · M3
│   │
│   ├── 📁 services/
│   │   ├── 🐍 init.py                                    🟢 W1 · M3
│   │   ├── 🔬 scanner.py                                     🟢 W1 (minimal) → 🟡 W2 (full)
│   │   ├── 📤 queue.py                                       🟢 W1 · M3
│   │   ├── 📄 reporting.py                                   🔴 W3 · M3
│   │   └── 🤖 ai.py                                          🔴 W3 · M3
│   │
│   └── 📁 migrations/                                        (generated per week)
│
│  ═══════════════════════════════════════════════════════════════════════
│  🎨 TEMPLATES — templates/
│  ═══════════════════════════════════════════════════════════════════════
│
├── 📁 templates/
│   ├── 🖼️ base.html                                          🟢 W1 · 🧑‍💼 Lead
│   │                                                        → 🔴 W3 (add Dashboard link)
│   │
│   ├── 📁 shared/                                            🟢 W1 · 🧑‍💼 Lead
│   │   └── 🖼️ form.html                                     🟢 W1
│   │
│   ├── 📁 registration/                                      🟢 W1 · M1
│   │   └── 🖼️ login.html                                    🟢 W1
│   │
│   ├── 📁 member1_core/                                      🟢 W1 · M1
│   │   ├── 🖼️ profile.html                                  🟢 W1
│   │   ├── 🖼️ target_list.html                              🟢 W1
│   │   ├── 🖼️ target_detail.html                            🟢 W1
│   │   │                                                   → 🟡 W2 (add subdomain+DNS)
│   │   │                                                   → 🔴 W3 (add comparison+assets)
│   │   ├── 🖼️ subdomains.html                               🟡 W2
│   │   ├── 🖼️ dns_records.html                              🟡 W2
│   │   ├── 🖼️ comparison_list.html                          🔴 W3
│   │   └── 🖼️ comparison_detail.html                        🔴 W3
│   │
│   ├── 📁 member2_assessment/                                🟢 W1 · M2
│   │   ├── 🖼️ profile_list.html                             🟢 W1
│   │   ├── 🖼️ scope_list.html                               🟢 W1
│   │   ├── 🖼️ results.html                                  🟡 W2
│   │   ├── 🖼️ finding_list.html                             🟡 W2
│   │   ├── 🖼️ finding_detail.html                           🟡 W2
│   │   │                                                   → 🔴 W3 (add correlations)
│   │   └── 🖼️ correlations.html                             🔴 W3
│   │
│   └── 📁 member3_operations/                                🟢 W1 · M3
│       ├── 🖼️ scan_list.html                                🟢 W1
│       ├── 🖼️ scan_detail.html                              🟢 W1
│       │                                                   → 🟡 W2 (add findings + evidence)
│       │                                                   → 🔴 W3 (add PDF button)
│       ├── 🖼️ dashboard.html                                🔴 W3
│       ├── 🖼️ notifications.html                            🔴 W3
│       └── 🖼️ report_list.html                              🔴 W3
│
│  ═══════════════════════════════════════════════════════════════════════
│  📄 GENERATED FILES
│  ═══════════════════════════════════════════════════════════════════════
│
└── 📁 media/                                                 (generated)
└── 📁 reports/                                           🔴 W3 · M3
└── 📄 *.pdf                                          (generated PDF reports)

## 👥  Members

    MD.Al-amin Hosen
    Tarikul Islam
    Shaon

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Alamin4-cyber/vulntrack.git
cd vulntrack