import os
import re
from typing import Dict, Any, List, Optional

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    try:
        import google.generativeai as genai
        GENAI_AVAILABLE = True
    except ImportError:
        GENAI_AVAILABLE = False

class GeminiService:
    """
    Dedicated AI Financial Service interfacing with Google Gemini 1.5 Flash.
    Includes a built-in Offline Heuristic Fallback Engine ensuring 100% resilience.
    """

    CATEGORIES = [
        'Food', 'Rent', 'Transport', 'Utilities', 'Entertainment',
        'Shopping', 'Healthcare', 'Education', 'EMI', 'Other'
    ]

    HEURISTIC_KEYWORDS = {
        'Food': [
            'dinner', 'lunch', 'breakfast', 'restaurant', 'cafe', 'coffee',
            'starbucks', 'dominos', 'pizza', 'burger', 'mcdonalds', 'swiggy',
            'zomato', 'grocery', 'supermarket', 'snack', 'food', 'meal', 'tea',
            'bistro', 'dining', 'barbeque', 'subway', 'kfc'
        ],
        'Rent': [
            'rent', 'landlord', 'flat', 'apartment', 'pg', 'hostel',
            'room rent', 'housing', 'lease', 'society maintenance'
        ],
        'Transport': [
            'uber', 'ola', 'rapido', 'metro', 'bus', 'train', 'flight',
            'ticket', 'petrol', 'diesel', 'fuel', 'auto', 'cab', 'taxi',
            'parking', 'toll', 'irctc', 'airline'
        ],
        'Utilities': [
            'electricity', 'water', 'internet', 'wifi', 'broadband',
            'gas', 'cylinder', 'mobile bill', 'recharge', 'dth', 'power bill',
            'piped gas', 'jio', 'airtel'
        ],
        'Entertainment': [
            'movie', 'cinema', 'netflix', 'spotify', 'hotstar', 'prime',
            'game', 'gaming', 'steam', 'concert', 'theatre', 'party',
            'club', 'outing', 'pvr', 'inox'
        ],
        'Shopping': [
            'amazon', 'flipkart', 'myntra', 'zara', 'clothes', 'shoes',
            'dress', 'shopping', 'mall', 'electronics', 'gadget', 'watch',
            'apple store', 'ajio', 'tshirt'
        ],
        'Healthcare': [
            'doctor', 'hospital', 'clinic', 'medicine', 'pharmacy',
            'chemist', 'dentist', 'medical', 'lab test', 'health',
            'apollo', '1mg', 'medplus'
        ],
        'Education': [
            'tuition', 'course', 'college', 'school', 'udemy', 'coursera',
            'books', 'exam', 'fees', 'library', 'stationery', 'tutorial',
            'coaching', 'cert'
        ],
        'EMI': [
            'emi', 'loan', 'credit card bill', 'mortgage', 'installment',
            'debt repayment', 'car loan', 'personal loan', 'home loan'
        ]
    }

    @staticmethod
    def _get_api_key() -> str:
        """Retrieve Gemini API key from environment."""
        return os.getenv('GEMINI_API_KEY', '').strip()

    # =========================================================================
    # 1. EXPENSE AUTO-CATEGORIZATION
    # =========================================================================

    @staticmethod
    def categorize_expense(description: str) -> Dict[str, Any]:
        """
        Classify expense description into a standard category using Gemini or Heuristic Fallback.
        """
        if not description or not description.strip():
            return {'category': 'Other', 'confidence': 0.5, 'source': 'default'}

        desc_clean = description.strip()
        api_key = GeminiService._get_api_key()

        # Try Gemini API if configured
        if api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = (
                    f"Categorize this expense description into exactly one of these categories: "
                    f"{', '.join(GeminiService.CATEGORIES)}.\n"
                    f"Expense description: \"{desc_clean}\"\n"
                    f"Output ONLY the category name, nothing else."
                )

                response = model.generate_content(prompt)
                suggested = response.text.strip().title()

                # Clean possible markdown or punctuation
                suggested = re.sub(r'[^a-zA-Z]', '', suggested)

                for cat in GeminiService.CATEGORIES:
                    if cat.lower() == suggested.lower():
                        return {'category': cat, 'confidence': 0.95, 'source': 'gemini'}

            except Exception:
                # Graceful fallback to heuristic engine
                pass

        # Heuristic Rule-Based Matching Engine
        desc_lower = desc_clean.lower()
        for cat, keywords in GeminiService.HEURISTIC_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or kw in desc_lower:
                    return {'category': cat, 'confidence': 0.88, 'source': 'heuristic'}

        return {'category': 'Other', 'confidence': 0.6, 'source': 'heuristic'}

    # =========================================================================
    # 2. FINANCIAL ADVICE & SUMMARY GENERATION
    # =========================================================================

    @staticmethod
    def generate_financial_advice(user_context: Dict[str, Any]) -> str:
        """
        Produce personalized financial analysis and budgeting recommendations.
        """
        api_key = GeminiService._get_api_key()

        # Try Gemini API if available
        if api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

                currency = user_context.get('currency', '₹')
                income = user_context.get('total_income', 0.0)
                expenses = user_context.get('total_expenses', 0.0)
                savings = user_context.get('net_balance', 0.0)
                savings_pct = user_context.get('savings_percentage', 0.0)
                categories = user_context.get('category_breakdown', {})
                burn_rate = user_context.get('average_daily_spend', 0.0)
                alerts = user_context.get('alerts', [])

                prompt = f"""
                You are a friendly, expert Senior Personal Finance Advisor mentoring a user on budgeting and personal wealth discipline.
                The financial data for the current month is:
                - Monthly Income: {currency}{income:,.2f}
                - Monthly Expenses: {currency}{expenses:,.2f}
                - Net Savings: {currency}{savings:,.2f}
                - Savings Percentage: {savings_pct}%
                - Average Daily Spending: {currency}{burn_rate:,.2f}/day
                - Category Spending Breakdown: {categories}
                - Active Budget Overruns/Warnings: {alerts}

                Please provide a concise, structured markdown report with:
                1. ### 📊 Monthly Spending Analysis (Assess their cash flow and savings health)
                2. ### 💡 Top 3 Actionable Cost-Cutting Opportunities (Focus on their highest spending categories)
                3. ### 🎯 Recommended Budget for Next Month (Suggested allocation using the 50/30/20 rule or tailored to their profile)
                4. ### 🛡️ Emergency Fund & Long-term Financial Health Tip

                IMPORTANT:
                - Keep advice practical, motivating, and easy to understand for a student, salaried professional, or freelancer.
                - Include a disclaimer: "General budgeting guidance only. Not licensed financial advice."
                - Format response cleanly in GitHub markdown with bold key figures and bullet points.
                """

                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()

            except Exception:
                pass

        # Robust Heuristic Financial Advisor Fallback
        return GeminiService._generate_heuristic_advice(user_context)

    @staticmethod
    def _generate_heuristic_advice(ctx: Dict[str, Any]) -> str:
        """Local rule-based financial advice generator producing personalized tips."""
        currency = ctx.get('currency', '₹')
        income = ctx.get('total_income', 0.0)
        expenses = ctx.get('total_expenses', 0.0)
        savings = ctx.get('net_balance', 0.0)
        savings_pct = ctx.get('savings_percentage', 0.0)
        categories = ctx.get('category_breakdown', {})
        burn = ctx.get('average_daily_spend', 0.0)

        # Identify top spending category
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_cats[0][0] if sorted_cats else "General Living"
        top_cat_amt = sorted_cats[0][1] if sorted_cats else 0.0

        discretionary = categories.get('Entertainment', 0.0) + categories.get('Shopping', 0.0)
        food_spend = categories.get('Food', 0.0)

        analysis = ""
        if income > 0 and expenses > income:
            analysis = f"⚠️ **Deficit Notice:** You are spending more than your income by **{currency}{expenses - income:,.2f}**. Prioritize covering essentials and curtail discretionary purchases immediately."
        elif savings_pct >= 20.0:
            analysis = f"🌟 **Excellent Financial Health:** You have achieved a **{savings_pct}%** savings rate (**{currency}{savings:,.2f}**), comfortably outperforming the standard 20% personal finance benchmark!"
        elif savings_pct > 0.0:
            analysis = f"👍 **Positive Cash Flow:** You saved **{currency}{savings:,.2f}** ({savings_pct}%). With small adjustments in discretionary expenses, you can steadily reach the 20% savings target."
        else:
            analysis = "ℹ️ **Break-Even Cash Flow:** All monthly inflows are currently consumed by outflows. Build a small monthly surplus to start your emergency fund."

        report = f"""### 📊 Monthly Spending Analysis
{analysis}
- **Total Inflow:** {currency}{income:,.2f}
- **Total Outflow:** {currency}{expenses:,.2f}
- **Daily Burn Rate:** {currency}{burn:,.2f}/day
- **Heaviest Category:** **{top_cat}** ({currency}{top_cat_amt:,.2f})

---

### 💡 Top 3 Actionable Cost-Cutting Opportunities
1. **Optimize {top_cat} Expenses:** As your largest single expense category ({currency}{top_cat_amt:,.2f}), a modest 10% reduction could save **{currency}{top_cat_amt * 0.1:,.2f}** next month.
"""
        if discretionary > 0:
            report += f"2. **Trim Discretionary Dining & Shopping:** Entertainment and Shopping accounted for **{currency}{discretionary:,.2f}**. Setting a weekend spending ceiling can save an estimated **{currency}{discretionary * 0.2:,.2f}**.\n"
        else:
            report += f"2. **Track Grocery vs Dining Out:** Preparing meals at home 2 additional days a week significantly reduces daily food burn.\n"

        if food_spend > 0:
            report += f"3. **Audit Subscription & Food Delivery Fees:** Recurring delivery app charges often add 15-20% hidden costs to food expenses.\n"
        else:
            report += f"3. **Review Utility Plans:** Check if your internet and mobile recharges match your actual bandwidth and call usage.\n"

        report += f"""
---

### 🎯 Recommended Budget for Next Month (50/30/20 Rule)
- **50% Needs (Rent, Utilities, Groceries):** {currency}{income * 0.50:,.2f}
- **30% Wants (Dining out, Entertainment, Shopping):** {currency}{income * 0.30:,.2f}
- **20% Savings & Debt Repayment:** {currency}{income * 0.20:,.2f}

---

### 🛡️ Emergency Fund & Long-term Financial Health Tip
Aim to accumulate **3 to 6 months of basic living expenses** ({currency}{expenses * 3:,.2f} – {currency}{expenses * 6:,.2f}) in a high-yield savings account or liquid deposit. This protects you against unexpected medical expenses, job changes, or freelance payment gaps.

> *Disclaimer: This guidance is provided for educational and budgeting purposes only. It does not constitute certified financial or investment advice.*
"""
        return report.strip()

    # =========================================================================
    # 3. INTERACTIVE CONVERSATIONAL ADVISOR
    # =========================================================================

    @staticmethod
    def chat_with_advisor(user_message: str, user_context: Dict[str, Any], chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Respond to user's natural language financial questions grounded in their real data.
        """
        if not user_message or not user_message.strip():
            return "How can I help you with your budget or personal finances today?"

        query = user_message.strip()
        api_key = GeminiService._get_api_key()

        # Try Gemini API if available
        if api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

                currency = user_context.get('currency', '₹')
                income = user_context.get('total_income', 0.0)
                expenses = user_context.get('total_expenses', 0.0)
                savings = user_context.get('net_balance', 0.0)
                savings_pct = user_context.get('savings_percentage', 0.0)
                categories = user_context.get('category_breakdown', {})
                burn_rate = user_context.get('average_daily_spend', 0.0)

                prompt = f"""
                You are FinanceAI, an intelligent and encouraging personal finance mentor.
                You are answering a user's question about their personal budget.
                
                Ground your answers strictly using their real financial data:
                - Currency: {currency}
                - Monthly Income: {currency}{income:,.2f}
                - Monthly Expenses: {currency}{expenses:,.2f}
                - Net Savings: {currency}{savings:,.2f} ({savings_pct}%)
                - Average Daily Spending: {currency}{burn_rate:,.2f}/day
                - Categories: {categories}

                User Question: "{query}"

                Guidelines:
                - Answer directly, referencing their specific numbers where applicable.
                - Keep responses concise (under 200 words), practical, and polite.
                - Use clear formatting with bullet points.
                - Educational and budgeting assistance only; no guaranteed returns or stock picks.
                """

                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()

            except Exception:
                pass

        # Intelligent Heuristic Chatbot Fallback
        return GeminiService._generate_heuristic_chat_reply(query, user_context)

    @staticmethod
    def _generate_heuristic_chat_reply(query: str, ctx: Dict[str, Any]) -> str:
        """Contextual heuristic responses tailored to common financial questions."""
        q = query.lower()
        currency = ctx.get('currency', '₹')
        income = ctx.get('total_income', 0.0)
        expenses = ctx.get('total_expenses', 0.0)
        savings = ctx.get('net_balance', 0.0)
        savings_pct = ctx.get('savings_percentage', 0.0)
        categories = ctx.get('category_breakdown', {})
        burn = ctx.get('average_daily_spend', 0.0)

        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_cats[0][0] if sorted_cats else "None"
        top_amt = sorted_cats[0][1] if sorted_cats else 0.0

        if any(w in q for w in ['spending the most', 'where am i spending', 'highest', 'top expense']):
            if top_amt > 0:
                pct = round((top_amt / expenses) * 100, 1) if expenses > 0 else 0
                return (
                    f"You are spending the most on **{top_cat}**, which accounts for "
                    f"**{currency}{top_amt:,.2f}** ({pct}% of your total outflows this month).\n\n"
                    f"💡 *Tip:* Setting a category budget for {top_cat} in the Budgets tab will help you set a firm ceiling."
                )
            return "You haven't logged any expenses yet this month. Start by recording an expense in the Expenses tab!"

        if any(w in q for w in ['save', 'reduce', 'cut', 'how can i save']):
            return (
                f"Based on your current numbers, here are 3 ways to boost your savings:\n\n"
                f"1. **Cap {top_cat}:** As your highest outflow ({currency}{top_amt:,.2f}), cutting just 10% saves **{currency}{top_amt * 0.1:,.2f}**.\n"
                f"2. **Monitor Daily Burn:** You are currently spending **{currency}{burn:,.2f}/day**. Trying a 'zero-spend day' twice a week can yield immediate savings.\n"
                f"3. **Follow the 50/30/20 Framework:** Allocate {currency}{income * 0.2:,.2f} (20%) directly into savings on income day before spending on wants."
            )

        if any(w in q for w in ['how much did i save', 'savings this month', 'balance', 'saved']):
            status_text = "healthy" if savings_pct >= 20 else "modest"
            return (
                f"This month, your total income is **{currency}{income:,.2f}** and total expenses are **{currency}{expenses:,.2f}**.\n\n"
                f"Your net savings are **{currency}{savings:,.2f}**, representing a **{savings_pct}%** ({status_text}) savings rate."
            )

        if any(w in q for w in ['student', 'college', 'allowance']):
            return (
                f"As a student or young professional:\n\n"
                f"• **Track Every Micro-Spend:** Small daily snacks and rides often add up to 30% of student allowances.\n"
                f"• **Cook / Pack Lunches:** Dining out is typically 3x more expensive than home food.\n"
                f"• **Student Discounts:** Always utilize student IDs for public transit, streaming services, and educational software.\n"
                f"• **Target:** Try to set aside even 10% of your allowance into an emergency buffer."
            )

        if any(w in q for w in ['emergency fund', 'emergency', 'buffer']):
            target = expenses * 3
            return (
                f"An emergency fund provides financial security against unexpected life events:\n\n"
                f"• **Recommended Size:** 3 to 6 months of basic living costs. For your current spending, that is **{currency}{target:,.2f}** to **{currency}{expenses * 6:,.2f}**.\n"
                f"• **Where to keep it:** In a separate, easily accessible savings account or liquid deposit.\n"
                f"• **How to build it:** Automate a fixed transfer (e.g. 15% of each paycheck) until your 3-month goal is reached."
            )

        if any(w in q for w in ['budget for next month', 'simple budget', 'plan']):
            return (
                f"Here is a recommended baseline budget for next month based on your {currency}{income:,.2f} income:\n\n"
                f"• **Needs (50%):** {currency}{income * 0.5:,.2f} (Rent, Utilities, Groceries)\n"
                f"• **Wants (30%):** {currency}{income * 0.3:,.2f} (Entertainment, Dining, Shopping)\n"
                f"• **Savings (20%):** {currency}{income * 0.2:,.2f} (Emergency Fund / Investments)\n\n"
                f"You can create these targets directly in the **Monthly Budgets** tab."
            )

        # Default helpful response
        return (
            f"Here is a snapshot of your finances:\n\n"
            f"• **Income:** {currency}{income:,.2f}\n"
            f"• **Expenses:** {currency}{expenses:,.2f}\n"
            f"• **Savings:** {currency}{savings:,.2f} ({savings_pct}%)\n"
            f"• **Top Expense:** {top_cat} ({currency}{top_amt:,.2f})\n\n"
            f"Feel free to ask me:\n"
            f"- *\"Where am I spending the most?\"*\n"
            f"- *\"How can I reduce my expenses?\"*\n"
            f"- *\"How do I build an emergency fund?\"*"
        )
