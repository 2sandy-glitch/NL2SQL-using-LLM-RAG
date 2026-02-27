import React from "react";

export default function QueryCostBanner({ queryCost }) {
    if (!queryCost || queryCost.level === "light") return null;

    return (
        <div style={{
            display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 16px",
            background: queryCost.level === "heavy" ? "rgba(255,100,60,0.07)" : "rgba(255,180,50,0.06)",
            border: `1px solid ${queryCost.level === "heavy" ? "rgba(255,100,60,0.25)" : "rgba(255,180,50,0.2)"}`,
            borderRadius: 9
        }}>
            <span style={{ fontSize: 15, lineHeight: 1 }}>{queryCost.level === "heavy" ? "⚠" : "◈"}</span>
            <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: queryCost.level === "heavy" ? "#ff9060" : "#ffb432", fontWeight: 600, marginBottom: 4, letterSpacing: "0.04em" }}>
                    {queryCost.level === "heavy" ? "Heavy Query" : "Moderate Cost"} · Est. {queryCost.estRows} rows scanned
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {queryCost.warnings.map((w, i) => (
                        <span key={i} style={{
                            fontSize: 10, background: "rgba(255,150,60,0.08)", border: "1px solid rgba(255,150,60,0.15)",
                            borderRadius: 4, padding: "1px 8px", color: "#c08050"
                        }}>{w}</span>
                    ))}
                </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <div style={{ width: 56, height: 5, background: "#111827", borderRadius: 3, overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${Math.min(queryCost.score, 100)}%`, background: queryCost.level === "heavy" ? "#ff6432" : "#ffb432", borderRadius: 3, transition: "width 0.5s" }} />
                </div>
                <span style={{ fontSize: 9, color: "#3a4a5c" }}>{queryCost.score}/100</span>
            </div>
        </div>
    );
}
