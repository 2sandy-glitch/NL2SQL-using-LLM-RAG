import React from "react";
import { renderTokens } from "../utils/sqlUtils";

export default function HighlightedSQL({ sql, errorLines = [], showLineNumbers = true }) {
    const lines = sql.split("\n");
    return (
        <div style={{ fontFamily: "'IBM Plex Mono','Fira Code',monospace", fontSize: 13, lineHeight: 1.8, overflowX: "auto", whiteSpace: "pre" }}>
            {lines.map((line, i) => {
                const hasError = errorLines.includes(i);
                return (
                    <div key={i} style={{
                        display: "flex",
                        background: hasError ? "rgba(255,80,80,0.06)" : "transparent",
                        borderLeft: hasError ? "2px solid #ff5050" : "2px solid transparent",
                    }}>
                        {showLineNumbers && (
                            <span style={{
                                userSelect: "none",
                                width: 36,
                                textAlign: "right",
                                paddingRight: 14,
                                color: hasError ? "#ff5050" : "#2a3a50",
                                fontSize: 11,
                                flexShrink: 0,
                                lineHeight: 1.8,
                            }}>{i + 1}</span>
                        )}
                        <span style={{ flex: 1 }}>
                            {renderTokens(line, hasError, React)}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}
