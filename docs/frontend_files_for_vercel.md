# 📁 Frontend Files to Push to GitHub for Vercel Deployment

This document tells you **exactly which files to include** in your GitHub repo for Vercel to build and deploy the TalentPulse frontend correctly.

---

## The Simple Answer

You push the **entire `talentpulse-frontend-main/` project folder** to GitHub — both `frontend/` and `backend/` can live in the same repo. Then you tell Vercel: **"Look inside the `frontend/` subfolder"**.

You do **not** need to create a separate repo just for the frontend.

---

## Step-by-Step: Push to GitHub

### Step 1 — Open PowerShell in the project root

Navigate to your project folder:

```powershell
cd "e:\CAPSTONE ALL\talentpulse-frontend-main"
```

### Step 2 — Initialise Git (if not already done)

```powershell
git init
git branch -M main
```

### Step 3 — Make sure `.env.local` is gitignored

The file `frontend/.env.local` contains your local backend URL and should **NOT** be pushed. The `frontend/.gitignore` already covers this, but double-check:

Open `frontend/.gitignore` and confirm it contains:
```
.env.local
```

### Step 4 — Stage all files

```powershell
git add .
```

### Step 5 — Commit

```powershell
git commit -m "TalentPulse HR system: frontend + backend + docs"
```

### Step 6 — Connect to GitHub and push

```powershell
git remote add origin https://github.com/YOUR_USERNAME/talentpulse-frontend-main.git
git push -u origin main
```

---

## Exact File List That Vercel Needs

When Vercel builds the project, it looks inside the `frontend/` folder (you set this as the Root Directory). Here is every file it needs — **all of these already exist in your project**:

```
frontend/
│
├── index.html                          ← HTML entry point
├── package.json                        ← npm scripts + dependency list
├── package-lock.json                   ← locked dependency versions
├── .env.example                        ← reference only (not used by Vite at build time)
│
└── src/
    ├── App.jsx                         ← root React component
    ├── main.jsx                        ← Vite entry point (mounts React)
    │
    ├── app/
    │   └── MockHRTalentDashboard.jsx   ← ⭐ Updated: uses ibmEmployees
    │
    ├── data/
    │   └── ibmEmployees.js             ← ⭐ New: 5 IBM HR employees with raw features
    │
    ├── features/
    │   ├── dashboard/
    │   │   └── SimpleDashboard.jsx
    │   ├── employees/
    │   │   └── EmployeesView.jsx       ← ⭐ Updated: live API fetch + SHAP/DiCE UI
    │   ├── layout/
    │   │   ├── Sidebar.jsx
    │   │   └── Topbar.jsx
    │   ├── recruitment/
    │   │   └── JobPostsOnly.jsx
    │   └── upskilling/
    │       └── UpskillingView.jsx
    │
    ├── components/
    │   └── ui/
    │       ├── Button.jsx
    │       ├── Pill.jsx
    │       └── SoftTag.jsx
    │
    ├── lib/
    │   ├── cx.js
    │   └── skillTone.js
    │
    └── mocks/
        ├── employees.js                ← old mock data (kept but no longer used)
        └── jobs.js
```

### ⛔ Do NOT push these files

| File | Why |
|------|-----|
| `frontend/.env.local` | Contains `localhost:8000` — wrong for production; Vercel has its own env var |
| `frontend/node_modules/` | Auto-installed by Vercel via `npm install`; too large to push |
| `backend/models/*.pkl` | Too large for regular Git — use Git LFS only if pushing backend separately |

---

## Vercel Configuration (Recap)

When you import the repo in Vercel's UI, set:

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Vite |
| **Build Command** | `npm run build` *(auto-detected)* |
| **Output Directory** | `dist` *(auto-detected)* |

### Then add the environment variable:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://YOUR_USERNAME-talentpulse-backend.hf.space` |

> ⚠️ **No trailing slash** on the URL. Correct: `https://abc.hf.space` — Wrong: `https://abc.hf.space/`

---

## Quick Verification After Deploy

After Vercel deploys, open your live URL and:

1. Click **Employees** in the sidebar
2. Click any employee card
3. You should see a **loading spinner** → then the live attrition risk %, SHAP drivers, and DiCE plans
4. If you see `"Inference failed"` → double-check `VITE_API_URL` in Vercel → Settings → Environment Variables
