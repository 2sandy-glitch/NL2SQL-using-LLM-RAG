import React, { useState } from "react";

export default function ResultView({ sql, results, loading }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
    };

    if (loading) {
        return (
            <div className="fade-in" style={{ display: "flex", alignItems: "center", gap: 12, padding: "14px 0" }}>
                <div style={{ display: "flex", gap: 4 }}>
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                    <span className="loader-dot" style={{ background: "#3dffc0" }} />
                </div>
                <span style={{ fontSize: 12, color: "#4a6080" }}>Translating to SQL...</span>
            </div>
        );
    }

    if (!sql) return null;

    return (
        <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            {/* SQL Block */}
            <div className="sql-container">
                <div style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "11px 16px",
                    borderBottom: "1px solid #111827",
                }}>
                    <div style={{ display: "flex", gap: 5 }}>
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#ff5f57" }} />
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#ffbd2e" }} />
                        <div style={{ width: 9, height: 9, borderRadius: "50%", background: "#28ca41" }} />
                    </div>
                    <span style={{ fontSize: 10, color: "#3a4a5c", letterSpacing: "0.1em" }}>GENERATED SQL</span>
                    <button className="copy-btn" onClick={handleCopy}>
                        {copied ? "✓ Copied" : "Copy"}
                    </button>
                </div>

                <div style={{
                    background: "#050509",
                    padding: "20px",
                    fontFamily: "'IBM Plex Mono','Fira Code',monospace",
                    fontSize: 13,
                    lineHeight: 1.8,
                    overflowX: "auto",
                    whiteSpace: "pre",
                    color: "#e2e8f0",
                }}>
                    {sql}
                </div>
            </div>

            {/* Results Table */}
            {results && results.length > 0 && (
                <div className="table-container">
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, fontFamily: "inherit" }}>
                            <thead>
                                <tr style={{ borderBottom: "1px solid #1a2234" }}>
                                    {Object.keys(results[0]).map(k => (
                                        <th key={k} style={{
                                            padding: "11px 16px",
                                            textAlign: "left",
                                            color: "#3dffc0",
                                            fontWeight: 500,
                                            letterSpacing: "0.08em",
                                            textTransform: "uppercase",
                                            fontSize: 9,
                                        }}>{k}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((row, i) => (
                                    <tr key={i} className="result-row">
                                        {Object.values(row).map((v, j) => (
                                            <td key={j} style={{
                                                padding: "9px 16px",
                                                color: "#94a3b8",
                                                borderBottom: "1px solid #0f1520",
                                            }}>{String(v)}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div style={{
                        padding: "9px 16px",
                        fontSize: 10,
                        color: "#2d3f58",
                        borderTop: "1px solid #0f1520",
                    }}>
                        {results.length} rows returned
                    </div>
                </div>
            )}
        </div>
    );
}
