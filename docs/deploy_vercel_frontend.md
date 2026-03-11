# 🚀 Deploying TalentPulse Frontend to Vercel

This guide walks you through every step to deploy the React frontend to Vercel — **completely free**.

---

## Prerequisites

You need:
- A free [Vercel account](https://vercel.com/signup)
- A [GitHub account](https://github.com/join)
- The project code pushed to a GitHub repository
- Your **HuggingFace Space URL** from the backend deployment (e.g., `https://your-name-talentpulse-backend.hf.space`)

---

## Step 1 — Push your project to GitHub

If you haven't already, create a GitHub repository and push this project.

1. Go to [https://github.com/new](https://github.com/new)
2. Name the repository: `talentpulse-frontend` (or any name)
3. Keep it **Public** (makes Vercel integration easier)
4. Click **Create repository**

Now push your local code. Open PowerShell in the project root folder:

```bash
git init
git add .
git commit -m "Initial commit: TalentPulse HR system"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/talentpulse-frontend.git
git push -u origin main
```

> **Tip:** If you already have the project on GitHub just make sure all your latest changes are committed and pushed.

---

## Step 2 — Create a Vercel account

1. Go to [https://vercel.com/signup](https://vercel.com/signup)
2. Click **Continue with GitHub** — this links your GitHub account automatically
3. Authorize Vercel to access your GitHub repositories

---

## Step 3 — Import your project to Vercel

1. On your Vercel dashboard, click the **Add New…** button (top right)
2. Click **Project**
3. You will see a list of your GitHub repositories — find `talentpulse-frontend` and click **Import**

---

## Step 4 — Configure the project settings

On the configuration page:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

> **Critical:** Set **Root Directory** to `frontend`. The frontend code is inside the `frontend/` subfolder, not the repo root.

---

## Step 5 — Add the environment variable

This is the most important step — it tells the frontend where your backend is hosted.

1. On the same configuration page, scroll down to **Environment Variables**
2. Click **Add**
3. Fill in:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://YOUR_USERNAME-talentpulse-backend.hf.space`
4. Click **Save**

Replace `YOUR_USERNAME-talentpulse-backend` with your actual HuggingFace Space URL (the one you saved in the backend deployment guide).

---

## Step 6 — Deploy!

1. Click the **Deploy** button
2. Vercel will:
   - Install npm packages
   - Run `vite build`
   - Deploy the output to a CDN
3. This takes about **1–2 minutes**
4. When done, you will see **"Congratulations! Your project has been deployed."**

---

## Step 7 — Open your live frontend

1. Click **Visit** (or the preview URL shown)
2. Your URL will look like: `https://talentpulse-frontend.vercel.app`
3. Navigate to the **Employees** tab
4. Click any employee card — you should see the **loading spinner** appear, then the live attrition risk score, SHAP feature drivers, and DiCE intervention plans load in!

---

## Step 8 — (Optional) Add a custom domain

If you have a domain name (e.g., `talentpulse.io`):

1. In your Vercel project, go to **Settings → Domains**
2. Click **Add**
3. Type your domain name and follow the DNS instructions Vercel provides

---

## Updating the frontend after code changes

Every time you push to the `main` branch on GitHub, Vercel automatically rebuilds and redeploys:

```bash
git add .
git commit -m "Update employee view UI"
git push origin main
```

Vercel will detect the push and deploy the new version in ~1 minute.

---

## How to update the environment variable

If your HuggingFace Space URL changes:

1. In Vercel, go to your project → **Settings → Environment Variables**
2. Find `VITE_API_URL` and click the edit (pencil) icon
3. Update the value and click **Save**
4. Go to **Deployments** and click **Redeploy** on the latest deployment

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails with "Cannot find module" | Make sure **Root Directory** is set to `frontend` in Vercel settings |
| Employee click shows "Inference failed" | Check `VITE_API_URL` is set correctly — no trailing slash |
| Data loads but UI looks broken | Run `npm run build` locally first to catch any build errors |
| CORS error in browser console | The backend's `allow_origins=["*"]` should handle this — double-check the Space is running |
| HF Space is sleeping (first request slow) | Visit `https://YOUR_SPACE.hf.space/` once manually to wake it up |

---

## Final architecture summary

```
User Browser
    │
    ▼
Vercel CDN (React/Vite frontend)
    │  POST /infer  with employee features
    ▼
HuggingFace Spaces (FastAPI Docker backend)
    │  loads pkl files at startup
    ├─ XGBoost → attrition probability
    ├─ RF      → attrition reason
    ├─ SHAP    → top-5 feature drivers
    └─ DiCE    → intervention plans
```
