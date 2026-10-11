# VinZie Budget Tracker 💰🤖
> **An AI-powered full-stack personal finance planning, budgeting, and management web application.**  
> Built with **Python, Flask, SQLite, Vanilla CSS/JS, Chart.js, and Google Gemini AI**.

---

## 📋 Table of Contents
1. [Documentation Suite (`docs/`)](#-documentation-suite-for-learning--viva)
2. [Project Overview](#-project-overview)
3. [Key Features](#-key-features)
4. [User Scenarios Supported](#-user-scenarios-supported)
5. [System Architecture](#-system-architecture)
6. [Database Schema & ER Design](#-database-schema--er-design)
7. [Technology Stack](#-technology-stack)
8. [Installation & Windows Setup Guide](#-installation--windows-setup-guide)
9. [Environment Configuration & API Keys](#-environment-configuration--api-keys)
10. [Running the Application in Browser](#-running-the-application-in-browser)
11. [REST API Documentation](#-rest-api-documentation)
12. [Automated Testing & Manual Checklist](#-automated-testing--manual-checklist)
13. [Cybersecurity & Data Privacy Implementation](#-cybersecurity--data-privacy-implementation)
14. [Deployment Guide (Render / PythonAnywhere)](#-deployment-guide)
15. [Git & GitHub Setup Guide](#-git--github-setup-guide)
16. [Viva Defense Guide & Q&A](#-viva-defense-guide--qa)
17. [Future Improvements](#-future-improvements)

---

## 📚 Documentation Suite (For Learning & Viva)

The project includes an in-depth, dedicated documentation library in the [`docs/`](./docs/) directory:

- 📖 [**01. Architecture & Design Patterns**](./docs/01_ARCHITECTURE_AND_DESIGN.md): Multi-tier architecture, Blueprint pattern, Service layer pattern, and decorators.
- 🗄️ [**02. Database Architecture & Models**](./docs/02_DATABASE_AND_MODELS.md): SQLite schema, ERD diagram, SQLAlchemy models, and cascading deletes.
- 🔐 [**03. Security & Authentication**](./docs/03_SECURITY_AND_AUTHENTICATION.md): PBKDF2 password hashing, session fixation mitigation, IDOR defense, and XSS/CSRF security.
- 🤖 [**04. AI Engine & Offline Fallback**](./docs/04_AI_ENGINE_AND_FALLBACK.md): Gemini 1.5 Flash client, prompt engineering, and offline heuristic rules engine.
- 📐 [**05. Financial Mathematics & Algorithms**](./docs/05_FINANCIAL_MATHEMATICS_AND_FORMULAS.md): Formulas for Net Balance, Savings Rate %, Daily Velocity, Month-End Projections, and 50/30/20 benchmarks.
- 📡 [**06. Complete REST API Reference**](./docs/06_API_REFERENCE.md): Full catalogue of HTTP endpoints, parameters, and JSON response models.
- 🖥️ [**07. How to Run & Complete Browser Guide**](./docs/07_HOW_TO_RUN_AND_BROWSER_GUIDE.md): Step-by-step setup, one-click launcher scripts, demo logins, and page-by-page tour.
- 🎓 [**08. Viva Questions & Model Answers**](./docs/08_VIVA_QUESTIONS_AND_ANSWERS.md): 18+ high-impact viva voce questions and model answers across engineering, security, database, and AI.
- 📄 [**Personal_Finance_Advisor_Bot_Documentation.docx**](./docs/Personal_Finance_Advisor_Bot_Documentation.docx): **Complete Compiled Microsoft Word Project Report** containing all 8 chapters, formatted tables, code boxes, and title page.

---

## 🌟 Project Overview

The **Personal Finance Advisor Bot** helps individuals, salaried professionals, freelancers, and students take control of their finances. It provides cash flow ledgers, monthly category budgets, daily spending velocity calculations, and an interactive **AI Financial Advisor** powered by **Google Gemini 1.5 Flash**.

> **Important Educational Notice:**  
> The system provides educational budgeting assistance and analytical simulations. It does not provide certified financial advice or guaranteed investment returns.

---

## 🚀 Key Features

- **📊 Comprehensive Financial Command Center**: Real-time KPI cards for Total Income, Outflows, Net Balance, and Savings Rate %.
- **💰 Inflow Management**: Record recurring salaries, freelance project payouts, allowances, and side-hustles with date and source tracking.
- **💳 Daily Expense Ledger**: Log day-to-day outlays categorized across Food, Rent, Transport, Utilities, Entertainment, Shopping, Healthcare, Education, EMI, and Other.
- **✨ Real-time AI Expense Auto-Categorizer**: Debounced NLP classifier suggesting categories from plain-text descriptions (e.g. *"Uber to college"* $\rightarrow$ `Transport`).
- **🎯 Dynamic Budget Guardrails & Threshold Alerts**: Set monthly category ceilings with color-shifting visual progress meters:
  - **Safe** ($< 75\%$ used): Green
  - **Warning** ($75\% - 99.9\%$ used): Amber alert
  - **Danger / Overrun** ($\ge 100\%$ used): Crimson alert with exact excess calculation.
- **⚡ Spending Velocity & Burn Rate Analytics**: Computes average daily spending ($\text{Outflows} / \text{Days Elapsed}$) and forecasts month-end spend.
- **📈 Interactive Visualizations (Chart.js)**: 6-Month cashflow trajectory bar charts and categorical Pareto doughnut charts.
- **🤖 Grounded AI Financial Advisor Chatbot**: Conversational assistant answering natural-language queries (*"Where am I spending most?"*, *"How can I save ₹5,000 more?"*, *"How to build an emergency fund?"*) using real user financial data.
- **🛡️ 100% Offline Heuristic Fallback Engine**: If no Gemini API key is configured or the external network is unreachable, the system automatically uses an offline rule-based advisor.
- **📑 Printable Executive Monthly Reports**: Formatted monthly statements with category audit tables, scorecards, and print-to-PDF support (`window.print()`).
- **📥 CSV Ledger Export**: Export all historical transactions into an RFC-4180 standard spreadsheet.
- **⚙️ Profile & Currency Selector**: Seamlessly switch between ₹ (INR), $ (USD), € (EUR), £ (GBP), and ¥ (JPY).

---

## 👥 User Scenarios Supported

1. **Salaried Professional (Scenario 1)**: Tracks stable monthly paychecks against fixed rent, grocery bills, and EMIs with automated savings rate tracking.
2. **College Student (Scenario 2)**: Budgets limited allowances, tracks micro-spends, and receives actionable advice on curbing discretionary dining out.
3. **Freelancer / Independent Contractor (Scenario 3)**: Manages irregular, multi-client cash inflows with emergency fund recommendations.
4. **Household Manager (Scenario 4)**: Consolidates family utilities, education fees, groceries, and medical expenses with printable audits.

---

## 🏗️ System Architecture

```text
[User Browser / Mobile Device]
       │
       ▼ (HTTP / HTML5 / REST JSON)
┌────────────────────────────────────────────────────────┐
│                   Flask Application                    │
├────────────────────────────────────────────────────────┤
│ Presentation Layer:                                    │
│   • Jinja2 Server-Rendered Templates (base, dashboard) │
│   • Modern Glassmorphism CSS Design System (style.css) │
│   • Vanilla JavaScript UI Controllers (main, dashboard)│
│   • Chart.js 4.4 Data Visualizations                   │
├────────────────────────────────────────────────────────┤
│ Security & Middleware:                                 │
│   • Session Guard (@login_required)                    │
│   • PBKDF2-SHA256 Password Hashing (Werkzeug)          │
│   • Multi-Tenant User Isolation (filter by user_id)     │
├────────────────────────────────────────────────────────┤
│ Controller Layer (Flask Blueprints):                   │
│   • auth_bp, dashboard_bp, income_bp, expenses_bp      │
│   • budget_bp, analytics_bp, ai_bp, reports_bp         │
├────────────────────────────────────────────────────────┤
│ Business Logic & Service Layer:                        │
│   • FinanceService: Math, Cashflow, Balances           │
│   • BudgetService: Threshold Limits & Overrun Alerts   │
│   • AnalyticsService: Velocity Burn Rate, Pareto Share │
│   • ReportService: Snapshot Compiler & CSV Exporter    │
│   • GeminiService: GenAI Client + Heuristic Fallback   │
├────────────────────────────────────────────────────────┤
│ Persistence Layer:                                     │
│   • SQLAlchemy 2.0 ORM Models                          │
│   • SQLite Database (database/finance.db)              │
│   • External Google Gemini 1.5 Flash API via HTTPS     │
└────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema & ER Design

```text
  +------------------+             +--------------------+
  |      USERS       | 1         * |       INCOME       |
  +------------------+-------------+--------------------+
  | id (PK)          |             | id (PK)            |
  | name             |             | user_id (FK)       |
  | email (Unique)   |             | amount             |
  | password_hash    |             | source             |
  | currency         |             | date               |
  | created_at       |             | description        |
  +------------------+             +--------------------+
          │ 1
          │
          │ *                      +--------------------+
          ├────────────────────────|      EXPENSES      |
          │                        +--------------------+
          │                        | id (PK)            |
          │                        | user_id (FK)       |
          │                        | amount             |
          │                        | category           |
          │                        | date               |
          │                        | description        |
          │                        | payment_method     |
          │                        +--------------------+
          │ 1
          │
          │ *                      +--------------------+
          ├────────────────────────|      BUDGETS       |
          │                        +--------------------+
          │                        | id (PK)            |
          │                        | user_id (FK)       |
          │                        | category           |
          │                        | amount             |
          │                        | month, year        |
          │                        +--------------------+
          │ 1
          │
          │ *                      +--------------------+
          └────────────────────────| FINANCIAL_REPORTS  |
                                   +--------------------+
                                   | id (PK)            |
                                   | user_id (FK)       |
                                   | month, year        |
                                   | total_income       |
                                   | total_expenses     |
                                   | total_savings      |
                                   | savings_percentage |
                                   | ai_summary         |
                                   +--------------------+
```

- **Cascading Deletions**: Deleting a user automatically purges all associated transactions, budgets, and historical reports (`cascade='all, delete-orphan'`).
- **Composite Unique Constraints**:
  - `uq_user_category_month_year`: Prevents duplicate category budgets in the same month.
  - `uq_user_report_month_year`: Ensures exactly one cached report per month.

---

## 💻 Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.11, Flask 3.1, Werkzeug 3.1 |
| **ORM & Database** | Flask-SQLAlchemy 3.1, SQLite 3 |
| **Artificial Intelligence** | Google Gemini 1.5 Flash (`google.generativeai` / `google.genai`) + Heuristic NLP Fallback |
| **Frontend Styling** | Vanilla Modern CSS3, CSS Custom Properties, Glassmorphism, Google Fonts (`Plus Jakarta Sans`, `Inter`) |
| **Frontend Scripting** | Vanilla Modern JavaScript (ES6+), Chart.js 4.4 |
| **Testing** | Python `unittest` standard library |
| **Configuration** | `python-dotenv` with `.env` files |

---

## ⚙️ Installation & Windows Setup Guide

### Prerequisites
- Windows 10/11
- Python 3.10+ installed ([python.org](https://www.python.org/)) with **"Add Python to PATH"** checked.
- VS Code or any text editor.

### Step 1: Open Project in Terminal
Open PowerShell or Command Prompt:
```powershell
cd "d:\VINIT PERSONAL\VINZIE PROJECTS\personal-finance-advisor"
```

### Step 2: Create and Activate Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration & API Keys

The application reads secrets from `.env`. A default `.env` is created automatically with development secrets.

1. Open `.env` in VS Code:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=dev_secret_key_personal_finance_advisor_2026_x89a
   DATABASE_URL=sqlite:///database/finance.db

   # Optional: Google Gemini AI Key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
2. **Getting a Free Gemini API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/).
   - Click **"Get API key"** and create a free key.
   - Paste the key in `GEMINI_API_KEY=...` in your `.env`.
   - *Note: If left blank, the system automatically uses the built-in Offline Heuristic Fallback Engine with zero disruption!*

---

## 🚀 Running the Application in Browser

### 1. Initialize and Seed the SQLite Database
```powershell
python init_db.py
```
*Creates all database tables and seeds 6 months of realistic transactions for the demo account (`demo_user` with password `DemoPass@123`).*

### 2. Launch the Application & Open Browser

You can start the app and automatically open your default browser using any of these methods:

#### Method A: One-Click Windows Batch Launcher (Double-Click or Command)
```cmd
.\run_app.bat
```
*(Automatically activates virtual environment if present, launches Flask, and opens `http://127.0.0.1:5000` in your default browser).*

#### Method B: PowerShell Launcher
```powershell
.\run_app.ps1
```

#### Method C: Python Browser Launcher
```powershell
python run_app.py
```

#### Method D: Standard Flask Server
```powershell
python app.py
```
*Then manually open your browser to **`http://127.0.0.1:5000`**.*

### 3. Log In to the Dashboard
- On the login page, click **`⚡ Quick Demo Fill`** to automatically populate:
  - **Username**: `demo_user`
  - **Password**: `DemoPass@123`
- Click **Sign In** to access your dashboard. For a complete UI tour and screenshot walkthrough, see [**`docs/07_HOW_TO_RUN_AND_BROWSER_GUIDE.md`**](./docs/07_HOW_TO_RUN_AND_BROWSER_GUIDE.md).

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Sample Request / Response |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user | `{"name":"Alex", "email":"alex@test.com", "password":"...", "currency":"₹"}` |
| `POST` | `/api/auth/login` | Authenticate user | `{"email":"demo@finance.test", "password":"..."}` |
| `GET` | `/api/auth/me` | Fetch active user profile | Returns `{user: {id, name, email, currency}}` |
| `GET` | `/api/income` | Query income list | Query params: `?month=10&year=2026&source=Salary` |
| `POST` | `/api/income` | Record income entry | `{"amount": 50000, "source": "Salary", "date": "2026-10-01"}` |
| `GET` | `/api/expenses` | Query expense list | Query params: `?month=10&year=2026&category=Food` |
| `POST` | `/api/expenses` | Record expense | `{"amount": 1500, "category": "Food", "date": "2026-10-05"}` |
| `GET` | `/api/budgets/status` | Real-time budget alerts | Returns `{budget_list: [...], alerts: [...], overall_utilization: 65.4}` |
| `GET` | `/api/analytics/charts` | Chart.js ready payloads | Returns `{category_chart, trend_chart, velocity}` |
| `POST` | `/api/ai/categorize` | NLP category prediction | `{"description": "Dominos pizza order"}` $\rightarrow$ `{"category": "Food"}` |
| `POST` | `/api/ai/chat` | Conversational financial Q&A | `{"message": "Where am I spending most?"}` |
| `POST` | `/api/ai/advice` | Generate strategic report | Returns markdown advice report |
| `GET` | `/reports/export/csv` | Download CSV ledger | Attachment download of all transactions |

---

## 🧪 Automated Testing & Manual Checklist

### Automated Test Suite
The project contains 42 automated unit tests across 6 dedicated test modules using Python's standard library `unittest`:
```powershell
python -m unittest discover tests
```

**Expected Result:**
```text
..........................................
----------------------------------------------------------------------
Ran 42 tests in 6.747s

OK
```

### Manual Testing Checklist for Demonstration
- [x] **Registration**: Register new user; verify that duplicate email is blocked.
- [x] **Login / Logout**: Verify password hashing and session clearance.
- [x] **Unauthorized Access**: Attempting to visit `/dashboard` while logged out redirects to `/login`.
- [x] **Add Income**: Add salary/freelance income; verify Total Income updates immediately.
- [x] **Add Expense with AI**: Type `"Uber to college"`; verify the AI suggests `Transport`. Click to apply.
- [x] **Budget Guardrails**: Set a budget of ₹5,000 for Food. Add an expense of ₹6,000. Verify the danger alert banner pops up stating: *"Food budget exceeded by ₹1,000.00"*.
- [x] **Interactive Charts**: Open Dashboard; verify grouped Bar chart and Doughnut chart render with custom tooltips.
- [x] **AI Chat Advisor**: Go to `/advisor`. Click *"Where am I spending the most?"*. Verify the AI responds with your real highest category.
- [x] **Print Monthly Report**: Open `/reports` and click *"Print / Save PDF"*. Verify navigation elements hide and the clean report card prints.
- [x] **CSV Export**: Click *"Export All (CSV)"*. Open the file in Excel; verify all records are present.

---

## 🛡️ Cybersecurity & Data Privacy Implementation

1. **Cryptographic Password Hashing**: Passwords are never stored in plaintext. Werkzeug's `generate_password_hash` uses **PBKDF2-SHA256** with unique salts.
2. **Tenant / User Data Isolation**: Every database query scopes transactions by `user_id == current_user.id`. User 1 can never access or modify User 2's financial data.
3. **Session Security**:
   - `session.clear()` is called upon authentication to prevent **Session Fixation Attacks**.
   - `SESSION_COOKIE_HTTPONLY = True` prevents client-side XSS cookie theft.
   - `SESSION_COOKIE_SAMESITE = 'Lax'` defends against Cross-Site Request Forgery (CSRF).
4. **Open Redirect Mitigation**: Form redirect targets are strictly validated with `next_page.startswith('/')`.
5. **AI Privacy & Context Grounding**: The application never transmits private user credentials or passwords to external AI APIs. Only sanitized numerical summaries are sent.

---

## 🌐 Deployment Guide

### Beginner-Friendly Deployment: Render.com
1. Create a free account at [render.com](https://render.com/).
2. Push your project repository to GitHub.
3. Click **New +** $\rightarrow$ **Web Service**.
4. Connect your GitHub repository.
5. Set the following build and run settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python init_db.py`
   - **Start Command:** `gunicorn app:app` (or `python app.py`)
6. In **Environment Variables**, add:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `GEMINI_API_KEY`: *(Your Google AI key)*
7. Click **Deploy**. Your app will be live with a free HTTPS URL.

---

## 🐙 Git & GitHub Setup Guide

To push this codebase to your GitHub profile:

```powershell
cd "d:\VINIT PERSONAL\VINZIE PROJECTS\personal-finance-advisor"
git init
git add .
git commit -m "feat: complete personal finance advisor bot with AI and analytics"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/personal-finance-advisor.git
git push -u origin main
```

---

## 🎓 Viva Defense Guide & Q&A

### High-Level Pitch for Examiners
> *"Personal Finance Advisor Bot is a full-stack personal financial planning application built using Flask, SQLite, Vanilla CSS/JS, and Google Gemini AI. It addresses the common problem of budget overruns by calculating daily burn rates, visualizing cash flow patterns, and using an AI financial assistant grounded in real stored transaction figures. It adheres strictly to cybersecurity best practices, including PBKDF2 password hashing, session fixation prevention, and tenant-isolated database access."*

### Top 15 Viva Questions and Answers

#### Q1: What software architecture does this application follow?
**Answer:** The project follows a multi-tier separation of concerns:
- **Presentation Layer:** Jinja2 templates, CSS design tokens, and JavaScript modules.
- **Controller Layer:** Flask Blueprints (`auth_bp`, `income_bp`, `expenses_bp`, `budget_bp`, etc.).
- **Service Layer:** `FinanceService`, `BudgetService`, `AnalyticsService`, `GeminiService`, and `ReportService`.
- **Persistence Layer:** SQLAlchemy ORM with SQLite.

#### Q2: Why use SQLite instead of MySQL or PostgreSQL?
**Answer:** SQLite is serverless, zero-configuration, and stores data in a single file (`database/finance.db`). It provides ACID compliance and is ideal for desktop and standalone university demonstrations without requiring a running database daemon.

#### Q3: How do you prevent User A from seeing User B's financial data?
**Answer:** Every database operation in `FinanceService` strictly filters by `user_id == current_user.id`. In our automated tests (`test_finance.py:test_strict_tenant_isolation`), we verify that User 1 attempting to view or delete User 2's transactions raises a `LookupError` and is denied.

#### Q4: How is password security implemented?
**Answer:** We use Werkzeug's `generate_password_hash()` which implements **PBKDF2-SHA256**. It automatically salts every password with random cryptographic bits and performs thousands of hash iterations to prevent rainbow table attacks.

#### Q5: What happens if the Gemini AI API goes offline or the user has no API key?
**Answer:** The application implements a **Heuristic Fallback Engine** in `GeminiService`. If the API key is missing or the external API call fails, the system automatically uses keyword-based NLP classification and rule-based financial advice generation with zero application crashes.

#### Q6: How does the AI know how much money the user has spent?
**Answer:** We use **Context Grounding**. Before querying the AI, `_build_user_financial_context()` aggregates numerical summaries (Total Income, Total Expenses, Category Breakdown) from SQLite and feeds them into the system prompt.

#### Q7: How does the application calculate the Savings Rate?
**Answer:** Using the formula:
$$\text{Savings Rate \%} = \frac{\text{Total Income} - \text{Total Expenses}}{\text{Total Income}} \times 100$$
If $\text{Total Income} \le 0$, the function safely returns $0.0\%$ to prevent `ZeroDivisionError`.

#### Q8: How is the Daily Spending Velocity calculated?
**Answer:** We compute:
$$\text{Average Daily Spend} = \frac{\text{Monthly Expenses}}{\text{Days Elapsed}}$$
We then multiply this by `calendar.monthrange(year, month)[1]` to project month-end spend before the month concludes.

#### Q9: What are the three Budget Threshold States?
**Answer:**
1. **Safe** ($< 75\%$ used): Normal spending.
2. **Warning** ($75\% - 99.9\%$ used): Approaching category ceiling.
3. **Danger / Overrun** ($\ge 100\%$ used): Exceeded budget; displays overrun excess amount in red.

#### Q10: How do you prevent duplicate category budgets in the same month?
**Answer:** We enforce a composite unique constraint at the database schema level in `models/budget.py`:
`db.UniqueConstraint('user_id', 'category', 'month', 'year')`. In `BudgetService`, setting a budget for an existing category updates the record in place.

#### Q11: What is Session Fixation and how did you prevent it?
**Answer:** Session Fixation occurs when an attacker tricks a user into authenticating with a known session ID. We prevent this by calling `session.clear()` inside `login()` right before assigning `session['user_id'] = user.id`.

#### Q12: Why did you use Vanilla CSS instead of Tailwind or Bootstrap?
**Answer:** Vanilla CSS allows full control over custom design properties, responsive layouts, glassmorphism blur effects, and animations without requiring npm dependencies, external build tools, or heavy CSS bundles.

#### Q13: How does the real-time AI auto-suggest chip work in the expense modal?
**Answer:** The description `<input>` has a 300ms JavaScript debounce timer. When the user stops typing, it triggers a background POST fetch to `/api/ai/categorize`. The returned category appears as a clickable chip that populates the category select element.

#### Q14: How does the CSV Export feature function?
**Answer:** In `ReportService.export_transactions_csv()`, all incomes and expenses are combined into an in-memory `io.StringIO` buffer using Python's standard `csv.DictWriter`, and returned as a `text/csv` attachment.

#### Q15: What is the 50/30/20 Budgeting Rule suggested by the advisor?
**Answer:** It is a standard financial planning principle where 50% of income is allocated to **Needs** (rent, utilities, groceries), 30% to **Wants** (dining out, entertainment), and 20% to **Savings** or debt reduction.

---

## 🔮 Future Improvements

1. **Bank Account & SMS Integration**: Automatic transaction logging via Account Aggregator APIs or SMS parsing.
2. **Goal-Based Savings Tracker**: Dedicated buckets for long-term targets (e.g. *"Emergency Fund: ₹1,00,000"*, *"Laptop: ₹75,000"*).
3. **Multi-Currency Live Conversion**: Real-time foreign exchange rate conversion using currency API feeds.
4. **Recurring Subscriptions Manager**: Automated detection of monthly recurring subscriptions with renewal warnings.
5. **Mobile PWA Support**: Progressive Web App manifest for offline installation on Android and iOS devices.

---

## 👨‍💻 Developer & Academic Context
- **Project:** Personal Finance Advisor Bot
- **Degree:** B.Sc. Computer Science / Cybersecurity Capstone
- **Tested On:** Windows 11, Python 3.11, Chrome / Edge
