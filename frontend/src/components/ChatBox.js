import React, { useState, useRef } from "react";

export default function ChatBox({
    input, setInput, handleConvert, loading,
    suggestions, setShowSuggestions, showSuggestions,
    schemaLoaded, parsedSchema, schemaOpen, setSchemaOpen,
}) {
    const [autocomplete, setAutocomplete] = useState([]);
    const [acIndex, setAcIndex] = useState(0);
    const [cursorPos, setCursorPos] = useState(0);
    const textareaRef = useRef(null);

    const handleSuggestion = (s) => {
        setInput(s);
        setShowSuggestions(false);
        handleConvert(s);
    };

    const handleInputChange = (e) => {
        const val = e.target.value;
        const pos = e.target.selectionStart;
        setInput(val);
        setCursorPos(pos);

        if (!schemaLoaded) { setAutocomplete([]); return; }
        const textBefore = val.slice(0, pos);
        const wordMatch = textBefore.match(/(\w+)$/);
        const currentWord = wordMatch ? wordMatch[1].toLowerCase() : "";
        if (currentWord.length < 2) { setAutocomplete([]); return; }

        const acSuggestions = [];
        for (const [table, cols] of Object.entries(parsedSchema)) {
            if (table.toLowerCase().startsWith(currentWord))
                acSuggestions.push({ label: table, type: "table", detail: `${cols.length} columns` });
            for (const col of cols) {
                if (col.name.toLowerCase().startsWith(currentWord))
                    acSuggestions.push({ label: col.name, type: "column", detail: `${table}.${col.name} · ${col.type}` });
            }
        }
        setAutocomplete(acSuggestions.slice(0, 6));
        setAcIndex(0);
    };

    const applyAutocomplete = (suggestion) => {
        const textBefore = input.slice(0, cursorPos);
        const textAfter = input.slice(cursorPos);
        const wordMatch = textBefore.match(/(\w+)$/);
        if (!wordMatch) return;
        const newBefore = textBefore.slice(0, textBefore.length - wordMatch[1].length) + suggestion.label;
        setInput(newBefore + textAfter);
        setAutocomplete([]);
        textareaRef.current?.focus();
    };

    const handleKeyDown = (e) => {
        if (autocomplete.length > 0) {
            if (e.key === "ArrowDown") { e.preventDefault(); setAcIndex(i => Math.min(i + 1, autocomplete.length - 1)); return; }
            if (e.key === "ArrowUp") { e.preventDefault(); setAcIndex(i => Math.max(i - 1, 0)); return; }
            if (e.key === "Tab" || (e.key === "Enter" && autocomplete.length > 0)) { e.preventDefault(); applyAutocomplete(autocomplete[acIndex]); return; }
            if (e.key === "Escape") { setAutocomplete([]); return; }
        }
        if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleConvert();
    };

    return (
        <>
            {/* Input Row */}
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <button
                    className={`schema-btn${schemaOpen ? " active" : ""}`}
                    onClick={() => setSchemaOpen(o => !o)}
                >
                    ▤ Schema{schemaLoaded ? ` (${Object.keys(parsedSchema).length})` : ""}
                </button>

                <div className="input-area" style={{ flex: 1, padding: "16px 18px", position: "relative" }}>
                    <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 12 }}>
                        <span style={{ color: "#3dffc0", fontSize: 12, paddingTop: 3, flexShrink: 0 }}>❯</span>
                        <textarea
                            ref={textareaRef}
                            rows={3}
                            placeholder={schemaLoaded ? "Type to autocomplete table/column names..." : "Describe what data you need in plain English..."}
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setShowSuggestions(true)}
                            onBlur={() => setTimeout(() => setAutocomplete([]), 160)}
                        />
                    </div>

                    {autocomplete.length > 0 && (
                        <div className="ac-dropdown">
                            {autocomplete.map((item, i) => (
                                <div key={item.label + i} className={`ac-item${i === acIndex ? " active" : ""}`} onMouseDown={() => applyAutocomplete(item)}>
                                    <span style={{ color: item.type === "table" ? "#3dffc0" : "#e2e8f0" }}>{item.label}</span>
                                    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                                        <span style={{ fontSize: 10, color: "#3a4a5c" }}>{item.detail}</span>
                                        <span className="ac-badge" style={{
                                            background: item.type === "table" ? "rgba(61,255,192,0.1)" : "rgba(126,184,255,0.1)",
                                            color: item.type === "table" ? "#3dffc0" : "#7eb8ff",
                                            border: `1px solid ${item.type === "table" ? "rgba(61,255,192,0.2)" : "rgba(126,184,255,0.2)"}`,
                                        }}>{item.type}</span>
                                    </div>
                                </div>
                            ))}
                            <div style={{ padding: "5px 14px", fontSize: 9, color: "#2d3f58", borderTop: "1px solid #111827" }}>Tab to complete · Esc to close</div>
                        </div>
                    )}

                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ fontSize: 10, color: "#2d3f58" }}>⌘ + Enter to convert</span>
                        <button className="convert-btn" onClick={() => handleConvert()} disabled={loading || !input.trim()}>
                            {loading ? "Converting..." : "Convert →"}
                        </button>
                    </div>
                </div>
            </div>

            {/* Suggestions */}
            {showSuggestions && (
                <div className="fade-in">
                    <div style={{
                        fontSize: 9, color: "#3a4a5c",
                        letterSpacing: "0.12em",
                        textTransform: "uppercase",
                        marginBottom: 8,
                        marginTop: 18
                    }}>Try an example</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
                        {suggestions.map(s => (
                            <button key={s} className="suggestion-chip" onClick={() => handleSuggestion(s)}>{s}</button>
                        ))}
                    </div>
                </div>
            )}
        </>
    );
}
