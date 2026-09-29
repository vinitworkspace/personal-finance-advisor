# Personal Finance Advisor Bot — Documentation Index

Welcome to the comprehensive technical documentation for the **Personal Finance Advisor Bot**. This documentation suite is designed for students, developers, and viva examination panels to understand every architectural decision, security protection, algorithm, and line of code.

---

## Document Roadmap & Reading Order

| Doc # | Title | Target Audience & Focus |
| :--- | :--- | :--- |
| [**01**](./01_ARCHITECTURE_AND_DESIGN.md) | **Architecture & Design Patterns** | Multi-tier architecture, Blueprint pattern, Service pattern, Decorators, and Directory layout. |
| [**02**](./02_DATABASE_AND_MODELS.md) | **Database Architecture & Data Models** | SQLite schema, ERD diagrams, SQLAlchemy models, cascading deletes, and Windows URI resolution. |
| [**03**](./03_SECURITY_AND_AUTHENTICATION.md) | **Security, Auth & Tenant Isolation** | PBKDF2-SHA256 password hashing, timing attack protection, session fixation mitigation, IDOR defense, and XSS/CSRF security. |
| [**04**](./04_AI_ENGINE_AND_FALLBACK.md) | **AI Engine & Offline Fallback** | Gemini 1.5 Flash client, prompt engineering, context grounding, real-time auto-categorization, and the offline heuristic rules engine. |
| [**05**](./05_FINANCIAL_MATHEMATICS_AND_FORMULAS.md) | **Financial Mathematics & Algorithms** | Mathematical formulations for Net Balance, Savings Rate %, Daily Velocity, Month-End Projections, and 50/30/20 benchmarks. |
| [**06**](./06_API_REFERENCE.md) | **Complete REST API Reference** | Complete endpoint catalogue: methods, parameters, request payloads, and JSON response envelopes. |
| [**07**](./07_HOW_TO_RUN_AND_BROWSER_GUIDE.md) | **How to Run & Complete Browser Guide** | Step-by-step installation, one-click launcher scripts, demo logins, page-by-page UI tour, and troubleshooting. |
| [**08**](./08_VIVA_QUESTIONS_AND_ANSWERS.md) | **Viva Examination Prep & Model Answers** | 18+ detailed viva exam questions with model answers across architecture, security, database, AI, and math. |

---

## 📄 Complete Microsoft Word (.docx) Report

A fully formatted, publication-grade Microsoft Word project report compiling all 8 chapters (complete with title page, executive summary, stylized code blocks, and formatted tables) is available here:

👉 [**`Personal_Finance_Advisor_Bot_Documentation.docx`**](./Personal_Finance_Advisor_Bot_Documentation.docx)

To regenerate or update this Word document at any time:
```powershell
python build_docx.py
```

---

## Quick Start
To launch the app immediately in your default web browser on Windows:
```cmd
.\run_app.bat
```
Or with PowerShell:
```powershell
.\run_app.ps1
```
Or standard Python:
```powershell
python app.py
```
Then visit `http://127.0.0.1:5000` in your browser. Demo credentials:
- **Username**: `demo_user`
- **Password**: `DemoPass@123`
*(Or click the "Fill Demo Credentials" button on the login screen).*
