# 05. Financial Mathematics & Algorithms

## Overview
All financial insights in the **Personal Finance Advisor Bot** are driven by mathematical algorithms implemented inside `services/finance_service.py`, `services/budget_service.py`, and `services/analytics_service.py`. This document explains every formula, edge case, and algorithmic calculation used in the application.

---

## 1. Net Balance (Cash Flow)

### Formula
$$\text{Net Balance} = \sum_{i=1}^{n} \text{Income}_i - \sum_{j=1}^{m} \text{Expense}_j$$

### Implementation (`services/finance_service.py`)
```python
total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0))\
    .filter(Income.user_id == user_id).scalar()

total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))\
    .filter(Expense.user_id == user_id).scalar()

net_balance = round(float(total_income) - float(total_expenses), 2)
```

- **Interpretation**:
  - `> 0`: Cash surplus (positive cashflow).
  - `< 0`: Cash deficit (expenses exceed income).
  - `= 0`: Break-even.

---

## 2. Savings Rate Percentage

The savings rate indicates the proportion of incoming cash retained as savings.

### Formula
$$\text{Savings Rate (\%)} = \begin{cases} 
\max\left(0, \frac{\text{Total Income} - \text{Total Expenses}}{\text{Total Income}} \times 100\right), & \text{if Total Income} > 0 \\
0.0, & \text{if Total Income} \le 0 
\end{cases}$$

### Edge Case Handling
1. **Zero Income (`Income == 0`)**: Division by zero is avoided; savings rate defaults to `0.0%`.
2. **Deficit Spending (`Expenses > Income`)**: Savings rate is clamped to `0.0%` (negative savings are reported as a cashflow deficit).

---

## 3. Budget Utilization Percentage & Status Tiers

### Formula
$$\text{Utilization (\%)} = \left(\frac{\text{Spent Amount}}{\text{Monthly Limit}}\right) \times 100$$

### Status Tiers (`services/budget_service.py`)
| Utilization Range | Status Key | CSS Badge | Interpretation |
| :--- | :--- | :--- | :--- |
| **0.0% – 79.9%** | `safe` | Green (`var(--success)`) | Spending is well within limits. |
| **80.0% – 99.9%** | `warning` | Amber (`var(--warning)`) | Spending approaches limit (≥80%). |
| **$\ge$ 100.0%** | `danger` | Red (`var(--danger)`) | **Budget Exceeded** (Overrun). |

### Overrun Excess Formula
$$\text{Overrun Amount} = \max(0, \text{Spent Amount} - \text{Monthly Limit})$$

---

## 4. Daily Spending Velocity (Burn Rate)

Spending velocity measures the average outflow of funds per elapsed day in the current calendar month.

### Formula
$$\text{Daily Velocity} = \frac{\text{Total Expenses to Date}}{D_{\text{elapsed}}}$$

Where:
- $D_{\text{elapsed}} = \max(1, \text{current day of month})$.

### Example
If on March 15, total spending is ₹30,000:
$$\text{Daily Velocity} = \frac{30,000}{15} = ₹2,000/\text{day}$$

---

## 5. Month-End Spending Projection

Projects total anticipated expenses by the final day of the current calendar month based on current velocity.

### Formula
$$\text{Projected Expense} = \text{Daily Velocity} \times D_{\text{total}}$$

Where:
- $D_{\text{total}} = \text{Total calendar days in the month}$ (e.g., 28, 29, 30, or 31, computed via `calendar.monthrange(year, month)[1]`).

### Example
If daily velocity is ₹2,000/day in a 31-day month:
$$\text{Projected Expense} = 2,000 \times 31 = ₹62,000$$

This allows the user to see immediately if they are projected to run a deficit before the month ends.

---

## 6. Categorical Pareto Distribution

Calculates the percentage of total monthly outflow attributed to each category.

### Formula
$$P_c = \left(\frac{\sum \text{Expense}_c}{\text{Total Expenses}}\right) \times 100$$

Used to populate the **Chart.js Category Doughnut Chart** and detect disproportionate spending leaks.

---

## 7. The 50/30/20 Budgeting Benchmark

A classical personal finance framework popularized by Senator Elizabeth Warren:

$$\begin{aligned}
\text{Needs (50\%)} &= \text{Income} \times 0.50 \quad \text{(Housing, Utilities, Groceries, Healthcare)} \\
\text{Wants (30\%)} &= \text{Income} \times 0.30 \quad \text{(Dining Out, Entertainment, Subscriptions, Shopping)} \\
\text{Savings (20\%)} &= \text{Income} \times 0.20 \quad \text{(Emergency Fund, Investments, Debt Payoff)}
\end{aligned}$$

The AI engine compares the user's actual categorical allocations against this benchmark to highlight overspending.

---

## 8. Emergency Fund Adequacy Ratio

Calculates how many months of baseline expenses the user's current net liquid balance can support:

$$\text{Emergency Runway (Months)} = \frac{\text{Net Balance}}{\text{Average Monthly Expenses (Last 3 Months)}}$$

- **Target**: 3 to 6 months of living expenses.
