# 🤗 Deploying TalentPulse Backend to HuggingFace Spaces (Docker)

This guide walks you through every step to host the FastAPI backend on HuggingFace Spaces — **completely free**.

---

## Prerequisites

You need:
- A free [HuggingFace account](https://huggingface.co/join)
- [Git](https://git-scm.com/downloads) installed on your computer
- [Git LFS](https://git-lfs.com/) installed (for the `.pkl` model files — they're large)

---

## Step 1 — Create a HuggingFace account

1. Open your browser and go to [https://huggingface.co/join](https://huggingface.co/join)
2. Enter your **email**, **username**, and **password**
3. Click **Create account**
4. Check your email and click the verification link HuggingFace sends you
5. Log in to your account

---

## Step 2 — Install the HuggingFace CLI (command line tool)

Open your terminal (PowerShell on Windows) and run:

```bash
pip install huggingface_hub
```

Then log in:

```bash
huggingface-cli login
```

When it asks for a token:
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **New token**
3. Give it a name (e.g., `talentpulse-deploy`)
4. Select **Write** permission
5. Click **Generate**
6. Copy the token and paste it into the terminal → press Enter

---

## Step 3 — Create a new HuggingFace Space

1. Go to [https://huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the form:
   - **Space name:** `talentpulse-backend` (or any name you like)
   - **License:** MIT
   - **Select the Space SDK:** Choose **Docker**
   - **Visibility:** Public (required for the free tier)
3. Click **Create Space**
4. You will see an empty Space page — this is normal

---

## Step 4 — Install Git LFS (Large File Storage)

The `.pkl` model files are larger than GitHub/HF's 10 MB limit. Git LFS handles them.

```bash
# Windows (with winget)
winget install GitHub.GitLFS

# Or download from https://git-lfs.com/
```

After installing, enable it:

```bash
git lfs install
```

---

## Step 5 — Clone your new HuggingFace Space locally

In your terminal, run (replace `YOUR_USERNAME` with your actual HuggingFace username):

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/talentpulse-backend
cd talentpulse-backend
```

---

## Step 6 — Copy the backend files into the cloned folder

From the project root, copy these files/folders into the cloned `talentpulse-backend/` folder:

```
backend/app.py              → talentpulse-backend/app.py
backend/inference.py        → talentpulse-backend/inference.py
backend/requirements.txt    → talentpulse-backend/requirements.txt
backend/Dockerfile          → talentpulse-backend/Dockerfile
backend/README.md           → talentpulse-backend/README.md
backend/data/               → talentpulse-backend/data/
backend/models/             → talentpulse-backend/models/
```

> **Important:** The `models/` folder contains `model_xgb_stage1.pkl`, `model_rf_stage2.pkl`, `preprocessor.pkl`, `feature_columns.json`. Make sure all 4 files are there.

On Windows (PowerShell), from the project root:

```powershell
$dest = "PATH_TO_YOUR\talentpulse-backend"
Copy-Item "backend\app.py"         "$dest\app.py"
Copy-Item "backend\inference.py"   "$dest\inference.py"
Copy-Item "backend\requirements.txt" "$dest\requirements.txt"
Copy-Item "backend\Dockerfile"     "$dest\Dockerfile"
Copy-Item "backend\README.md"      "$dest\README.md"
Copy-Item "backend\data"           "$dest\data"   -Recurse
Copy-Item "backend\models"         "$dest\models" -Recurse
```

---

## Step 7 — Track large files with Git LFS

Inside the cloned `talentpulse-backend/` folder, tell Git LFS to track `.pkl` files:

```bash
cd talentpulse-backend
git lfs track "*.pkl"
git add .gitattributes
```

---

## Step 8 — Commit and push everything

```bash
git add .
git commit -m "Initial deploy: TalentPulse FastAPI backend with XGBoost + SHAP + DiCE"
git push origin main
```

> **Note:** The push might take a few minutes because the `.pkl` files are uploaded via Git LFS.

---

## Step 9 — Watch the build on HuggingFace

1. Go to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/talentpulse-backend`
2. Click the **Logs** tab at the top
3. You will see Docker building the image — this takes **3–6 minutes** on first run
4. When it says `Application startup complete`, your backend is live!

---

## Step 10 — Test your deployed API

Your Space URL is:
```
https://YOUR_USERNAME-talentpulse-backend.hf.space
```

Test it in your browser:

1. **Health check:** `https://YOUR_USERNAME-talentpulse-backend.hf.space/`
   - Should return: `{"status": "ok"}`

2. **Interactive docs (Swagger UI):** `https://YOUR_USERNAME-talentpulse-backend.hf.space/docs`
   - You can test all endpoints directly from the browser here!

3. **List employees:** `https://YOUR_USERNAME-talentpulse-backend.hf.space/employees`

4. **Infer by EmployeeNumber:** `https://YOUR_USERNAME-talentpulse-backend.hf.space/infer/1`
   - Should return attrition probability ~98.3%, SHAP top-5, and DiCE plans

---

## Step 11 — Copy your Space URL

Your final API URL (you'll need this for the frontend Vercel deployment):

```
https://YOUR_USERNAME-talentpulse-backend.hf.space
```

Write this down. You will add it as an environment variable in Vercel.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails with "package not found" | Check `requirements.txt` version pins match what's in the Dockerfile Python version |
| `.pkl` file too large | Make sure `git lfs install` was run BEFORE `git add` |
| `Application startup complete` but 502 error | Wait 30 more seconds — HF Spaces can take a moment to become ready |
| CORS errors from frontend | The backend already allows all origins (`allow_origins=["*"]`) |
| Cold start is slow | Free tier HF Spaces sleep after 30 min of inactivity. First request after sleep takes ~30 sec |
