# 09. Vercel Serverless Deployment Guide

## Overview
This guide provides complete instructions to deploy the **Personal Finance Advisor Bot** onto **Vercel** serverless infrastructure using Python 3.11, WSGI request routing, and automatic cold-start database seeding.

---

## 1. How the Vercel Architecture Works

```text
[ User Browser ]
       │
       ▼ (HTTPS Request)
[ Vercel Global Edge CDN ]
       │
   ┌───┴─────────────────────────────────────────┐
   │                                             │
   ▼ Static Route (/static/*)                    ▼ Serverless Route (/*)
[ Edge Static Storage ]                   [ api/index.py (Flask WSGI) ]
 (css/style.css, js/main.js, ...)                │
                                                 ▼
                                          [ /tmp/finance.db (SQLite) ]
                                          *Auto-seeded on cold start*
```

### Key Components Configured:
1. **`vercel.json`**:
   - Directs `/static/*` requests to Vercel's edge cache for sub-10ms delivery.
   - Rewrites all other routes (`/*`) to `api/index.py`.
2. **`api/index.py`**:
   - Exposes the production WSGI application instance.
   - Automatically initializes SQLite tables and seeds the demo account on container cold start in `/tmp/finance.db`.
3. **`config.py`**:
   - Detects the `VERCEL=1` environment variable.
   - Automatically switches SQLite to the writable `/tmp` directory, preventing `readonly filesystem` errors.

---

## 2. Database Considerations on Vercel

### 2.1 Demo & Viva Voce Evaluations (Default / Free)
Vercel serverless containers provide a writable directory at `/tmp`. 
- Our self-healing code automatically creates `/tmp/finance.db` and populates the sample student account (`demo@finance.test` / `Password123!`).
- Perfect for live presentations, examiner testing, and portfolio showcases with **zero external database setup required**.
- *Note*: Because serverless containers recycle periodically, newly added records in `/tmp` will reset back to the default demo state when the container sleeps.

### 2.2 Permanent Production Persistence (Optional)
If you require long-term persistent data storage across serverless restarts, you can connect a free hosted PostgreSQL database:
1. Create a free PostgreSQL database at [Neon.tech](https://neon.tech/) or [Supabase.com](https://supabase.com/).
2. Copy the connection string (e.g., `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`).
3. Add it as an environment variable in Vercel:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://...`
4. Our `config.py` will automatically switch from SQLite to PostgreSQL without modifying any application code!

---

## 3. Step-by-Step Deployment Guide

### Step 3.1: Commit and Push to GitHub
Open your terminal in the project directory:
```powershell
git add .
git commit -m "Configure Vercel serverless entrypoint and configuration"
git push origin main
```

---

### Step 3.2: Connect Project in Vercel Dashboard
1. Go to [vercel.com](https://vercel.com/) and sign in with your GitHub account.
2. On your Vercel Dashboard, click **"Add New..."** $\rightarrow$ **"Project"**.
3. Under **"Import Git Repository"**, find `personal-finance-advisor` and click **"Import"**.

---

### Step 3.3: Configure Project Settings & Environment Variables
In the Vercel configuration screen:
- **Framework Preset**: Leave as **Other** (Vercel will automatically detect `vercel.json`).
- **Root Directory**: `./` (leave default).
- Expand **Environment Variables** and add the following keys:

| Variable Name | Recommended Value | Notes |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(A random 32+ character string)* | Secures session cookies |
| `FLASK_ENV` | `production` | Enables production optimizations |
| `GEMINI_API_KEY` | `your_gemini_api_key_here` | *(Optional)* If omitted, the offline rule engine is used |
| `DATABASE_URL` | *(Leave empty for default SQLite in `/tmp`)* | Or paste PostgreSQL URI for permanent storage |

---

### Step 3.4: Deploy
1. Click the **"Deploy"** button.
2. Vercel will install dependencies from `requirements.txt`, build the `@vercel/python` lambda, and deploy edge routes (takes ~45–60 seconds).
3. Once completed, Vercel will display celebration confetti and provide your live production URL:  
   👉 `https://your-project-name.vercel.app`

---

## 4. Testing Your Live Vercel Deployment

1. Open your live Vercel URL in any browser or on your smartphone.
2. On the login page, click **`⚡ Quick Demo Account`** to auto-fill:
   - **Email**: `demo@finance.test`
   - **Password**: `Password123!`
3. Click **Sign In**.
4. Test all live features:
   - View 6-month historical cashflow bar charts and spending doughnut charts.
   - Enter a new expense and observe real-time AI auto-categorization.
   - Ask the AI Financial Advisor questions via interactive chat.
   - Click **"Print / Save as PDF"** or **"Export CSV"** in the Reports tab.

---

## 5. Troubleshooting Vercel Deployments

### Issue: `ModuleNotFoundError: No module named '...'`
- **Cause**: A dependency is missing from `requirements.txt`.
- **Solution**: All required packages (`Flask`, `Flask-SQLAlchemy`, `google-generativeai`, `requests`, `python-docx`) are already configured in `requirements.txt`. Ensure your latest commit includes `requirements.txt`.

### Issue: Function Timeout (504 Gateway Timeout)
- **Cause**: External API latency when connecting to Google Gemini.
- **Solution**: Gemini 1.5 Flash responds in under 1 second. If you encounter slow connections, Vercel free tier allows up to 10-second serverless execution limits. If an API call fails, our offline heuristic engine provides instantaneous fallback advice.
