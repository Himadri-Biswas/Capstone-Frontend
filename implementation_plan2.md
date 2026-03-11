# TalentPulse HR Attrition Risk System — Implementation Plan (v2: Live Inference)

## Architecture

```
[React/Vite Frontend on Vercel]
        │  POST /infer  (employee raw features JSON)
        ▼
[FastAPI on HuggingFace Spaces — Docker]
        │  loads pkl/json model files at startup
        ├─ XGBoost Stage 1 → attrition_probability, risk_tier
        ├─ RF Stage 2      → primary_reason, reason_probs
        ├─ SHAP TreeExplainer → top-5 feature attributions
        └─ Custom DiCE engine → 3 counterfactual interventions
```

The backend performs **live inference** — it receives raw employee feature values, applies the same preprocessing pipeline (encoding, feature engineering), runs the models, computes SHAP and DiCE, and returns all results as JSON.

---

## Files To Create/Modify

### Backend (HuggingFace Spaces — Docker SDK)

#### [NEW] `backend/app.py`
FastAPI entrypoint:
- `GET /` → health check
- `GET /employees` → list of 5 IBM employees (metadata only)
- `POST /infer` → accepts raw IBM HR employee JSON → returns full inference result

#### [NEW] `backend/inference.py`
Live inference pipeline — mirrors the notebook exactly:
- **Feature engineering**: computes `income_to_dept_avg`, `promotion_stagnation`, `burnout_proxy`, `total_satisfaction` using dept averages loaded from [preprocessor.pkl](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/preprocessor.pkl)
- **Encoding**: applies `label_encoders`, `business_travel_map`, `marital_status_map`, `gender` and `overtime` maps
- **Stage 1**: XGBoost predict_proba → `attrition_probability`, `risk_tier`
- **Stage 2**: RF predict → `primary_reason`, `reason_probs`
- **SHAP**: `shap.TreeExplainer(xgb_model).shap_values(X_row)` → top-5 by |value|
- **DiCE**: Custom perturbation engine (same as notebook) → 3 CFs (best, 2nd-best, combo)
- **Returns**: structured JSON dict

#### [NEW] `backend/requirements.txt`
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.0
xgboost==2.0.3
shap==0.45.1
joblib==1.4.2
python-multipart==0.0.9
```

#### [NEW] `backend/Dockerfile`
- Python 3.11 slim
- Copies `requirements.txt`, installs deps
- Copies `app.py`, `inference.py`, and `models/` folder (pkl/json files)
- Exposes port 7860 (HF Spaces Docker default)
- CMD: `uvicorn app:app --host 0.0.0.0 --port 7860`

#### [NEW] `backend/README.md`
HuggingFace Spaces YAML header:
```yaml
---
title: TalentPulse Backend
emoji: 🧠
sdk: docker
app_port: 7860
---
```

#### [NEW] `backend/models/` (directory)
Place these files here (copied from `results/`):
- [model_xgb_stage1.pkl](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/model_xgb_stage1.pkl)
- [model_rf_stage2.pkl](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/model_rf_stage2.pkl)
- [preprocessor.pkl](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/preprocessor.pkl)
- [feature_columns.json](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/feature_columns.json)

#### [NEW] `backend/data/ibm_employees.json`
The 5 IBM employees' raw features (from dataset.csv rows 1–5), for the `/employees` endpoint.

#### [NEW] `backend/.gitignore`

---

### Frontend

#### [NEW] `frontend/src/data/ibmEmployees.js`
5 IBM HR employees from [dataset.csv](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/dataset.csv) (EmployeeNumbers 1,2,4,5,7), all columns except `Attrition`, plus UI fields: [id](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/j.id), `initials`, `name` (descriptive), `workMode`, `skills`, `location`, `manager`, `email`, `joined`, `lastPromotion`.

#### [MODIFY] [frontend/src/app/MockHRTalentDashboard.jsx](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/app/MockHRTalentDashboard.jsx)
- Import from `../data/ibmEmployees.js` instead of `../mocks/employees.js`

#### [MODIFY] [frontend/src/features/employees/EmployeesView.jsx](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/frontend/src/features/employees/EmployeesView.jsx)
Major update to the employee detail panel:
- On employee card click → `POST ${VITE_API_URL}/infer` with the employee's raw feature object
- Show loading spinner while waiting
- On success, display:
  - **Attrition Risk header**: real `attrition_probability` (as `%`), `risk_tier` label (Critical/High/Medium/Low) with tier-specific color
  - **Primary Reason** (Stage 2): `primary_reason` badge (`Burnout`, `Compensation`, `Stagnation`, `Career Growth`, or `N/A`)
  - **Key Drivers (SHAP Top-5)**: bar-like cards for each of the 5 features:
    - Feature name (human-readable label)
    - SHAP value: positive = 🔴 (pushes toward attrition), negative = 🟢 (protective)
    - Visual bar proportional to |shap_value|
  - **DiCE Intervention Plans**: 3 expandable "Plan" cards (CF 1, 2, 3):
    - Each plan lists its `intervention_label(s)` and the resulting `new_attrition_prob` after the change
    - Risk reduction badge: e.g. `-12.4%`
  - Error state for failed inference

#### [NEW] `frontend/.env.example`
```
VITE_API_URL=https://YOUR-SPACE.hf.space
```

#### [NEW] `frontend/.env.local`  (gitignored)
```
VITE_API_URL=http://localhost:8000
```

---

## File Structure After Changes

```
talentpulse-frontend-main/
├── results/                     ← original model outputs (reference)
├── backend/
│   ├── app.py                   [NEW]
│   ├── inference.py             [NEW]
│   ├── requirements.txt         [NEW]
│   ├── Dockerfile               [NEW]
│   ├── README.md                [NEW]
│   ├── .gitignore               [NEW]
│   ├── data/
│   │   └── ibm_employees.json   [NEW]
│   └── models/
│       ├── model_xgb_stage1.pkl (copied from results/)
│       ├── model_rf_stage2.pkl  (copied from results/)
│       ├── preprocessor.pkl     (copied from results/)
│       └── feature_columns.json (copied from results/)
├── frontend/
│   ├── .env.example             [NEW]
│   ├── .env.local               [NEW]
│   └── src/
│       ├── data/
│       │   └── ibmEmployees.js  [NEW]
│       ├── app/
│       │   └── MockHRTalentDashboard.jsx  [MODIFY]
│       └── features/employees/
│           └── EmployeesView.jsx          [MODIFY]
└── docs/
    ├── deploy_huggingface_spaces.md       [NEW]
    └── deploy_vercel_frontend.md          [NEW]
```

---

## Critical Notes

> [!IMPORTANT]
> The `inference.py` must replicate the notebook's preprocessing **exactly** — same encoders, same dept avg dict, same formula for `burnout_proxy` etc. All of this is saved in [preprocessor.pkl](file:///e:/CAPSTONE%20ALL/talentpulse-frontend-main/results/preprocessor.pkl). Loading that bundle is the key to consistent predictions.

> [!WARNING]
> `shap` + `xgboost` + `scikit-learn` have strict version compatibility. The `requirements.txt` pins exact versions matching what the notebook used (xgboost==2.0.3, shap==0.45.1, sklearn==1.5.0). The Dockerfile must use Python 3.11 (same as Kaggle default).

---

## Verification Plan

### Backend Local Test
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# Test:
curl http://localhost:8000/
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d @data/ibm_employees.json
```

### Frontend Local Test
1. Set `VITE_API_URL=http://localhost:8000` in `frontend/.env.local`
2. `npm run dev`
3. Click **Employee #1** → expect ~98.3% Critical risk, SHAP shows `burnout_proxy`, `WorkLifeBalance`, DiCE shows WLB improvement + stock options
4. Click **Employee #2** → expect ~6.97% Low risk with green protective SHAP values
