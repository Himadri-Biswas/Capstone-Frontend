import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, Calendar, ChevronDown, Filter, TrendingUp, Users } from "lucide-react";
import Button from "../../components/ui/Button.jsx";
import Pill from "../../components/ui/Pill.jsx";
import SoftTag from "../../components/ui/SoftTag.jsx";
import { cx } from "../../lib/cx.js";

function EmployeesView({ employees, search, setSearch }) {
  const [dept, setDept] = useState("All Department");
  const [risk, setRisk] = useState("All Risk");
  const [mode, setMode] = useState("All Mode");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);
  

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return employees.filter((e) => {
      const qOk = !q || `${e.name} ${e.role} ${e.email}`.toLowerCase().includes(q);
      const dOk = dept === "All Department" || e.dept === dept;
      const rOk = risk === "All Risk" || e.risk === risk;
      const mOk = mode === "All Mode" || e.workMode === mode;
      return qOk && dOk && rOk && mOk;
    });
  }, [employees, search, dept, risk, mode]);

  useEffect(() => {
    if (selectedEmployeeId && !filtered.find((x) => x.id === selectedEmployeeId)) {
      setSelectedEmployeeId(null);
    }
  }, [filtered, selectedEmployeeId]);

  const selectedEmployee = filtered.find((x) => x.id === selectedEmployeeId) || null;

  const deptPill = (d) => {
    const map = {
      Engineering: "text-blue-700 bg-blue-50 border-blue-200",
      Marketing: "text-pink-700 bg-pink-50 border-pink-200",
      HR: "text-violet-700 bg-violet-50 border-violet-200",
      Sales: "text-emerald-700 bg-emerald-50 border-emerald-200",
      Design: "text-rose-700 bg-rose-50 border-rose-200",
      Software: "text-indigo-700 bg-indigo-50 border-indigo-200",
      Data: "text-sky-700 bg-sky-50 border-sky-200",
      AI: "text-fuchsia-700 bg-fuchsia-50 border-fuchsia-200",
          };
    return map[d] || "text-slate-700 bg-slate-50 border-slate-200";
  };

  const riskMeta = (r) => {
    if (r === "High")
      return {
        label: "High",
        pct: 85,
        header: "bg-rose-600",
        soft: "bg-rose-50 border-rose-200 text-rose-700",
      };
    if (r === "Medium")
      return {
        label: "Medium",
        pct: 55,
        header: "bg-amber-500",
        soft: "bg-amber-50 border-amber-200 text-amber-700",
      };
    return {
      label: "Low",
      pct: 25,
      header: "bg-emerald-600",
      soft: "bg-emerald-50 border-emerald-200 text-emerald-700",
    };
  };

  // UI-friendly summary (derived from the Module 3 approach: risk score + top drivers + interventions)
  const insightsByRisk = {
    High: {
      baseline: 16,
      drivers: [
        { label: "Overtime workload", value: "+25%" },
        { label: "Promotion delay", value: "+19%" },
        { label: "Below dept pay", value: "+14%" },
      ],
      interventions: [
        { title: "Reduce overtime", detail: "Rebalance workload and remove overtime", tag: "No-cost", right: "Expected risk: 42%" },
        { title: "Career advancement", detail: "Promotion + small salary adjustment", tag: "High impact", right: "Expected risk: 31%" },
      ],
    },
    Medium: {
      baseline: 16,
      drivers: [
        { label: "Frequent travel", value: "+12%" },
        { label: "Overtime workload", value: "+10%" },
        { label: "Work-life balance", value: "+8%" },
      ],
      interventions: [
        { title: "Flexible schedule", detail: "Add 2 WFH days + meeting-free blocks", tag: "Quick", right: "Expected risk: 38%" },
        { title: "Compensation tune-up", detail: "Align pay to dept average", tag: "Moderate", right: "Expected risk: 30%" },
      ],
    },
    Low: {
      baseline: 16,
      drivers: [
        { label: "Stable role tenure", value: "-6%" },
        { label: "Good work-life balance", value: "-5%" },
        { label: "Above-average performance", value: "-4%" },
      ],
      interventions: [
        { title: "Maintain engagement", detail: "Regular 1:1s + growth plan", tag: "Preventive", right: "Expected risk: 18%" },
        { title: "Recognition", detail: "Spot bonus / public recognition", tag: "Light", right: "Expected risk: 16%" },
      ],
    },
  };

  const EmployeeCard = ({ e }) => {
    return (
      <button
        onClick={() => setSelectedEmployeeId(e.id)}
        className="text-left rounded-3xl border border-slate-200 bg-white p-4 shadow-sm transition hover:bg-slate-50"
      >
        <div className="flex items-start gap-3">
          <div className="h-14 w-14 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white font-bold">
            {e.initials}
          </div>
          <div className="flex-1">
            <div className="text-lg font-bold text-slate-900">{e.name}</div>
            <div className="text-sm text-slate-500">{e.role}</div>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className={cx("inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm", deptPill(e.dept))}>
                <span className="h-2 w-2 rounded-full bg-current opacity-60" />
                {e.dept}
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm text-slate-600">
                <Calendar className="h-4 w-4" /> {e.joined}
              </span>
              <span className={cx("inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm", riskMeta(e.risk).soft)}>
                <AlertTriangle className="h-4 w-4" /> {riskMeta(e.risk).label}
              </span>
            </div>
          </div>
        </div>
      </button>
    );
  };

  const InfoRow = ({ label, value }) => (
    <div className="flex items-center justify-between gap-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-sm font-semibold text-slate-900 text-right">{value}</div>
    </div>
  );

  return (
    <div className="rounded-[28px] overflow-hidden border border-slate-200 bg-white shadow-sm">
      <div className="bg-gradient-to-b from-white to-slate-50 p-6">
        {!selectedEmployee ? (
          <>
            {/* Controls (use the TOPBAR search only - no duplicate search here) */}
            <div className="rounded-3xl border border-slate-200 bg-white p-3 shadow-sm">
              <div className="flex flex-wrap items-center justify-start gap-3">
                <button
                  className="inline-flex min-w-[160px] items-center justify-between gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  onClick={() => setDept((d) => (d === "All Department" ? "Engineering" : "All Department"))}
                  title="Demo toggle"
                >
                  <Filter className="h-4 w-4 text-slate-500" />
                  {dept}
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </button>

                <button
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  onClick={() => setRisk((r) => (r === "All Risk" ? "High" : "All Risk"))}
                  title="Demo toggle"
                >
                  <TrendingUp className="h-4 w-4 text-slate-500" />
                  {risk}
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </button>

                <button
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  onClick={() => setMode((m) => (m === "All Mode" ? "Remote" : "All Mode"))}
                  title="Demo toggle"
                >
                  <Users className="h-4 w-4 text-slate-500" />
                  {mode}
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </button>
              </div>
            </div>

            <div className="mt-6">
              <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {filtered.map((e) => (
                  <EmployeeCard key={e.id} e={e} />
                ))}
              </div>
            </div>
          </>
        ) : (
          (() => {
            const rm = riskMeta(selectedEmployee.risk);
            const insights = insightsByRisk[selectedEmployee.risk] || insightsByRisk.Low;

            return (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setSelectedEmployeeId(null)}
                    className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    <ArrowRight className="h-4 w-4 rotate-180" /> Back
                  </button>
                </div>

                {/* No reserved space: selected profile becomes the whole page */}
                <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
                  {/* LEFT: profile + details */}
                  <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="h-20 w-20 rounded-3xl bg-gradient-to-br from-indigo-200 to-sky-200 border border-slate-200" />
                      <div className="flex-1">
                        <div className="text-2xl font-bold text-slate-900">{selectedEmployee.name}</div>
                        <div className="text-sm text-slate-500 mt-1">{selectedEmployee.role}</div>
                        <div className="text-xs text-slate-500 mt-2">{selectedEmployee.email}</div>

                        <div className="mt-4 flex flex-wrap gap-2">
                          <span className={cx("inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm", deptPill(selectedEmployee.dept))}>
                            <span className="h-2 w-2 rounded-full bg-current opacity-60" />
                            {selectedEmployee.dept}
                          </span>
                          <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm text-slate-700">
                            <Calendar className="h-4 w-4" /> {selectedEmployee.joined}
                          </span>
                          <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm text-slate-700">
                            {selectedEmployee.workMode}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 space-y-3">
                      <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Employee info</div>
                      <InfoRow label="Location" value={selectedEmployee.location} />
                      <InfoRow label="Manager" value={selectedEmployee.manager} />
                      <InfoRow label="Monthly income" value={`$${selectedEmployee.monthlyIncome.toLocaleString()}`} />
                      <InfoRow label="Tenure" value={`${selectedEmployee.yearsAtCompany} years`} />
                      <InfoRow label="Last promotion" value={selectedEmployee.lastPromotion} />
                      <InfoRow label="Overtime" value={selectedEmployee.overtime} />
                    </div>

                    <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-4">
                      <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Skills</div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {selectedEmployee.skills.map((s) => (
                          <SoftTag key={s}>{s}</SoftTag>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* RIGHT: risk + insights + interventions (no SHAP/DiCE wording) */}
                  <div className="space-y-4">
                    <div className={cx("rounded-3xl p-5 text-white shadow-sm", rm.header)}>
                      <div className="text-sm opacity-90">Attrition Risk</div>
                      <div className="mt-1 text-3xl font-extrabold tracking-tight">
                        {rm.label} ({rm.pct}%)
                      </div>
                      <div className="mt-2 text-sm text-white/90">Company baseline: {insights.baseline}%</div>
                      <div className="mt-4 h-2 rounded-full bg-white/30 overflow-hidden">
                        <div className="h-full rounded-full bg-white" style={{ width: `${rm.pct}%` }} />
                      </div>
                    </div>

                    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                      <div className="text-lg font-bold text-slate-900">Key reasons</div>
                      <div className="text-sm text-slate-600 mt-2">Top factors contributing to the current risk score.</div>
                      <div className="mt-4 space-y-3">
                        {insights.drivers.map((d) => (
                          <div key={d.label} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                            <div className="text-sm font-semibold text-slate-900">{d.label}</div>
                            <div className={cx(
                              "text-sm font-mono",
                              String(d.value).startsWith("+") ? "text-rose-700" : "text-emerald-700"
                            )}>
                              {d.value}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                      <div className="text-lg font-bold text-slate-900">Intervention options</div>
                      <div className="mt-4 space-y-3">
                        {insights.interventions.map((opt, idx) => (
                          <div key={idx} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <div className="text-sm font-semibold text-slate-900">{opt.title}</div>
                                <div className="text-sm text-slate-600 mt-1">{opt.detail}</div>
                                <div className="mt-2">
                                  <Pill className="bg-indigo-50 text-indigo-700 border border-indigo-200">{opt.tag}</Pill>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-xs text-slate-500">{opt.right}</div>
                                <Button className="mt-2 rounded-2xl bg-indigo-600 hover:bg-indigo-700">Apply</Button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                  </div>
                </div>
              </div>
            );
          })()
        )}
      </div>
    </div>

  );
}

export default EmployeesView;
