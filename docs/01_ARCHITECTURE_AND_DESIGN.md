# 01. System Architecture & Design Patterns

## Overview
The **Personal Finance Advisor Bot** is engineered following enterprise-grade software architecture principles adapted for modern Python web applications. Rather than placing all logic inside route handlers or a monolithic script, the system utilizes a **multi-tier separation of concerns**:

```text
[ Browser / Client ] 
        ↕ (HTTP / JSON)
[ Presentation Layer ] (Jinja2 Templates + Vanilla CSS + Vanilla JS + Chart.js)
        ↕
[ Controller Layer ] (Flask Blueprints: auth, dashboard, income, expenses, budget, analytics, ai, reports)
        ↕
[ Security Layer ] (@login_required + PBKDF2 Password Hashing + Tenant Isolation)
        ↕
[ Service Layer ] (FinanceService, BudgetService, AnalyticsService, GeminiService, ReportService)
        ↕
[ Persistence Layer ] (SQLAlchemy ORM Models + SQLite Database: database/finance.db)
        ↕
[ External AI Layer ] (Google Gemini 1.5 Flash API + Offline Heuristic Fallback Engine)
```

---

## 1. Multi-Tier Separation of Concerns

### Tier 1: Presentation Layer
- **Templates (`templates/`)**: Server-rendered HTML5 templates powered by Jinja2. Inherits from `base.html` for uniform navigation, styling, flash alerts, and disclaimer notices.
- **Design System (`static/css/style.css`)**: Built with pure **Vanilla CSS3**. Implements CSS custom properties (`:root` design tokens), dark mode, glassmorphism surface blurs, responsive grids, and micro-interactions without relying on heavy frontend frameworks like Tailwind or Bootstrap.
- **Client Scripting (`static/js/`)**: Modular Vanilla JavaScript for interactive controls:
  - `main.js`: Global toast notification engine, modal toggles, mobile drawer navigation, demo credentials quick-fill.
  - `dashboard.js`: Chart.js visualization engine for cashflow trends and categorical doughnut distribution.
  - `advisor.js`: Chat stream manager, debounced input triggers, and safe markdown formatting.

### Tier 2: Controller / Routing Layer (`routes/`)
Each functional domain is encapsulated within a separate **Flask Blueprint**:
- `routes/auth.py`: Registration, authentication session management, logout, and `@login_required` decorator.
- `routes/dashboard.py`: Aggregates real-time KPIs, budget guardrail warnings, and recent transaction feeds.
- `routes/income.py`: Income ledger views, search filters, and CRUD endpoints.
- `routes/expenses.py`: Expense ledger views, category filters, and real-time AI auto-categorization.
- `routes/budget.py`: Category budget ceiling management, utilization meters, and overrun warnings.
- `routes/analytics.py`: Deep-dive analytics, daily burn rate, and `/api/analytics/charts` endpoint.
- `routes/ai.py`: Conversational advisor interface, Q&A chat, and advice generation endpoints.
- `routes/reports.py`: Monthly statement reports, snapshot compiling, and CSV ledger export.

### Tier 3: Service / Business Logic Layer (`services/`)
Controllers **never execute raw calculations or complex queries directly**. All math, business rules, and transformations reside in dedicated service classes:
- `FinanceService`: Net balance calculation, savings rate %, transaction CRUD with tenant isolation.
- `BudgetService`: Utilization percentages, threshold alerts (`safe`, `warning`, `danger`), overrun excess calculation.
- `AnalyticsService`: Daily spending velocity, calendar month-end projections, categorical Pareto share, 6-month historical trends, and heuristic pattern detection.
- `GeminiService`: Google Gemini 1.5 Flash client, prompt engineering, context grounding, and offline heuristic fallback engine.
- `ReportService`: Monthly snapshot compilation, database caching, and RFC-4180 CSV generation.

### Tier 4: Persistence Layer (`models/`)
- Uses **SQLAlchemy 2.0 ORM** mapped to an ACID-compliant **SQLite** database (`database/finance.db`).
- Models: `User`, `Income`, `Expense`, `Budget`, and `FinancialReport`.
- Enforces composite uniqueness constraints, indexing on date and user_id, and foreign key cascading deletions (`cascade='all, delete-orphan'`).

---

## 2. Key Design Patterns Implemented

### Pattern 1: Application Factory Pattern (`create_app()`)
In `app.py`, the Flask application is constructed inside a factory function:
```python
def create_app(config_name=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    # Register blueprints...
    return app
```
**Benefits:**
1. Eliminates circular imports between models, extensions, and route handlers.
2. Allows instantiating separate application instances with different configurations (e.g. `DevelopmentConfig` using SQLite vs `TestingConfig` using `:memory:` database).

### Pattern 2: Service Layer Pattern
Instead of writing database queries inside route handlers, routes call static methods on Services:
```python
# In routes/income.py
@income_bp.route('/income', methods=['POST'])
@login_required
def add_income():
    income = FinanceService.create_income(
        user_id=current_user.id,
        amount=request.form.get('amount'),
        source=request.form.get('source'),
        date_val=request.form.get('date')
    )
```
**Benefits:**
1. **Reusability**: The exact same method can be called by an HTML form route, a REST JSON API endpoint, or an automated unit test.
2. **Testability**: Services can be unit-tested in isolation without mocking HTTP request objects.

### Pattern 3: Template Context Injection Pattern
In `app.py`, a global context processor injects the currently authenticated user into every Jinja2 template:
```python
@app.context_processor
def inject_global_template_context():
    return {'current_user': get_current_user()}
```
**Benefits:**
Eliminates passing `user=current_user` manually in dozens of `render_template()` calls.

---

## 3. Request-Response Lifecycle Walkthrough

Here is the exact lifecycle of an HTTP request (e.g., logging an expense):
1. **Client Action**: User submits the Add Expense modal form in their browser.
2. **Network Transport**: Browser sends `POST /expenses` with form payload (`amount=1500`, `category=Food`, `date=2026-10-05`).
3. **Route Guard**: The `@login_required` decorator checks `session['user_id']`. If valid, loads `User` into `g.current_user`.
4. **Controller Handling**: `routes/expenses.py:add_expense()` parses form inputs.
5. **Service Validation & Execution**: `FinanceService.create_expense()` validates that amount is a positive float, parses date, and instantiates the `Expense` model with `user_id = g.current_user.id`.
6. **Database Persistence**: SQLAlchemy generates parameterized SQL `INSERT INTO expenses (...) VALUES (...)` and commits to `database/finance.db`.
7. **Session Flash & Redirect**: Controller flashes a success notification and issues an HTTP 302 redirect back to the expense ledger.
8. **Render & DOM Update**: Browser requests `GET /expenses`, Jinja renders the updated table with the new row, and JavaScript updates the UI.
