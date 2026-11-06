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

VulnTrack/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── db.sqlite3 (generated)
├── vulntrack/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── member1_core/
│   ├── __init__.py
│   ├── apps.py
│   ├── signals.py
│   ├── utils.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── comparison.py
│   ├── admin.py
│   └── migrations/
├── member2_assessment/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   ├── admin.py
│   └── migrations/
├── member3_operations/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tasks.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scanner.py
│   │   ├── queue.py
│   │   ├── reporting.py
│   │   └── ai.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── shared/
│   │   └── form.html
│   ├── registration/
│   │   └── login.html
│   ├── member1_core/
│   │   ├── profile.html
│   │   ├── target_list.html
│   │   ├── target_detail.html
│   │   ├── subdomains.html
│   │   ├── dns_records.html
│   │   ├── comparison_list.html
│   │   └── comparison_detail.html
│   ├── member2_assessment/
│   │   ├── profile_list.html
│   │   ├── scope_list.html
│   │   ├── results.html
│   │   ├── finding_list.html
│   │   ├── finding_detail.html
│   │   └── correlations.html
│   └── member3_operations/
│       ├── scan_list.html
│       ├── scan_detail.html
│       ├── dashboard.html
│       ├── notifications.html
│       └── report_list.html
├── media/
└── reports/

## 👥  Members

    MD.Al-amin Hosen
    Tarikul Islam
    Shaon

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Alamin4-cyber/vulntrack.git
cd vulntrack
