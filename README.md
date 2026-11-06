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

## 📁 Project Structure

> 🏗️ **VulnTrack** is organized into 3 independent Django apps — one per team member — plus a shared template layer.

```
📦 VulnTrack/
│
├── ⚙️  manage.py                    Django entry point
├── 📋 requirements.txt               Python dependencies
├── 🚫 .gitignore                     Git ignore rules
├── 📖 README.md                      You are here
├── 🗄️  db.sqlite3                    Generated after migrate
│
├── 🎯 vulntrack/                     Django project config
│   ├── 🔧 __init__.py
│   ├── ⚙️  settings.py                All project settings
│   ├── 🔗 urls.py                     Root URL router
│   └── 🌐 wsgi.py                     WSGI entry
│
├── 👤 member1_core/                  USER & RECON LAYER
│   ├── 🧩 __init__.py
│   ├── 🎛️  apps.py
│   ├── 📡 signals.py                  Model signals
│   ├── 🛠️  utils.py                    Helper utilities
│   ├── 🗃️  models.py                   UserProfile · Target · Subdomain
│   │                                  · DNSRecord · AssetChange · ScanComparison
│   ├── 📝 forms.py                    Register · Profile · Target · Comparison
│   ├── 👁️  views.py                    CRUD + verification views
│   ├── 🔗 urls.py                     /accounts/ · /targets/ · /comparisons/
│   ├── 🔍 comparison.py               Scan diff engine
│   ├── 🎨 admin.py                    Django admin registration
│   └── 📁 migrations/                 Auto-generated
│       └── 🧩 __init__.py
│
├── 🕵️ member2_assessment/            ASSESSMENT LAYER
│   ├── 🧩 __init__.py
│   ├── 🎛️  apps.py
│   ├── 🗃️  models.py                   ScopeRule · ScanProfile · Host · Port
│   │                                  · Technology · Endpoint · VulnerabilityFinding
│   │                                  · FindingCorrelation
│   ├── 📝 forms.py                    ScopeRuleForm · ScanProfileForm
│   ├── 👁️  views.py                    Profiles · Scopes · Results · Findings
│   ├── 🔗 urls.py                     /assessment/profiles/ · /scopes/ · /findings/
│   ├── ⚡ services.py                  correlate_scan() engine
│   ├── 🎨 admin.py
│   └── 📁 migrations/
│       └── 🧩 __init__.py
│
├── 🚀 member3_operations/            OPERATIONS & AI LAYER
│   ├── 🧩 __init__.py
│   ├── 🎛️  apps.py
│   ├── 🗃️  models.py                   ScanJob · ScanLog · Evidence
│   │                                  · Remediation · Notification · Report
│   ├── 📝 forms.py                    ScanJob · Evidence · Remediation
│   ├── 👁️  views.py                    Scans · Dashboard · Notifications · Reports
│   ├── 🔗 urls.py                     /scans/ · /notifications/ · /reports/
│   ├── 🎨 admin.py
│   ├── ⏱️  tasks.py                    Celery async tasks
│   ├── 📁 services/
│   │   ├── 🧩 __init__.py
│   │   ├── 🔬 scanner.py              Core scanner engine
│   │   ├── 📤 queue.py                Task queue handler
│   │   ├── 📄 reporting.py            PDF/CSV report generator
│   │   └── 🤖 ai.py                   AI remediation suggestions
│   └── 📁 migrations/
│       └── 🧩 __init__.py
│
├── 🎨 templates/                     ALL HTML TEMPLATES
│   ├── 🖼️  base.html                  Master layout
│   ├── 📁 shared/
│   │   └── 📝 form.html               Reusable form template
│   ├── 📁 registration/
│   │   └── 🔐 login.html
│   ├── 📁 member1_core/
│   │   ├── 👤 profile.html
│   │   ├── 🎯 target_list.html
│   │   ├── 📊 target_detail.html
│   │   ├── 🌐 subdomains.html
│   │   ├── 📡 dns_records.html
│   │   ├── ⚖️  comparison_list.html
│   │   └── 🔍 comparison_detail.html
│   ├── 📁 member2_assessment/
│   │   ├── 📋 profile_list.html
│   │   ├── 🎚️  scope_list.html
│   │   ├── 📊 results.html
│   │   ├── 🐛 finding_list.html
│   │   ├── 🔎 finding_detail.html
│   │   └── 🔗 correlations.html
│   └── 📁 member3_operations/
│       ├── 🚀 scan_list.html
│       ├── 📈 scan_detail.html
│       ├── 📊 dashboard.html
│       ├── 🔔 notifications.html
│       └── 📄 report_list.html
│
├── 🖼️  media/                        User uploads (gitignored)
│   └── 📌 .gitkeep
│
└── 📄 reports/                       Generated PDF reports
    └── 📌 .gitkeep
```
## 👥  Members

    MD.Al-amin Hosen
    Tarikul Islam
    Shaon

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Alamin4-cyber/vulntrack.git
cd vulntrack
