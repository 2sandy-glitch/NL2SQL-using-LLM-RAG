import React from "react";

export default function ChatBox({ input, setInput, handleConvert, loading, suggestions, setShowSuggestions, showSuggestions }) {
    const handleSuggestion = (s) => {
        setInput(s);
        setShowSuggestions(false);
        handleConvert(s);
    };

    return (
        <>
            <div className="input-area" style={{ padding: "16px 18px" }}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 12 }}>
                    <span style={{ color: "#3dffc0", fontSize: 12, paddingTop: 3, flexShrink: 0 }}>❯</span>
                    <textarea
                        rows={3}
                        placeholder="Describe what data you need in plain English..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleConvert(); }}
                        onFocus={() => setShowSuggestions(true)}
                    />
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 10, color: "#2d3f58" }}>⌘ + Enter to convert</span>
                    <button
                        className="convert-btn"
                        onClick={() => handleConvert()}
                        disabled={loading || !input.trim()}
                    >
                        {loading ? "Converting..." : "Convert →"}
                    </button>
                </div>
            </div>

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
