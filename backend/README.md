---
title: TalentPulse Backend
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: HR attrition risk prediction API (XGBoost + SHAP + DiCE)
---

# TalentPulse — Attrition Risk API

FastAPI backend for the **TalentPulse HR Talent Management System**.

## What this Space does

Accepts raw IBM HR employee feature data and returns:

| Output | Model |
|--------|-------|
| Attrition probability + risk tier | XGBoost (Stage 1) |
| Primary reason for attrition | Random Forest (Stage 2) |
| Top-5 SHAP feature attributions | SHAP TreeExplainer |
| 3 counterfactual intervention plans | Custom DiCE engine |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/employees` | List all 5 IBM demo employees |
| `GET` | `/employees/{id}` | Get employee by EmployeeNumber |
| `POST` | `/infer` | Run full inference from raw features |
| `GET` | `/infer/{id}` | Run inference by EmployeeNumber |

## Interactive docs

Visit `/docs` on your Space URL for the Swagger UI.
