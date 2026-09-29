# 07. How to Run & Complete Browser Guide

## Overview
This step-by-step guide explains how to install, initialize, and launch the **Personal Finance Advisor Bot** on Windows and open it in your browser.

---

## 1. Prerequisites
- **Python**: Version 3.9 or higher (Python 3.11 recommended).
- **Web Browser**: Google Chrome, Microsoft Edge, Mozilla Firefox, or Brave.
- **Operating System**: Windows 10/11 (macOS and Linux also supported).
- *(Optional)*: A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/). The application runs fully offline even without this key!

---

## 2. One-Time Setup & Installation

Open **PowerShell** or **Command Prompt** and navigate to the project directory:

```powershell
cd "d:\VINIT PERSONAL\VINZIE PROJECTS\personal-finance-advisor"
```

### Step 2.1: (Recommended) Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again).*

### Step 2.2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables
Copy `.env.example` to create your active `.env` file:
```powershell
copy .env.example .env
```
Inside `.env`, you can optionally paste your `GEMINI_API_KEY`:
```ini
FLASK_ENV=development
SECRET_KEY=change-this-to-a-super-secret-key-in-production
DATABASE_PATH=database/finance.db
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=5000
```
> **Note**: If you leave `GEMINI_API_KEY` blank or commented out, the app automatically switches to the built-in **Deterministic Financial Rules Engine** without crashing or throwing errors.

### Step 2.4: Initialize the Database & Seed Demo Data
```powershell
python init_db.py
```
This creates the SQLite database at `database/finance.db` and populates 6 months of realistic transactions for the demo user:
- **Username**: `demo_user`
- **Password**: `DemoPass@123`

---

## 3. Starting the App in Your Browser

You have three convenient ways to launch the application:

### Method A: One-Click Batch Launcher (Double-Click or Command)
Double-click `run_app.bat` in the project root, or execute:
```cmd
.\run_app.bat
```
*This launches the Flask server and automatically opens your default browser at `http://127.0.0.1:5000`.*

### Method B: PowerShell Launcher
```powershell
.\run_app.ps1
```

### Method C: Standard Python Command
```powershell
python app.py
```
Then open your favorite browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 4. Complete Browser Tour & Feature Walkthrough

### 4.1 Authentication & Quick-Fill Demo
1. Navigate to `http://127.0.0.1:5000`.
2. If you are not signed in, you will be redirected to `/auth/login`.
3. Click the **"Fill Demo Credentials"** button to automatically populate `demo_user` and `DemoPass@123`.
4. Click **Sign In**.

```text
+-------------------------------------------------------+
|  [F] FinBot | Personal Finance Advisor                |
|  Welcome back! Sign in to access your financial hub.  |
|                                                       |
|  Username: [ demo_user              ]                 |
|  Password: [ *************          ]                 |
|                                                       |
|  [ Sign In ]   [⚡ Quick Demo Fill ]                  |
+-------------------------------------------------------+
```

---

### 4.2 The Dashboard (`/dashboard`)
Upon login, you arrive at the central financial command center:
- **Hero KPI Cards**:
  - **Total Income**: Aggregated inflows for the active month (e.g., ₹65,000.00).
  - **Total Expenses**: Aggregated outflows to date (e.g., ₹38,400.00).
  - **Net Savings**: Cashflow surplus (e.g., ₹26,600.00).
  - **Savings Rate**: Target benchmark gauge (e.g., 40.9%).
- **Interactive Charts**:
  - **Cash Flow History (Bar/Line)**: Shows 6-month historical trajectory of income vs. expenses vs. net savings.
  - **Spending Distribution (Doughnut)**: Visual breakdown of expense categories.
- **Budget Guardrails**: Live visual progress meters showing category limits, current spend, and warning badges.
- **Recent Transactions Feed**: Fast ledger preview with quick action buttons.

---

### 4.3 Income Ledger (`/income/`)
- View all income streams sorted chronologically.
- Filter by keyword or date range.
- Click **"Add Income"** to log new paychecks, freelance earnings, or investment returns.
- Inline edit and delete buttons with instant confirmation modals.

---

### 4.4 Expense Tracking & AI Auto-Categorization (`/expenses/`)
- Click **"Add Expense"**.
- As you type in the description field (e.g., *"Starbucks mocha"* or *"Uber cab to office"*), watch the **AI Suggested Category** chip update in real-time.
- Click the chip to instantly assign the recommended category!
- View categorized expenses with formatted currency badges.

---

### 4.5 Budget Ceilings (`/budget/`)
- Set monthly financial guardrails for categories (e.g., ₹9,000 for Food & Dining, ₹5,000 for Utilities).
- View color-coded utilization meters:
  - **Green (Safe)**: Under 80% of limit.
  - **Amber (Warning)**: Between 80% and 99% of limit.
  - **Red (Danger / Overrun)**: Exceeded 100% of limit, displaying exact overrun amount.

---

### 4.6 Analytics & Burn Rate (`/analytics/`)
- **Daily Spending Velocity**: Measures average outflow per elapsed day in the month.
- **Month-End Projection**: Projects total anticipated month-end spend if current burn rate continues.
- **50/30/20 Rule Analysis**: Compares actual spend against recommended Needs (50%), Wants (30%), and Savings (20%).
- **Historical Comparison**: Toggle between 3-month, 6-month, and 12-month trend charts.

---

### 4.7 FinBot AI Financial Advisor (`/advisor/`)
- Real-time interactive financial chat interface.
- Click **Quick Prompt Chips** to ask:
  - *"How can I improve my savings rate?"*
  - *"Analyze my budget overruns for this month."*
  - *"Explain the 50/30/20 rule based on my income."*
- Responses are formatted with rich markdown (bullet points, bold text, headings).
- Source tag shows whether the insight was generated by **Gemini 1.5 Flash** or the **Deterministic Heuristic Rules Engine**.

---

### 4.8 Reports & Statements (`/reports/`)
- **Print / Save as PDF**: Press the printer button or `Ctrl + P` to produce an executive-ready PDF financial report. CSS `@media print` rules automatically hide navigation bars and action buttons.
- **Export to CSV**: Click **"Export CSV"** to download an RFC-4180 compliant `.csv` file compatible with Microsoft Excel, Google Sheets, or Apple Numbers.

---

### 4.9 Settings (`/settings/`)
- Configure preferred display currency (INR ₹, USD $, EUR €, GBP £).
- Update user password with secure validation.

---

## 5. Troubleshooting & Frequently Asked Questions

### Q: Port 5000 is already in use by another application.
**Fix**: Edit `PORT` in your `.env` file to another port (e.g., `PORT=5050`) or run:
```powershell
python -c "from app import app; app.run(port=5050, debug=True)"
```

### Q: I see `sqlite3.OperationalError: unable to open database file`.
**Fix**: In this project, `config.py` converts relative paths to absolute POSIX paths automatically. Make sure the `database/` directory exists and you have write permissions. Run `python init_db.py` to create the database file cleanly.

### Q: Does the app work without internet access?
**Yes!** If you are presenting your viva in a room without Wi-Fi, the entire application functions flawlessly using the built-in offline heuristic rules engine and local SQLite database.
