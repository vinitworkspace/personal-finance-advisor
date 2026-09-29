# 08. Viva Examination Preparation Guide & Model Answers

## Overview
This document prepares Computer Science, Information Technology, and Cybersecurity students for technical viva voce examinations, project defense panels, and technical interviews based on the **Personal Finance Advisor Bot** codebase.

---

## Category 1: Software Architecture & Design Patterns

### Q1: Why did you choose a multi-tier architecture instead of writing all logic inside Flask route handlers?
**Model Answer:**
> *"Placing business logic, database queries, and data validation directly inside route handlers results in 'Fat Controllers' or spaghetti code that is difficult to test, maintain, and refactor. 
> In this project, we implemented a 4-tier architecture:
> 1. **Presentation Layer (Jinja2 Templates & Vanilla JS)**: Responsible solely for rendering and user interaction.
> 2. **Controller Layer (Flask Blueprints)**: Parses incoming HTTP requests, performs high-level validation, and invokes services.
> 3. **Service Layer (FinanceService, BudgetService, GeminiService)**: Encapsulates pure business logic and financial mathematics independent of HTTP or database details.
> 4. **Persistence Layer (SQLAlchemy ORM)**: Manages database transactions, schemas, and referential integrity.
> This separation allows us to unit test calculations in `tests/test_analytics.py` and `tests/test_finance.py` without needing to mock HTTP requests or browser sessions."*

---

### Q2: What is the purpose of Flask Blueprints, and how do they benefit this project?
**Model Answer:**
> *"Flask Blueprints allow large web applications to be decomposed into modular, domain-specific components. Rather than having a 2,000-line monolithic `app.py`, we created dedicated blueprints for `auth`, `dashboard`, `income`, `expenses`, `budget`, `analytics`, `ai`, and `reports`. Each blueprint manages its own routes, URL prefixes, and error handling, making the application modular, extensible, and clean."*

---

### Q3: Explain how the Decorator Pattern is utilized in your application.
**Model Answer:**
> *"We utilized the Decorator Pattern to implement the `@login_required` middleware in `routes/auth.py`. Using Python's `functools.wraps`, the decorator intercepts incoming requests to protected routes (like `/dashboard` or `/expenses/add`), verifies whether `'user_id'` exists in the active Flask session, and redirects unauthenticated users to `/auth/login` while preserving their intended destination in the `next` query parameter. This guarantees declarative, centralized access control without repeating authorization checks in every view."*

---

## Category 2: Cybersecurity & Authentication

### Q4: How are passwords stored, and why didn't you use plain MD5 or SHA-256?
**Model Answer:**
> *"We use **PBKDF2 (Password-Based Key Derivation Function 2)** with HMAC-SHA256, implemented via Werkzeug. Plain SHA-256 or MD5 are designed to be fast algorithms for data integrity, which makes them disastrous for passwords because modern GPUs can compute billions of SHA-256 hashes per second to crack passwords via brute force or Rainbow Tables. 
> PBKDF2 solves this by:
> 1. Generating a unique 16-byte cryptographically secure random salt for every user, neutralizing rainbow table attacks.
> 2. Applying 150,000+ key-stretching iterations, deliberately slowing down hash computation for an attacker while remaining imperceptible to a legitimate user."*

---

### Q5: What is a Timing Attack, and how does your code defend against it?
**Model Answer:**
> *"A timing attack occurs when an attacker measures the precise execution time of a password verification check. Standard string comparison (`if stored == input:`) stops executing at the first character that differs, allowing an attacker to deduce the correct password character-by-character based on millisecond differences. 
> We defend against this by using Werkzeug's `check_password_hash()`, which internally calls Python's `hmac.compare_digest()`. This function executes in **constant time**, regardless of how many leading characters match, eliminating timing side-channels."*

---

### Q6: What is Session Fixation, and how did you mitigate it?
**Model Answer:**
> *"In a Session Fixation attack, an attacker tricks a victim into using a known session identifier (e.g., by sending a pre-seeded cookie link). If the server maintains that same session ID after the victim logs in, the attacker can hijack the authenticated session. 
> We mitigate this in `routes/auth.py` by calling `session.clear()` immediately upon successful credential validation before assigning `session['user_id']`. This destroys any pre-existing unauthenticated session state and issues a fresh session."*

---

### Q7: What is an IDOR vulnerability, and how does your architecture prevent it?
**Model Answer:**
> *"IDOR stands for **Insecure Direct Object Reference**. It occurs when a web application accepts a database record identifier (like `/expenses/delete/14`) from a client and performs the action without verifying that the record belongs to the requesting user. 
> In our application, every database operation in `FinanceService` and `BudgetService` strictly combines the record ID with the authenticated session's `user_id`:
> ```python
> Expense.query.filter_by(id=expense_id, user_id=user_id).first()
> ```
> If user A attempts to manipulate record ID 14 belonging to user B, the query returns `None`, completely preventing unauthorized cross-tenant data access."*

---

### Q8: How does your application protect against Cross-Site Scripting (XSS)?
**Model Answer:**
> *"We employ a two-fold defense:
> 1. **Server-Side**: Jinja2 automatically escapes all dynamic template variables (`{{ var }}`), converting `<script>` into safe HTML entities (`&lt;script&gt;`).
> 2. **Client-Side (AI Chat)**: In `static/js/advisor.js`, before formatting AI markdown responses, all text is passed through an HTML entity sanitizer using a detached DOM node (`div.textContent = text; return div.innerHTML`), ensuring external text cannot inject rogue script tags or attributes."*

---

## Category 3: Database & Data Modeling

### Q9: Why SQLite instead of MySQL or PostgreSQL for this project?
**Model Answer:**
> *"SQLite was chosen because it provides a zero-configuration, serverless, self-contained ACID-compliant database stored as a single file (`database/finance.db`). It eliminates the operational overhead of installing and running external database server daemons during project evaluation, portability testing, and student viva presentations. 
> Furthermore, because we abstract all database access through the SQLAlchemy 2.0 ORM, switching to PostgreSQL or MySQL in production requires changing only the `DATABASE_URL` connection string without modifying our application models or service queries."*

---

### Q10: What are cascading deletes, and why are they necessary in your models?
**Model Answer:**
> *"In `models/user.py`, our relationships with `Income`, `Expense`, `Budget`, and `FinancialReport` are configured with `cascade='all, delete-orphan'`. If a user account is deleted, the database automatically cascades the deletion to remove all associated transactions, budgets, and historical reports. This preserves database referential integrity, avoids orphaned records, and ensures compliance with privacy regulations like GDPR's 'Right to be Forgotten'."*

---

### Q11: What was the Windows SQLite path issue, and how did you resolve it?
**Model Answer:**
> *"In Flask-SQLAlchemy 3.0+, relative SQLite connection strings (like `sqlite:///database/finance.db`) resolve relative to `app.instance_path`. On Windows, if the instance folder structure differs or relative backslashes are mishandled, SQLite throws `unable to open database file`. 
> In `config.py`, we solved this by using Python's `pathlib.Path(__file__).resolve().parent`, guaranteeing that the target database directory is created programmatically and formatted into an absolute POSIX URI (`sqlite:///d:/.../database/finance.db`), ensuring 100% cross-platform reliability across Windows, macOS, and Linux."*

---

## Category 4: Artificial Intelligence & Advisory Engine

### Q12: How do you prevent AI hallucinations when using Google Gemini?
**Model Answer:**
> *"Large language models hallucinate when asked to provide financial advice in a vacuum without real data. We eliminate this through **Context Grounding (Retrieval-Augmented Generation / RAG concept)**:
> Before sending the user's prompt to Gemini 1.5 Flash in `GeminiService`, we query the database for the user's current month income, total expenses, savings rate, top spending categories, and any budget overruns. We inject this factual data into a system prompt directive instructing the model to ground its advice exclusively in the user's actual numbers."*

---

### Q13: What happens if the Gemini API key expires, quota runs out, or there is no internet connection?
**Model Answer:**
> *"The application is designed with **Graceful Degradation**. In `services/gemini_service.py`, if the API key is missing, network is unavailable, or a 429 quota exception occurs, the system automatically falls back to an internal **Deterministic Heuristic Rules Engine**. 
> The rules engine classifies user intent (savings, budget overrun, investment, debt), executes deterministic financial formulas (such as the 50/30/20 rule and spending velocity), and returns tailored advice with an academic disclosure tag. The user experience remains uninterrupted."*

---

### Q14: How does the real-time expense auto-categorization feature work?
**Model Answer:**
> *"When a user types an expense description in the modal, a debounced JavaScript event sends the string to `/api/ai/categorize`. 
> The backend executes a two-tier evaluation:
> 1. **Tier 1 (Instant Heuristic Keyword Matcher)**: Matches high-frequency patterns (e.g., 'uber' -> Transportation, 'starbucks' -> Food & Dining) in under 2 milliseconds.
> 2. **Tier 2 (Gemini Zero-Shot Classifier)**: For novel or ambiguous phrases, it queries Gemini 1.5 Flash with a constrained prompt to select from our predefined category list. The frontend then dynamically displays an auto-suggest badge that the user can click to apply instantly."*

---

## Category 5: Financial Mathematics & Analytics

### Q15: How is the Daily Spending Velocity calculated, and what does it tell the user?
**Model Answer:**
> *"Daily Spending Velocity is the burn rate of cash per elapsed day in the active calendar month:
> $$\text{Daily Velocity} = \frac{\text{Total Expenses to Date}}{\max(1, \text{Elapsed Days})}$$
> Multiplying this velocity by the total days in the month gives the **Month-End Projected Expense**. This provides early warning: if on day 10 a user has already spent ₹20,000 (₹2,000/day), the system projects ₹62,000 by month-end, alerting the user to curtail spending before incurring a deficit."*

---

### Q16: How do you handle edge cases in the Savings Rate calculation?
**Model Answer:**
> *"The savings rate formula is:
> $$\text{Savings Rate} = \frac{\text{Income} - \text{Expenses}}{\text{Income}} \times 100$$
> Two critical edge cases exist:
> 1. **Zero Income (`Income == 0`)**: Normal division would raise a `ZeroDivisionError`. The function checks for this and returns `0.0%`.
> 2. **Deficit Spending (`Expenses > Income`)**: Subtracting expenses from income produces a negative number. We clamp the savings rate to `0.0%` using `max(0, ...)` and report the deficit separately in net balance."*

---

## Category 6: Full-Stack Engineering & Frontend Design

### Q17: Why did you build the UI with Vanilla CSS and Vanilla JS instead of React or Tailwind?
**Model Answer:**
> *"Choosing Vanilla CSS and Vanilla JavaScript offers several key engineering benefits:
> 1. **Zero Build Step Dependency**: Eliminates Node.js, Webpack, Vite, or npm compilation pipelines, making the application instantly runnable on any machine with just Python installed.
> 2. **Performance & Lightweight Footprint**: Zero framework bloat results in sub-50ms page loads and instantaneous browser rendering.
> 3. **Design Flexibility**: By defining CSS custom properties (variables) in `:root`, we implemented a modern dark-mode glassmorphism design system with responsive flex/grid layouts and micro-interactions entirely from scratch."*

---

### Q18: How is the print-ready PDF financial report generated?
**Model Answer:**
> *"Instead of relying on heavy server-side PDF rendering binaries like `wkhtmltopdf` or `weasyprint` (which require external C-libraries often troublesome on Windows), we implemented CSS `@media print` stylesheets inside `templates/reports.html`. When the user clicks 'Print / Save as PDF' or triggers `window.print()`, the print stylesheet automatically hides the navigation bar, sidebar, and buttons, formats table pagination, and produces a clean, high-resolution PDF document directly using the browser's native PDF engine."*
