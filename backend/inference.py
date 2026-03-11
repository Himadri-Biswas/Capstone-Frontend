"""
inference.py — Live TalentPulse Inference Engine
Mirrors the notebook (module3-1 version6) preprocessing + model pipeline exactly.

Steps on each call:
  1. Feature engineering  (income_to_dept_avg, promotion_stagnation, burnout_proxy, total_satisfaction)
  2. Encode categoricals  (using saved label_encoders + ordinal maps from preprocessor.pkl)
  3. Stage 1: XGBoost    → attrition_probability, risk_tier
  4. Stage 2: RF         → primary_reason, reason_probs
  5. SHAP                → top-5 feature attributions (TreeExplainer)
  6. DiCE-style engine   → 3 counterfactual intervention plans
"""

import json
import os
import numpy as np
import pandas as pd
import joblib
import shap

# ── Resolve paths relative to this file ───────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS = os.path.join(_HERE, "models")

# ── Load models & preprocessor bundle once at import ─────────────────────────
print("Loading models...", flush=True)
xgb_model = joblib.load(os.path.join(_MODELS, "model_xgb_stage1.pkl"))
rf_model   = joblib.load(os.path.join(_MODELS, "model_rf_stage2.pkl"))
bundle     = joblib.load(os.path.join(_MODELS, "preprocessor.pkl"))

label_encoders      = bundle["label_encoders"]        # dict: JobRole/Department/EducationField → LabelEncoder
dept_avg_dict       = bundle["dept_avg_dict"]          # dict: Department → mean MonthlyIncome
business_travel_map = bundle["business_travel_map"]    # {'Non-Travel':0,'Travel_Rarely':1,'Travel_Frequently':2}
marital_status_map  = bundle["marital_status_map"]     # {'Single':0,'Married':1,'Divorced':2}
REASON_MAP          = bundle["reason_map"]             # {0:'Burnout', 1:'Compensation', 2:'Stagnation', 3:'Career Growth'}
FEATURES            = bundle["feature_columns"]        # ordered list of 31 feature names

with open(os.path.join(_MODELS, "feature_columns.json")) as f:
    FEATURES = json.load(f)

# Build SHAP explainer once
explainer  = shap.TreeExplainer(xgb_model)
BASE_VALUE = float(explainer.expected_value)
print(f"✅ Models loaded. Features: {len(FEATURES)}, SHAP base: {BASE_VALUE:.4f}", flush=True)


# ── Human-readable SHAP feature labels ────────────────────────────────────────
FEATURE_LABELS = {
    "Age": "Age",
    "BusinessTravel": "Business Travel Frequency",
    "Department": "Department",
    "DistanceFromHome": "Distance from Home",
    "Education": "Education Level",
    "EducationField": "Education Field",
    "EnvironmentSatisfaction": "Environment Satisfaction",
    "Gender": "Gender",
    "JobInvolvement": "Job Involvement",
    "JobLevel": "Job Level",
    "JobRole": "Job Role",
    "JobSatisfaction": "Job Satisfaction",
    "MaritalStatus": "Marital Status",
    "MonthlyIncome": "Monthly Income",
    "NumCompaniesWorked": "Number of Companies Worked",
    "OverTime": "Overtime",
    "PercentSalaryHike": "Salary Hike %",
    "PerformanceRating": "Performance Rating",
    "RelationshipSatisfaction": "Relationship Satisfaction",
    "StockOptionLevel": "Stock Option Level",
    "TotalWorkingYears": "Total Working Years",
    "TrainingTimesLastYear": "Training Sessions / Year",
    "WorkLifeBalance": "Work-Life Balance",
    "YearsAtCompany": "Years at Company",
    "YearsInCurrentRole": "Years in Current Role",
    "YearsSinceLastPromotion": "Years Since Last Promotion",
    "YearsWithCurrManager": "Years with Current Manager",
    "income_to_dept_avg": "Income vs Dept Average",
    "promotion_stagnation": "Promotion Stagnation",
    "burnout_proxy": "Burnout Risk Proxy",
    "total_satisfaction": "Overall Satisfaction",
}

# ── Mutable feature ranges for the DiCE engine ────────────────────────────────
MUTABLE_RANGES = {
    "OverTime":                [0, 1],
    "JobSatisfaction":         [1, 2, 3, 4],
    "EnvironmentSatisfaction": [1, 2, 3, 4],
    "WorkLifeBalance":         [1, 2, 3, 4],
    "StockOptionLevel":        [0, 1, 2, 3],
    "JobLevel":                [1, 2, 3, 4, 5],
    "YearsSinceLastPromotion": [0, 1, 2],
    "TrainingTimesLastYear":   [2, 3, 4, 5, 6],
    "MonthlyIncome":           None,   # continuous
    "DistanceFromHome":        None,   # continuous
}
MUTABLE_FEATURES = [f for f in MUTABLE_RANGES if f in FEATURES]


# ─────────────────────────────────────────────────────────────────────────────
# Main preprocessing + inference entry point
# ─────────────────────────────────────────────────────────────────────────────

def _encode_row(raw: dict) -> pd.DataFrame:
    """
    Accepts a raw IBM HR employee dict (as stored in dataset.csv) and returns
    a properly encoded + feature-engineered DataFrame row matching FEATURES order.
    """
    # Work on a copy
    d = dict(raw)

    # ── Feature engineering ───────────────────────────────────────────────────
    # 1. income_to_dept_avg
    dept = d.get("Department", "")
    dept_avg = dept_avg_dict.get(dept, np.mean(list(dept_avg_dict.values())))
    d["income_to_dept_avg"] = round(d["MonthlyIncome"] / dept_avg, 4) if dept_avg > 0 else 1.0

    # 2. promotion_stagnation
    d["promotion_stagnation"] = d["YearsAtCompany"] - d["YearsSinceLastPromotion"]

    # 3. burnout_proxy  (OverTime binary × (4 - WorkLifeBalance))
    ot_bin = 1 if d.get("OverTime", "No") in ("Yes", 1, "1") else 0
    d["burnout_proxy"] = ot_bin * (4 - d["WorkLifeBalance"])

    # 4. total_satisfaction
    sat_cols = ["JobSatisfaction", "EnvironmentSatisfaction",
                "RelationshipSatisfaction", "WorkLifeBalance"]
    d["total_satisfaction"] = round(np.mean([d[c] for c in sat_cols]), 4)

    # ── Encode categoricals ───────────────────────────────────────────────────
    # Binary maps
    d["Gender"]  = 1 if d.get("Gender",  "Male")  == "Male"  else 0
    d["OverTime"] = 1 if d.get("OverTime", "No")   in ("Yes", 1) else 0

    # Ordinal maps
    d["BusinessTravel"] = business_travel_map.get(str(d.get("BusinessTravel", "Non-Travel")), 0)
    d["MaritalStatus"]  = marital_status_map.get(str(d.get("MaritalStatus",  "Single")),     0)

    # Label-encoded multi-category strings
    for col in ["JobRole", "Department", "EducationField"]:
        le = label_encoders[col]
        val = str(d.get(col, le.classes_[0]))
        if val in le.classes_:
            d[col] = int(le.transform([val])[0])
        else:
            d[col] = 0  # fallback to first class if unseen

    # ── Build DataFrame in correct feature order ───────────────────────────────
    row = pd.DataFrame([{f: d[f] for f in FEATURES}])
    return row


def _get_risk_tier(p: float) -> str:
    if p >= 0.70: return "Critical"
    if p >= 0.50: return "High"
    if p >= 0.30: return "Medium"
    return "Low"


def _make_intervention_label(feat: str, cur: float, sug: float) -> str:
    labels = {
        "OverTime":               "Remove overtime requirement",
        "MonthlyIncome":          f"Salary raise: ${cur:,.0f} → ${sug:,.0f}/month"
                                  + (f" (+{(sug/cur-1)*100:.0f}%)" if cur > 0 else ""),
        "YearsSinceLastPromotion":"Promote employee (reset promotion clock to 0)",
        "JobLevel":               f"Promote to Job Level {int(sug)}",
        "WorkLifeBalance":        f"Improve work-life balance: {int(cur)} → {int(sug)}/4",
        "JobSatisfaction":        f"Improve job satisfaction: {int(cur)} → {int(sug)}/4",
        "EnvironmentSatisfaction":f"Improve work environment: {int(cur)} → {int(sug)}/4",
        "StockOptionLevel":       f"Grant stock options (Level {int(cur)} → {int(sug)})",
        "TrainingTimesLastYear":  f"Increase training sessions: {int(cur)} → {int(sug)}/year",
        "DistanceFromHome":       f"Offer remote/hybrid work (commute: {cur:.0f} → {sug:.0f} miles)",
    }
    return labels.get(feat, f"Adjust {feat}: {cur:.2f} → {sug:.2f}")


def _get_scan_values(feat: str, current_val: float) -> list:
    """Return candidate values to perturb a mutable feature to."""
    if MUTABLE_RANGES[feat] is not None:
        # Discrete
        if feat == "OverTime":
            return [0] if current_val > 0 else []
        if feat == "YearsSinceLastPromotion":
            return [v for v in MUTABLE_RANGES[feat] if v < current_val]
        return [v for v in MUTABLE_RANGES[feat] if v > current_val]
    else:
        # Continuous — use sensible fixed steps
        if feat == "MonthlyIncome":
            return [current_val * 1.10, current_val * 1.20, current_val * 1.30]
        if feat == "DistanceFromHome":
            return [v for v in [1] if v < current_val]
    return []


def _run_dice(encoded_row: pd.DataFrame, current_risk: float) -> list:
    """
    Custom single-feature perturbation DiCE engine — mirrors the notebook.
    Returns list of CF dicts grouped by cf_index (1, 2, 3).
    """
    dice_records = []

    # Collect single-feature improvements
    single_changes = []
    for feat in MUTABLE_FEATURES:
        cur_val   = float(encoded_row[feat].iloc[0])
        scan_vals = _get_scan_values(feat, cur_val)
        for try_val in scan_vals:
            perturbed       = encoded_row.copy()
            perturbed[feat] = try_val
            new_risk        = float(xgb_model.predict_proba(perturbed)[0, 1])
            reduction       = current_risk - new_risk
            if reduction > 0.005:
                single_changes.append((reduction, feat, cur_val, try_val, new_risk))

    single_changes.sort(reverse=True)

    # CF 1: best single change
    if single_changes:
        red, feat, cur, sug, new_risk = single_changes[0]
        dice_records.append({
            "cf_index":           1,
            "feature_changed":    feat,
            "feature_label":      FEATURE_LABELS.get(feat, feat),
            "current_value":      round(cur, 4),
            "suggested_value":    round(float(sug), 4),
            "new_attrition_prob": round(new_risk, 4),
            "risk_reduction":     round(red, 4),
            "intervention_label": _make_intervention_label(feat, cur, sug),
        })

    # CF 2: second-best (different feature from CF1)
    best_feat = single_changes[0][1] if single_changes else None
    for red, feat, cur, sug, new_risk in single_changes[1:]:
        if feat != best_feat:
            dice_records.append({
                "cf_index":           2,
                "feature_changed":    feat,
                "feature_label":      FEATURE_LABELS.get(feat, feat),
                "current_value":      round(cur, 4),
                "suggested_value":    round(float(sug), 4),
                "new_attrition_prob": round(new_risk, 4),
                "risk_reduction":     round(red, 4),
                "intervention_label": _make_intervention_label(feat, cur, sug),
            })
            break

    # CF 3: combo of top-2 features applied together
    used = []
    combo = encoded_row.copy()
    for red, feat, cur, sug, _ in single_changes[:6]:
        if feat not in [u[0] for u in used]:
            combo[feat] = sug
            used.append((feat, cur, sug))
        if len(used) == 2:
            break

    if len(used) == 2:
        combo_risk = float(xgb_model.predict_proba(combo)[0, 1])
        for feat, cur, sug in used:
            dice_records.append({
                "cf_index":           3,
                "feature_changed":    feat,
                "feature_label":      FEATURE_LABELS.get(feat, feat),
                "current_value":      round(cur, 4),
                "suggested_value":    round(float(sug), 4),
                "new_attrition_prob": round(combo_risk, 4),
                "risk_reduction":     round(current_risk - combo_risk, 4),
                "intervention_label": _make_intervention_label(feat, cur, sug),
            })

    return dice_records


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_inference(raw_employee: dict) -> dict:
    """
    Full inference pipeline for one raw employee dict.
    Returns a structured result dict ready to be serialised as JSON.
    """
    # 1. Preprocess
    encoded_row = _encode_row(raw_employee)

    # 2. Stage 1 — XGBoost attrition
    attrition_prob = float(xgb_model.predict_proba(encoded_row)[0, 1])
    attrition_pred = int(xgb_model.predict(encoded_row)[0])
    risk_tier      = _get_risk_tier(attrition_prob)

    # 3. Stage 2 — RF reason classifier
    reason_proba_raw  = rf_model.predict_proba(encoded_row)
    reason_pred_label = int(rf_model.predict(encoded_row)[0])

    # Map to full 4-class array safely (RF may not have seen all classes)
    reason_proba_full = np.zeros(4)
    for col_idx, cls_label in enumerate(rf_model.classes_):
        reason_proba_full[int(cls_label)] = reason_proba_raw[0, col_idx]

    primary_reason = REASON_MAP[reason_pred_label] if attrition_pred == 1 else "N/A"

    # 4. SHAP
    shap_values  = explainer.shap_values(encoded_row)
    emp_shap     = shap_values[0]
    sorted_idx   = np.argsort(np.abs(emp_shap))[::-1]

    shap_top5 = []
    for rank in range(5):
        fi      = sorted_idx[rank]
        fname   = FEATURES[fi]
        fval    = float(emp_shap[fi])
        raw_val = float(encoded_row.iloc[0, fi])
        shap_top5.append({
            "rank":          rank + 1,
            "feature":       fname,
            "feature_label": FEATURE_LABELS.get(fname, fname),
            "shap_value":    round(fval, 6),
            "raw_value":     round(raw_val, 4),
            "direction":     "risk" if fval > 0 else "protective",
        })

    # 5. DiCE interventions
    dice_plans = _run_dice(encoded_row, attrition_prob)

    return {
        "employee_number":      raw_employee.get("EmployeeNumber"),
        "attrition_prob":       round(attrition_prob, 4),
        "attrition_pct":        round(attrition_prob * 100, 2),
        "attrition_verdict":    "Yes" if attrition_pred == 1 else "No",
        "risk_tier":            risk_tier,
        "primary_reason":       primary_reason,
        "reason_probs": {
            "Burnout":       round(float(reason_proba_full[0]), 4),
            "Compensation":  round(float(reason_proba_full[1]), 4),
            "Stagnation":    round(float(reason_proba_full[2]), 4),
            "Career Growth": round(float(reason_proba_full[3]), 4),
        },
        "shap_base_value": round(BASE_VALUE, 6),
        "shap_top5":       shap_top5,
        "dice_plans":      dice_plans,
    }
