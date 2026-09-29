# 06. Complete REST API Reference

## Overview
The **Personal Finance Advisor Bot** exposes server-rendered HTML endpoints alongside JSON REST endpoints for charts, AI chat, and dynamic categorization. All JSON endpoints return standard HTTP status codes and uniform JSON envelopes.

---

## 1. Authentication Endpoints (`/auth`)

### 1.1 Register Account
- **Endpoint**: `POST /auth/register`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request Parameters**:
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `username` | string | Yes | Unique handle (3-80 chars) |
  | `email` | string | Yes | Valid email address |
  | `password` | string | Yes | Min 8 chars, 1 uppercase, 1 digit, 1 symbol |
  | `confirm_password` | string | Yes | Must match `password` |
  | `currency` | string | No | Default: `'INR'` |
- **Response**: `302 Redirect to /auth/login` on success, or `200 OK` with flash error.

### 1.2 Sign In
- **Endpoint**: `POST /auth/login`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request Parameters**:
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `username` | string | Yes | Registered username or email |
  | `password` | string | Yes | User password |
- **Response**: `302 Redirect to /dashboard` with signed `session` cookie.

### 1.3 Sign Out
- **Endpoint**: `GET /auth/logout`
- **Response**: `302 Redirect to /auth/login` (clears session store).

---

## 2. Financial Ledger Endpoints

### 2.1 Income Ledger
- `GET /income/`: View income listing with optional search & date filters.
- `POST /income/add`:
  - **Body**: `amount` (float), `source` (string), `category` (string), `date` (YYYY-MM-DD), `description` (optional).
  - **Response**: `302 Redirect to /income/`.
- `POST /income/edit/<id>`: Updates existing record.
- `POST /income/delete/<id>`: Deletes record (enforcing tenant isolation).

### 2.2 Expense Ledger
- `GET /expenses/`: View expense listing with category filters.
- `POST /expenses/add`:
  - **Body**: `amount` (float), `category` (string), `date` (YYYY-MM-DD), `description` (optional).
  - **Response**: `302 Redirect to /expenses/`.
- `POST /expenses/edit/<id>`: Updates existing expense.
- `POST /expenses/delete/<id>`: Deletes expense record.

### 2.3 Budget Management
- `GET /budget/`: View budget ceiling meters and monthly spending progress.
- `POST /budget/set`:
  - **Body**: `category` (string), `monthly_limit` (float), `month` (1-12), `year` (int).
  - **Response**: `302 Redirect to /budget/`.
- `POST /budget/delete/<id>`: Deletes category budget.

---

## 3. Analytics & Visualization JSON API

### 3.1 Fetch Chart Data
- **Endpoint**: `GET /api/analytics/charts`
- **Query Parameters**:
  - `period`: `3m`, `6m` (default), or `12m`.
- **Response**: `200 OK` (JSON)
```json
{
  "status": "success",
  "data": {
    "trend": {
      "labels": ["Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026"],
      "income": [65000, 68000, 72000, 65000, 65000, 80000],
      "expenses": [38000, 41000, 49000, 37000, 36000, 38400],
      "savings": [27000, 27000, 23000, 28000, 29000, 41600]
    },
    "distribution": {
      "labels": ["Rent & Housing", "Food & Dining", "Utilities", "Transportation", "Entertainment"],
      "values": [18000, 9800, 4500, 3200, 2900]
    }
  }
}
```

---

## 4. AI & Intelligent Advisory API

### 4.1 Conversational Advisor Chat
- **Endpoint**: `POST /api/ai/chat`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "message": "How much did I spend on food this month and can I afford eating out tonight?"
}
```
- **Response**: `200 OK` (JSON)
```json
{
  "status": "success",
  "reply": "Based on your records for March 2026, you have spent **₹9,800.00** on Food & Dining against your budget limit of **₹9,000.00**. You are currently **₹800.00 over budget** in this category. I recommend cooking at home this weekend to bring your cashflow back into equilibrium.",
  "source": "Gemini 1.5 Flash (Context Grounded)",
  "timestamp": "2026-03-29T19:30:00Z"
}
```

### 4.2 Real-Time Expense Auto-Categorization
- **Endpoint**: `POST /api/ai/categorize`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "description": "Starbucks cold brew with oat milk"
}
```
- **Response**: `200 OK` (JSON)
```json
{
  "status": "success",
  "category": "Food & Dining",
  "confidence": 0.95
}
```

---

## 5. Reports & Data Portability

### 5.1 Export Ledger to CSV
- **Endpoint**: `GET /reports/export/csv`
- **Response**: `200 OK` with headers:
  - `Content-Type: text/csv; charset=utf-8`
  - `Content-Disposition: attachment; filename="personal_finance_ledger_20260329.csv"`
- Generates RFC-4180 compliant CSV export of all income and expense items.

### 5.2 Monthly Statement View & PDF Print
- **Endpoint**: `GET /reports/`
- Serves print-ready HTML monthly financial statement with embedded CSS `@media print` rules, generating clean PDF statements when the user presses **Print / Save as PDF** (`Ctrl + P`).
