import React from "react";

export default function HistoryTab({ history, onRestore }) {
    if (history.length === 0) {
        return (
            <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                <div style={{ color: "#3a4a5c", fontSize: 12, padding: "16px 0" }}>No history yet.</div>
            </div>
        );
    }

    return (
        <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {history.map((h, i) => (
                <div key={i} className="history-item" onClick={() => onRestore(h)}>
                    <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 3 }}>{h.query}</div>
                    <div style={{ fontSize: 10, color: "#2d3f58", display: "flex", gap: 10 }}>
                        <span>{h.time.toLocaleTimeString()}</span>
                        {h.processingTime && <span>⏱ {h.processingTime < 1000 ? `${h.processingTime}ms` : `${(h.processingTime / 1000).toFixed(2)}s`}</span>}
                    </div>
                </div>
            ))}
        </div>
    );
}
