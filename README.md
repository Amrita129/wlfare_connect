# WelfareConnect: Welfare Scheme Awareness, Eligibility & Utilization Gap Analysis System

A comprehensive web platform engineered with **Flask**, **SQLAlchemy**, and **Plotly** to bridge last-mile welfare awareness and diagnose citizen drop-off bottlenecks in social welfare distribution.

---

## 🌟 Key Features

1. **Citizen Registration & Secure Authentication:**
   - Password hashing with `werkzeug.security` (PBKDF2-SHA256).
   - Dynamic profile creation: Age, Gender, Occupation, Annual Income, Social Category, State, District.
   - Role-based authorization: Citizen vs. Administrator.

2. **Explainable Eligibility Engine (30+ Real Government Schemes):**
   - Deterministic, rule-based matching covering National & State schemes (Education, Agriculture, Women & Child, Health, Housing, Social Security, Banking).
   - Itemized criteria checks (Age limits, Income ceilings, Occupation, Region).
   - Match percentage scoring (e.g. 95% Match) and "Why you qualify" explainability tags.

3. **Multilingual Architecture (5 Indian Languages):**
   - Full bilingual/multilingual UI translation across **English (🇬🇧)**, **Hindi (हिंदी)**, **Telugu (తెలుగు)**, **Odia (ଓଡ଼ିଆ)**, and **Marathi (मराठी)**.
   - Client-side dynamic switching persisted across sessions.

4. **Welfare Delivery Funnel & Gap Analysis (Core Academic Feature):**
   - Tracks citizen applications along the 5-stage lifecycle:
     $$\text{Eligible} \longrightarrow \text{Aware} \longrightarrow \text{Applied} \longrightarrow \text{Approved} \longrightarrow \text{Received}$$
   - Calculates step-by-step conversion rates and dropout counts.
   - **Automated Bottleneck Diagnostics:** Isolates the stage with the highest citizen attrition (e.g., administrative review delays) and provides actionable policy recommendations.
   - Interactive **Plotly** data visualizations: Funnel Waterfall, Scheme Performance Bar Chart, Category Donut Chart.

5. **Application Tracking & Notifications:**
   - Visual 5-stage stepper progress tracker for citizen applications.
   - In-app notification center for new scheme alerts and application status changes.
   - Direct links to verified official government application portals (MyScheme, IndiaPost, NSP).

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.11+ / 3.14, Flask 3.1.2
- **ORM & Database:** Flask-SQLAlchemy 3.1.1 (SQLite for development, PostgreSQL / MySQL ready)
- **Data Analytics & Visualization:** Plotly 6.3.1, Pandas 2.3.3
- **Frontend:** Jinja2 Templates, Modern Responsive CSS, Vanilla JavaScript (i18n engine)
- **Production Server:** Gunicorn 23.0.0

---

## 🚀 Running Locally

### Step 1: Open Terminal in Project Directory
```powershell
cd d:\Anu\welfare_scheme_system\welfare_scheme_system\welfare_scheme_system
```

### Step 2: Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🔐 Demo Credentials

| Role | Email | Password | Dashboard Destination |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@welfareconnect.in` | `admin123` | `/admin` & `/admin/gap-analysis` |
| **Demo Citizen** | `user@welfareconnect.in` | `user123` | `/user` & `/find-schemes` |

*Note: Any citizen can also click **Register** on the homepage to create a brand new personal account with persistent data.*

---

## 🧪 Running Automated Tests

Run the built-in 21-point test suite covering authentication, eligibility matching, gap analysis, and security guards:

```bash
python -c "from app import create_app; import test_runner; test_runner.run()"
```
Or execute:
```powershell
.\venv\Scripts\python.exe -c "
from app import create_app, db
from app.models import User, Citizen, Scheme, Application
app = create_app()
client = app.test_client()
print('Health check:', client.get('/api/health').json)
print('Analytics check:', client.get('/api/analytics').json['stages'])
"
```

---

## 🌐 Production Deployment Guide

### Option A: Render (Recommended - Free Tier)

1. Create a free account on [render.com](https://render.com).
2. Push your project code to a GitHub repository.
3. On Render, click **New +** → **Web Service** and connect your GitHub repository.
4. Set the following settings:
   - **Name:** `welfareconnect`
   - **Root Directory:** (leave empty or set path to project directory)
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: `<generate-a-random-secret-string>`
   - `FLASK_ENV`: `production`
6. Click **Create Web Service**. Your app will deploy to a public `https://welfareconnect.onrender.com` URL!

### Option B: Railway

1. Sign up at [railway.app](https://railway.app).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Railway automatically detects `Procfile` (`web: gunicorn run:app`) and requirements.
4. Add `SECRET_KEY` in Railway Variables and click Deploy.

### Option C: PythonAnywhere

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Upload files or `git clone` your repository into your home directory.
3. Create a virtual environment with `python3 -m venv venv` and run `pip install -r requirements.txt`.
4. In the **Web** tab, create a manual Flask configuration and point WSGI configuration file to:
   ```python
   import sys
   path = '/home/yourusername/welfare_scheme_system'
   if path not in sys.path:
       sys.path.append(path)
   from run import app as application
   ```
5. Reload the web app.

---

## 📑 Academic Viva Highlights

When demonstrating this project during your viva examination:
1. **Explain the Funnel:** Show how citizen attrition is mapped from *Eligible* to *Received*, quantifying where policy execution fails.
2. **Demonstrate Bottleneck Analysis:** Point out the largest dropout stage and how the system generates actionable administrative recommendations.
3. **Show Explainability:** Open any scheme detail page to demonstrate the live itemized criteria evaluation comparing the citizen's profile against official criteria.
4. **Show Multilingual Accessibility:** Switch languages in real time (e.g. to Hindi or Marathi) to demonstrate inclusivity for rural citizens.
