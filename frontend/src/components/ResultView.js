import React, { useState } from "react";
import HighlightedSQL from "./HighlightedSQL";
import QueryCostBanner from "./QueryCostBanner";
import ExplainTab from "./ExplainTab";
import HistoryTab from "./HistoryTab";
import EmptyState from "./EmptyState";

export default function ResultView({
    sql, results, loading, processingTime, elapsedMs,
    syntaxErrors, queryCost, history,
    explanation, explainLoading, handleExplain,
    onRestoreHistory,
}) {
    const [copied, setCopied] = useState(false);
    const [activeTab, setActiveTab] = useState("results");
    const [isMinified, setIsMinified] = useState(false);
    const [showLineNumbers, setShowLineNumbers] = useState(true);
    const [rowAnimKey, setRowAnimKey] = useState(0);

    const minifySQL = (s) => s.replace(/\s+/g, " ").replace(/\s*([(),])\s*/g, "$1").trim();
    const displaySQL = isMinified ? minifySQL(sql) : sql;

    const handleCopy = () => {
        navigator.clipboard.writeText(displaySQL);
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
    };

    const exportCSV = () => {
        if (!results?.length) return;
        const headers = Object.keys(results[0]).join(",");
        const rows = results.map(r => Object.values(r).map(v => `"${String(v).replace(/"/g, '""')}"`).join(","));
        const blob = new Blob([headers + "\n" + rows.join("\n")], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a"); a.href = url; a.download = "query_results.csv"; a.click();
        URL.revokeObjectURL(url);
    };

    const exportJSON = () => {
        if (!results?.length) return;
        const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a"); a.href = url; a.download = "query_results.json"; a.click();
        URL.revokeObjectURL(url);
    };

    const handleRestoreHistory = (h) => {
        setActiveTab("results");
        setRowAnimKey(k => k + 1);
        setIsMinified(false);
        onRestoreHistory(h);
    };

    // Loading state
    if (loading) {
        return (
            <div className="fade-in" style={{ display: "flex", alignItems: "center", gap: 12, padding: "14px 0" }}>
                <div style={{ display: "flex", gap: 4 }}>
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                </div>
                <span style={{ fontSize: 12, color: "#4a6080" }}>Translating to SQL...</span>
                {elapsedMs > 0 && (
                    <span style={{ fontSize: 11, color: "#3dffc0", background: "rgba(61,255,192,0.06)", border: "1px solid rgba(61,255,192,0.15)", borderRadius: 5, padding: "2px 10px", fontVariantNumeric: "tabular-nums" }}>
                        {(elapsedMs / 1000).toFixed(2)}s
                    </span>
                )}
            </div>
        );
    }

    // Empty state
    if (!sql) return <EmptyState />;

    return (
        <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {/* Query Cost Banner */}
            <QueryCostBanner queryCost={queryCost} />

            {/* SQL Block */}
            <div style={{ background: "#0b0b14", border: `1px solid ${syntaxErrors.length ? "rgba(255,80,80,0.3)" : "#1a2234"}`, borderRadius: 12, overflow: "hidden" }}>
                {/* Toolbar */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "11px 16px", borderBottom: "1px solid #111827", flexWrap: "wrap", gap: 8 }}>
                    <div style={{ display: "flex", gap: 5 }}>
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#ff5f57" }} />
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#ffbd2e" }} />
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#28ca41" }} />
                    </div>
                    <span style={{ fontSize: 10, color: "#3a4a5c", letterSpacing: "0.1em" }}>
                        GENERATED SQL
                        {syntaxErrors.length > 0 && (
                            <span style={{ color: "#ff6060", marginLeft: 8 }}>· {syntaxErrors.length} issue{syntaxErrors.length > 1 ? "s" : ""} detected</span>
                        )}
                    </span>

                    {/* Controls */}
                    <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap" }}>
                        {processingTime !== null && (
                            <span style={{ fontSize: 10, color: "#3dffc0", background: "rgba(61,255,192,0.07)", border: "1px solid rgba(61,255,192,0.18)", borderRadius: 5, padding: "2px 9px" }}>
                                ⏱ {processingTime < 1000 ? `${processingTime}ms` : `${(processingTime / 1000).toFixed(2)}s`}
                            </span>
                        )}
                        <button
                            onClick={() => setShowLineNumbers(v => !v)}
                            style={{
                                background: showLineNumbers ? "rgba(61,255,192,0.07)" : "#111827",
                                border: `1px solid ${showLineNumbers ? "rgba(61,255,192,0.25)" : "#1e2d40"}`,
                                color: showLineNumbers ? "#3dffc0" : "#4a6080",
                                borderRadius: 6, padding: "4px 10px", cursor: "pointer",
                                fontFamily: "inherit", fontSize: 10, transition: "all 0.15s", letterSpacing: "0.04em"
                            }}
                        ># Lines</button>
                        <button
                            onClick={() => setIsMinified(v => !v)}
                            style={{
                                background: isMinified ? "rgba(126,184,255,0.08)" : "#111827",
                                border: `1px solid ${isMinified ? "rgba(126,184,255,0.25)" : "#1e2d40"}`,
                                color: isMinified ? "#7eb8ff" : "#4a6080",
                                borderRadius: 6, padding: "4px 10px", cursor: "pointer",
                                fontFamily: "inherit", fontSize: 10, transition: "all 0.15s", letterSpacing: "0.04em"
                            }}
                        >{isMinified ? "⇥ Format" : "⇤ Minify"}</button>
                        <button className="copy-btn" onClick={handleCopy}>{copied ? "✓ Copied" : "Copy"}</button>
                    </div>
                </div>

                {/* SQL content */}
                <div className="sql-block" style={{ background: "#050509", padding: "20px 12px" }}>
                    <HighlightedSQL
                        sql={displaySQL}
                        errorLines={isMinified ? [] : syntaxErrors}
                        showLineNumbers={showLineNumbers && !isMinified}
                    />
                </div>
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #111827" }}>
                <div style={{ display: "flex" }}>
                    {[
                        { id: "results", label: "Results" },
                        { id: "explain", label: "✦ Explain" },
                        { id: "history", label: `History${history.length > 0 ? ` (${history.length})` : ""}` },
                    ].map(({ id, label }) => (
                        <button key={id} className="tab-btn"
                            onClick={() => { setActiveTab(id); if (id === "explain" && !explanation && !explainLoading) handleExplain(); }}
                            style={{
                                color: activeTab === id ? (id === "explain" ? "#a78bfa" : "#3dffc0") : "#3a4a5c",
                                borderBottom: activeTab === id ? `2px solid ${id === "explain" ? "#a78bfa" : "#3dffc0"}` : "2px solid transparent",
                            }}>{label}</button>
                    ))}
                </div>
                {activeTab !== "explain" && (
                    <button className="explain-btn" onClick={() => { setActiveTab("explain"); if (!explanation && !explainLoading) handleExplain(); }}>
                        ✦ Explain SQL
                    </button>
                )}
            </div>

            {/* Results Tab */}
            {activeTab === "results" && results && results.length > 0 && (
                <div className="fade-in table-container">
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, fontFamily: "inherit" }}>
                            <thead>
                                <tr style={{ borderBottom: "1px solid #1a2234" }}>
                                    {Object.keys(results[0]).map(k => (
                                        <th key={k} style={{ padding: "11px 16px", textAlign: "left", color: "#3dffc0", fontWeight: 500, letterSpacing: "0.08em", textTransform: "uppercase", fontSize: 9 }}>{k}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((row, i) => (
                                    <tr key={`${rowAnimKey}-${i}`} className="result-row anim-row" style={{ animationDelay: `${i * 60}ms` }}>
                                        {Object.values(row).map((v, j) => (
                                            <td key={j} style={{ padding: "9px 16px", color: "#94a3b8", borderBottom: "1px solid #0f1520" }}>{String(v)}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div style={{ padding: "9px 16px", fontSize: 10, color: "#2d3f58", borderTop: "1px solid #0f1520", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
                        <div style={{ display: "flex", gap: 14 }}>
                            <span>{results.length} rows returned</span>
                            {processingTime !== null && <span>· processed in <span style={{ color: "#3dffc0" }}>{processingTime < 1000 ? `${processingTime}ms` : `${(processingTime / 1000).toFixed(2)}s`}</span></span>}
                        </div>
                        <div style={{ display: "flex", gap: 7 }}>
                            <button className="export-btn" onClick={exportCSV}>↓ CSV</button>
                            <button className="export-btn" onClick={exportJSON}>↓ JSON</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Explain Tab */}
            {activeTab === "explain" && (
                <ExplainTab explanation={explanation} explainLoading={explainLoading} />
            )}

            {/* History Tab */}
            {activeTab === "history" && (
                <HistoryTab history={history} onRestore={handleRestoreHistory} />
            )}
        </div>
    );
}
