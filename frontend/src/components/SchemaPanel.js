import React, { useRef } from "react";

export default function SchemaPanel({ schemaOpen, schemaText, setSchemaText, parsedSchema, schemaLoaded }) {
    const schemaFileRef = useRef(null);

    const handleSchemaFile = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => setSchemaText(ev.target.result);
        reader.readAsText(file);
    };

    return (
        <div className="schema-panel-wrap" style={{ maxWidth: schemaOpen ? 300 : 0, opacity: schemaOpen ? 1 : 0, flexShrink: 0 }}>
            <div style={{ width: 300, paddingRight: 4 }}>
                <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span>Database Schema</span>
                    <button onClick={() => schemaFileRef.current?.click()} style={{ background: "none", border: "none", color: "#3dffc0", cursor: "pointer", fontSize: 10, fontFamily: "inherit", letterSpacing: "0.05em" }}>↑ Upload .sql</button>
                    <input ref={schemaFileRef} type="file" accept=".sql,.txt" style={{ display: "none" }} onChange={handleSchemaFile} />
                </div>

                {schemaLoaded && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 }}>
                        {Object.entries(parsedSchema).map(([table, cols]) => (
                            <div key={table} style={{ background: "#0c0c18", border: "1px solid #1a2234", borderRadius: 8, padding: "8px 12px" }}>
                                <div style={{ fontSize: 11, color: "#3dffc0", marginBottom: 5, display: "flex", alignItems: "center", gap: 5 }}>
                                    <span style={{ opacity: 0.5 }}>▤</span> {table}
                                </div>
                                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                                    {cols.map(col => (
                                        <span key={col.name} style={{ fontSize: 9, background: "#101828", border: "1px solid #1e2d40", borderRadius: 3, padding: "1px 6px", color: "#64748b" }}>
                                            {col.name} <span style={{ color: "#2d3f58" }}>{col.type}</span>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <div style={{ background: "#09090f", border: "1px solid #1a2234", borderRadius: 10, overflow: "hidden" }}>
                    <div style={{ padding: "9px 14px", borderBottom: "1px solid #111827", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.1em", textTransform: "uppercase" }}>Schema Editor</span>
                        {schemaLoaded && <span style={{ fontSize: 9, color: "#3dffc0" }}>● Parsed</span>}
                    </div>
                    <textarea
                        value={schemaText}
                        onChange={(e) => setSchemaText(e.target.value)}
                        placeholder="Paste CREATE TABLE statements..."
                        spellCheck={false}
                        style={{ padding: "14px 16px", fontSize: 11, color: "#64748b", minHeight: 220, lineHeight: 1.7 }}
                    />
                </div>
            </div>
        </div>
    );
}
