# TalentPulse HR Attrition Risk System — Implementation Plan

## What We're Building

The TalentPulse project has:
- A trained **XGBoost + Random Forest** pipeline saved in `results/` (pkl/json/csv files)
- A **React/Vite** frontend with an [EmployeesView.jsx](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/features/employees/EmployeesView.jsx) that currently shows hardcoded dummy data
- An **empty** `backend/` folder

We will build the complete pipeline so that clicking an employee card in the frontend triggers a **real API call** to a FastAPI backend (deployed on HuggingFace Spaces), which returns attrition probability, top-5 SHAP features, and DiCE counterfactual interventions — all displayed live in the UI.

**For now:** We use only the **first 5 rows** of [dataset.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/dataset.csv) (IBM HR employees #1, #2, #4, #5, #7), with pre-computed results from `results/*.csv`.

---

## Proposed Changes

### Data Layer

#### [NEW] `frontend/src/data/ibmEmployees.js`
- 5 IBM HR employees from [dataset.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/dataset.csv) (all columns except `Attrition`)
- Each employee augmented with UI display fields: [id](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/j.id), `initials`, `name` (generated), `workMode`, etc.
- `EmployeeNumber` used as the key to link to backend predictions

#### [NEW] `frontend/src/data/inferenceResults.js`
- Pre-computed attrition + SHAP + DiCE for the 5 employees, embedded as a JS module
- Used as frontend fallback/local mock when backend is not available

---

### Backend (FastAPI — HuggingFace Spaces)

#### [NEW] `backend/app.py`
- FastAPI app with CORS enabled for the Vercel frontend URL
- `GET /` — health check endpoint
- `GET /employees` — returns list of all 5 employee IDs and basic metadata
- `GET /infer/{employee_id}` — returns full inference result (attrition probability, risk tier, primary reason, reason probs, top-5 SHAP explanation, DiCE interventions)
- Data sourced from: pre-computed CSVs ([attrition_results.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/attrition_results.csv), [shap_results.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/shap_results.csv), [dice_interventions.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/dice_interventions.csv)) loaded at startup
- **No live model inference in v1** — results are pre-computed due to HF Spaces free-tier limitations and to avoid slow cold-starts

#### [NEW] `backend/inference_store.py`
- Loads [attrition_results.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/attrition_results.csv), [shap_results.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/shap_results.csv), [dice_interventions.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/dice_interventions.csv), [feature_columns.json](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/feature_columns.json) at module import
- Returns structured dicts for any `EmployeeNumber`
- Handles `N/A` primary_reason for low-risk employees

#### [NEW] `backend/requirements.txt`
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pandas==2.2.2
python-multipart==0.0.9
```

#### [NEW] `backend/README.md`
- HuggingFace Spaces YAML header: `title: TalentPulse Backend`, `sdk: docker`, `app_port: 7860`

#### [NEW] `backend/Dockerfile`
- Python 3.11 slim base
- Copies result CSVs + JSON into the image for self-contained deployment

#### [NEW] `backend/.gitignore`
- Excludes `__pycache__`, `.env`

---

### Frontend Updates

#### [MODIFY] [frontend/src/app/MockHRTalentDashboard.jsx](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/app/MockHRTalentDashboard.jsx)
- Import `ibmEmployees` from `../data/ibmEmployees.js` instead of `../mocks/employees.js`
- Pass `ibmEmployees` as `employees` prop to [EmployeesView](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/features/employees/EmployeesView.jsx#8-324)

#### [MODIFY] [frontend/src/features/employees/EmployeesView.jsx](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/features/employees/EmployeesView.jsx)
- Add `useState` for `analysis` (backend result) and `loading`/`error` states
- On employee click: call `fetch(`${import.meta.env.VITE_API_URL}/infer/${e.EmployeeNumber}`)` 
- Display real data in the right panel:
  - **Attrition Risk** — real `attrition_probability` (as %) and `risk_tier`
  - **Primary Reason** — `primary_reason` from Stage 2 RF model
  - **Key Drivers (SHAP)** — `shap_feature_1..5` with `shap_value_1..5` (positive = risk, negative = protective)
  - **DiCE Interventions** — grouped by `cf_index` (1,2,3), showing `intervention_label` and `new_attrition_prob`
- Graceful loading spinner and error fallback

#### [NEW] `frontend/.env.example`
```
VITE_API_URL=https://your-space.hf.space
```

#### [NEW] `frontend/.env.local` (user fills in after HF deploy)
```
VITE_API_URL=http://localhost:8000
```

---

### Deployment Docs

#### [NEW] `docs/deploy_huggingface_spaces.md`
- Step-by-step: HF account, new Space (Docker SDK), upload result files + backend code, test API

#### [NEW] `docs/deploy_vercel_frontend.md`
- Step-by-step: GitHub push, Vercel account, import repo, set `VITE_API_URL` env var, deploy

---

## File Structure After Changes

```
talentpulse-frontend-main/
├── dataset.csv
├── results/
│   ├── attrition_results.csv      ← loaded by backend
│   ├── shap_results.csv           ← loaded by backend
│   ├── dice_interventions.csv     ← loaded by backend
│   ├── feature_columns.json       ← loaded by backend
│   ├── model_xgb_stage1.pkl       ← (not used in v1 pre-computed mode)
│   ├── model_rf_stage2.pkl        ← (not used in v1 pre-computed mode)
│   └── preprocessor.pkl           ← (not used in v1 pre-computed mode)
├── backend/
│   ├── app.py                     ← FastAPI entrypoint [NEW]
│   ├── inference_store.py         ← CSV loader [NEW]
│   ├── requirements.txt           ← Python deps [NEW]
│   ├── Dockerfile                 ← HF Spaces Docker [NEW]
│   ├── README.md                  ← HF Space metadata [NEW]
│   ├── .gitignore                 [NEW]
│   └── results/                   ← copy of result CSVs for HF [NEW]
│       ├── attrition_results.csv
│       ├── shap_results.csv
│       ├── dice_interventions.csv
│       └── feature_columns.json
├── frontend/
│   ├── .env.example               [NEW]
│   ├── .env.local                 [NEW]  ← not committed
│   ├── src/
│   │   ├── data/
│   │   │   ├── ibmEmployees.js    [NEW]  ← 5 IBM employees
│   │   │   └── inferenceResults.js [NEW] ← pre-computed results
│   │   ├── app/
│   │   │   └── MockHRTalentDashboard.jsx [MODIFY] ← use ibmEmployees
│   │   └── features/employees/
│   │       └── EmployeesView.jsx  [MODIFY] ← real API + SHAP/DiCE UI
│   └── package.json              (no change needed)
└── docs/
    ├── deploy_huggingface_spaces.md [NEW]
    └── deploy_vercel_frontend.md   [NEW]
```

---

## Verification Plan

> [!NOTE]
> There are **no existing automated tests** in this project. Verification will be a combination of running the dev server and manual UI inspection.

### Backend Local Test
1. In `backend/`, run: `pip install -r requirements.txt`
2. Run: `uvicorn app:app --reload --port 8000`
3. Open browser: `http://localhost:8000/` → should return `{"status": "ok"}`
4. Open: `http://localhost:8000/infer/1` → should return full JSON with attrition ~98.3%, SHAP features, DiCE interventions
5. Open: `http://localhost:8000/infer/2` → should return attrition ~6.97%, risk_tier "Low"

### Frontend Local Test
1. In `frontend/`, set `VITE_API_URL=http://localhost:8000` in `.env.local`
2. Run: `npm run dev`
3. Navigate to **Employees** tab
4. Click on **Employee #1** (EmployeeNumber 1, Sales Executive) — expect right panel to show "Critical" risk, ~98.3%, SHAP and DiCE data
5. Click on **Employee #2** (Research Scientist) — expect "Low" risk, ~6.97%
6. Verify SHAP drivers section shows feature names + values with correct color (red for positive SHAP = risk factor, green for negative = protective)
7. Verify DiCE shows intervention labels grouped by CF plan (1, 2, 3)
