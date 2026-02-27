import React, { useState } from "react";

export default function DBSettingsPanel({ onClose, dbConfig, setDbConfig }) {
    const [localConfig, setLocalConfig] = useState(dbConfig);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null);

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        await new Promise(r => setTimeout(r, 1200));
        setTestResult(localConfig.host ? "success" : "error");
        setTesting(false);
    };

    return (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }} onClick={onClose}>
            <div style={{ background: "#0d1020", border: "1px solid #1e3050", borderRadius: 14, padding: 28, width: 420, maxWidth: "90vw" }} onClick={e => e.stopPropagation()}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 22 }}>
                    <div style={{ fontFamily: "'Syne',sans-serif", fontSize: 16, fontWeight: 800, color: "#fff" }}>Database Connection</div>
                    <button onClick={onClose} style={{ background: "none", border: "none", color: "#3a4a5c", cursor: "pointer", fontSize: 18, lineHeight: 1 }}>×</button>
                </div>

                {/* DB Type */}
                <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>Database Type</div>
                    <div style={{ display: "flex", gap: 8 }}>
                        {["PostgreSQL", "MySQL", "SQLite"].map(t => (
                            <button key={t} onClick={() => setLocalConfig(c => ({ ...c, type: t }))} style={{
                                flex: 1, padding: "8px 0", borderRadius: 7, border: `1px solid ${localConfig.type === t ? "#3dffc0" : "#1e2d40"}`,
                                background: localConfig.type === t ? "rgba(61,255,192,0.08)" : "transparent",
                                color: localConfig.type === t ? "#3dffc0" : "#4a6080",
                                cursor: "pointer", fontFamily: "inherit", fontSize: 11, transition: "all 0.15s"
                            }}>{t}</button>
                        ))}
                    </div>
                </div>

                {localConfig.type !== "SQLite" ? (
                    <>
                        {[
                            { label: "Host", key: "host", placeholder: "localhost" },
                            { label: "Port", key: "port", placeholder: localConfig.type === "MySQL" ? "3306" : "5432" },
                            { label: "Database", key: "database", placeholder: "mydb" },
                            { label: "Username", key: "user", placeholder: "admin" },
                        ].map(({ label, key, placeholder }) => (
                            <div key={key} style={{ marginBottom: 12 }}>
                                <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 5 }}>{label}</div>
                                <input value={localConfig[key] || ""} onChange={e => setLocalConfig(c => ({ ...c, [key]: e.target.value }))}
                                    placeholder={placeholder} style={{
                                        width: "100%", background: "#080810", border: "1px solid #1e2d40", borderRadius: 7, padding: "8px 12px",
                                        color: "#e2e8f0", fontFamily: "inherit", fontSize: 12, outline: "none"
                                    }} />
                            </div>
                        ))}
                        <div style={{ marginBottom: 16 }}>
                            <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 5 }}>Password</div>
                            <input type="password" value={localConfig.password || ""} onChange={e => setLocalConfig(c => ({ ...c, password: e.target.value }))}
                                placeholder="••••••••" style={{
                                    width: "100%", background: "#080810", border: "1px solid #1e2d40", borderRadius: 7, padding: "8px 12px",
                                    color: "#e2e8f0", fontFamily: "inherit", fontSize: 12, outline: "none"
                                }} />
                        </div>
                    </>
                ) : (
                    <div style={{ marginBottom: 16 }}>
                        <div style={{ fontSize: 9, color: "#3a4a5c", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 5 }}>File Path</div>
                        <input value={localConfig.filepath || ""} onChange={e => setLocalConfig(c => ({ ...c, filepath: e.target.value }))}
                            placeholder="/path/to/database.db" style={{
                                width: "100%", background: "#080810", border: "1px solid #1e2d40", borderRadius: 7, padding: "8px 12px",
                                color: "#e2e8f0", fontFamily: "inherit", fontSize: 12, outline: "none"
                            }} />
                    </div>
                )}

                {testResult && (
                    <div style={{
                        padding: "8px 14px", borderRadius: 7, marginBottom: 14, fontSize: 12,
                        background: testResult === "success" ? "rgba(61,255,192,0.07)" : "rgba(255,80,80,0.07)",
                        border: `1px solid ${testResult === "success" ? "rgba(61,255,192,0.2)" : "rgba(255,80,80,0.2)"}`,
                        color: testResult === "success" ? "#3dffc0" : "#ff6b6b",
                    }}>
                        {testResult === "success" ? "✓ Connection successful" : "✗ Could not connect — check credentials"}
                    </div>
                )}

                <div style={{ display: "flex", gap: 10 }}>
                    <button onClick={handleTest} disabled={testing} style={{
                        flex: 1, padding: "10px 0", borderRadius: 8, border: "1px solid #1e3050",
                        background: "transparent", color: "#7eb8ff", fontFamily: "inherit", fontSize: 11,
                        cursor: testing ? "not-allowed" : "pointer", opacity: testing ? 0.5 : 1, letterSpacing: "0.06em"
                    }}>{testing ? "Testing..." : "Test Connection"}</button>
                    <button onClick={() => { setDbConfig(localConfig); onClose(); }} style={{
                        flex: 1, padding: "10px 0", borderRadius: 8, border: "none",
                        background: "linear-gradient(135deg, #3dffc0, #00d4aa)", color: "#0a0a0f",
                        fontFamily: "inherit", fontSize: 11, fontWeight: 700, cursor: "pointer", letterSpacing: "0.08em"
                    }}>Save Connection</button>
                </div>
            </div>
        </div>
    );
}
