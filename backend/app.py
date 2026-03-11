"""
app.py — TalentPulse FastAPI Backend
Deployed on HuggingFace Spaces (Docker SDK), port 7860.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import json
import os

from inference import run_inference

# ── Load employee metadata ────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data", "ibm_employees.json")

with open(_DATA) as f:
    IBM_EMPLOYEES: list = json.load(f)

# Index by EmployeeNumber for fast lookup
EMPLOYEE_INDEX: Dict[int, dict] = {
    int(e["EmployeeNumber"]): e for e in IBM_EMPLOYEES
}

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TalentPulse Attrition API",
    description=(
        "Live inference: XGBoost (attrition risk) + RF (reason) + "
        "SHAP (feature attribution) + DiCE (counterfactual interventions)."
    ),
    version="1.0.0",
)

# Allow all origins during development; tighten in production to your Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ─────────────────────────────────────────────────
class EmployeeFeatures(BaseModel):
    """Raw IBM HR features (matches dataset.csv columns, minus Attrition)."""
    EmployeeNumber: int
    Age: int
    BusinessTravel: str
    DailyRate: int
    Department: str
    DistanceFromHome: int
    Education: int
    EducationField: str
    EmployeeCount: int = 1
    EnvironmentSatisfaction: int
    Gender: str
    HourlyRate: int
    JobInvolvement: int
    JobLevel: int
    JobRole: str
    JobSatisfaction: int
    MaritalStatus: str
    MonthlyIncome: int
    MonthlyRate: int
    NumCompaniesWorked: int
    Over18: str = "Y"
    OverTime: str
    PercentSalaryHike: int
    PerformanceRating: int
    RelationshipSatisfaction: int
    StandardHours: int = 80
    StockOptionLevel: int
    TotalWorkingYears: int
    TrainingTimesLastYear: int
    WorkLifeBalance: int
    YearsAtCompany: int
    YearsInCurrentRole: int
    YearsSinceLastPromotion: int
    YearsWithCurrManager: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health():
    """Health check."""
    return {"status": "ok", "service": "TalentPulse Attrition API", "version": "1.0.0"}


@app.get("/employees", tags=["Employees"])
def list_employees():
    """Return the 5 IBM HR employees (metadata + raw features)."""
    return {"employees": IBM_EMPLOYEES}


@app.get("/employees/{employee_number}", tags=["Employees"])
def get_employee(employee_number: int):
    """Return a single employee by EmployeeNumber."""
    emp = EMPLOYEE_INDEX.get(employee_number)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_number} not found")
    return emp


@app.post("/infer", tags=["Inference"])
def infer(employee: EmployeeFeatures):
    """
    Run full live inference for one employee.

    Returns:
    - attrition_prob + attrition_pct + risk_tier
    - primary_reason (Stage 2 RF)
    - reason_probs (Burnout/Compensation/Stagnation/Career Growth)
    - shap_top5: top-5 SHAP feature attributions
    - dice_plans: 3 counterfactual intervention plans
    """
    try:
        raw = employee.model_dump()
        result = run_inference(raw)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/infer/{employee_number}", tags=["Inference"])
def infer_by_id(employee_number: int):
    """
    Convenience GET: infer by EmployeeNumber from the stored dataset.
    Equivalent to POST /infer with the stored employee's features.
    """
    emp = EMPLOYEE_INDEX.get(employee_number)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_number} not found")
    try:
        result = run_inference(emp)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
