import React from "react";

export default function ExplainTab({ explanation, explainLoading }) {
    if (explainLoading) {
        return (
            <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ padding: "8px 0" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                        <div style={{ display: "flex", gap: 4 }}>
                            <span className="loader-dot" style={{ background: "#a78bfa" }} />
                            <span className="loader-dot" style={{ background: "#a78bfa" }} />
                            <span className="loader-dot" style={{ background: "#a78bfa" }} />
                        </div>
                        <span style={{ fontSize: 12, color: "#6d4faa" }}>Analyzing SQL with AI...</span>
                    </div>
                    {[100, 75, 88, 60, 90].map((w, i) => <div key={i} className="skeleton" style={{ width: `${w}%` }} />)}
                </div>
            </div>
        );
    }

    if (explanation?.error) {
        return (
            <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ color: "#ff6b6b", fontSize: 13 }}>{explanation.error}</div>
            </div>
        );
    }

    if (!explanation) return null;

    return (
        <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ background: "rgba(123,97,255,0.07)", border: "1px solid rgba(123,97,255,0.18)", borderRadius: 10, padding: "14px 18px" }}>
                <div style={{ fontSize: 9, color: "#7c5fcc", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 7 }}>What this query does</div>
                <div style={{ fontSize: 13, color: "#c4b5fd", lineHeight: 1.65 }}>{explanation.summary}</div>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
                <div style={{ background: "#0c0c18", border: "1px solid #1a2234", borderRadius: 8, padding: "10px 14px", minWidth: 100 }}>
                    <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 5 }}>Complexity</div>
                    <span style={{ fontSize: 13, fontWeight: 600, color: explanation.complexity === "Simple" ? "#3dffc0" : explanation.complexity === "Moderate" ? "#ffd787" : "#ff9e87" }}>
                        {explanation.complexity}
                    </span>
                </div>
                <div style={{ background: "#0c0c18", border: "1px solid #1a2234", borderRadius: 8, padding: "10px 14px", flex: 1 }}>
                    <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>Tables Used</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                        {(explanation.tables_used || []).map(t => (
                            <span key={t} style={{ fontSize: 10, background: "rgba(61,255,192,0.06)", border: "1px solid rgba(61,255,192,0.14)", borderRadius: 4, padding: "2px 8px", color: "#3dffc0" }}>{t}</span>
                        ))}
                    </div>
                </div>
            </div>
            <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 2 }}>Clause Breakdown</div>
            {(explanation.clauses || []).map((c, i) => (
                <div key={i} className="clause-card">
                    <div style={{ fontSize: 11, color: "#7eb8ff", marginBottom: 5, letterSpacing: "0.03em" }}>
                        {c.clause.length > 70 ? c.clause.slice(0, 70) + "…" : c.clause}
                    </div>
                    <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{c.explanation}</div>
                </div>
            ))}
        </div>
    );
}
