import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import ChatBox from './components/ChatBox';
import ResultView from './components/ResultView';
import SchemaPanel from './components/SchemaPanel';
import DBSettingsPanel from './components/DBSettingsPanel';
import { parseSchema, SAMPLE_SCHEMA } from './utils/schemaUtils';
import { estimateQueryCost, detectSyntaxErrors } from './utils/sqlUtils';

const API_BASE = 'http://127.0.0.1:5000';

const DEFAULT_SUGGESTIONS = [
    "Show me all customers who made a purchase last month",
    "What are the top 5 products by revenue in Q4?",
    "Find employees in the engineering department hired after 2020",
    "How many orders were placed per day this week?",
];

function App() {
    const [input, setInput] = useState("");
    const [sql, setSql] = useState("");
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [history, setHistory] = useState([]);
    const [processingTime, setProcessingTime] = useState(null);
    const [elapsedMs, setElapsedMs] = useState(0);

    // Schema state
    const [schemaOpen, setSchemaOpen] = useState(false);
    const [schemaText, setSchemaText] = useState(SAMPLE_SCHEMA);
    const [parsedSchema, setParsedSchema] = useState({});
    const [schemaLoaded, setSchemaLoaded] = useState(false);

    // Explain state
    const [explanation, setExplanation] = useState(null);
    const [explainLoading, setExplainLoading] = useState(false);

    // SQL analysis state
    const [syntaxErrors, setSyntaxErrors] = useState([]);
    const [queryCost, setQueryCost] = useState(null);

    // DB settings state
    const [dbSettingsOpen, setDbSettingsOpen] = useState(false);
    const [dbConfig, setDbConfig] = useState({ type: "PostgreSQL", host: "", port: "5432", database: "", user: "", password: "" });

    const timerRef = useRef(null);
    const startTimeRef = useRef(null);

    useEffect(() => {
        fetchSuggestions();
    }, []);

    // Parse schema whenever it changes
    useEffect(() => {
        if (schemaText.trim()) {
            const parsed = parseSchema(schemaText);
            setParsedSchema(parsed);
            setSchemaLoaded(Object.keys(parsed).length > 0);
        }
    }, [schemaText]);

    // Detect syntax errors and cost whenever SQL changes
    useEffect(() => {
        if (sql) {
            setSyntaxErrors(detectSyntaxErrors(sql).map(e => e.line));
            setQueryCost(estimateQueryCost(sql));
        } else {
            setSyntaxErrors([]);
            setQueryCost(null);
        }
    }, [sql]);

    const fetchSuggestions = async () => {
        try {
            const res = await axios.get(`${API_BASE}/suggestions`);
            if (res.data.suggestions && res.data.suggestions.length > 0) {
                setSuggestions(res.data.suggestions);
            }
        } catch (err) {
            console.error('Failed to fetch suggestions', err);
        }
    };

    const handleConvert = async (query = input) => {
        if (!query.trim()) return;
        setLoading(true);
        setSql("");
        setResults(null);
        setShowSuggestions(false);
        setExplanation(null);
        setProcessingTime(null);
        setElapsedMs(0);

        startTimeRef.current = performance.now();
        timerRef.current = setInterval(() => setElapsedMs(Math.floor(performance.now() - startTimeRef.current)), 50);

        try {
            const res = await axios.post(`${API_BASE}/generate-sql`, {
                question: query,
                include_sample_data: true,
                sample_rows: 5,
            });

            clearInterval(timerRef.current);
            const totalMs = Math.floor(performance.now() - startTimeRef.current);
            setProcessingTime(totalMs);

            if (res.data.success) {
                setSql(res.data.sql);
                setResults(res.data.sample_data || []);
                setHistory((prev) => [{ query, sql: res.data.sql, time: new Date(), processingTime: totalMs }, ...prev.slice(0, 9)]);
            } else {
                setSql(`-- Error: ${res.data.error}`);
            }
        } catch (err) {
            clearInterval(timerRef.current);
            const totalMs = Math.floor(performance.now() - startTimeRef.current);
            setProcessingTime(totalMs);
            console.error('REQUEST FAILED', err);
            setSql(`-- Error: ${err?.response?.data?.detail || err.message || 'Request failed'}`);
        } finally {
            setLoading(false);
        }
    };

    const handleExplain = async (sqlToExplain) => {
        const targetSql = sqlToExplain || sql;
        if (!targetSql) return;
        setExplainLoading(true);
        setExplanation(null);

        try {
            const schemaContext = schemaLoaded ? `\n\nDatabase schema:\n${schemaText.slice(0, 1500)}` : "";
            const response = await fetch("https://api.anthropic.com/v1/messages", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "claude-sonnet-4-20250514",
                    max_tokens: 1000,
                    messages: [{
                        role: "user",
                        content: `You are a SQL expert. Explain this SQL query in plain English for a non-technical user. Break it down clause by clause.

Return ONLY a JSON object with this exact structure (no markdown, no extra text):
{
  "summary": "One sentence summary of what this query does",
  "clauses": [
    { "clause": "the SQL clause", "explanation": "plain English explanation" }
  ],
  "tables_used": ["table1", "table2"],
  "complexity": "Simple"
}

Complexity must be one of: Simple, Moderate, Complex.

SQL:
${targetSql}${schemaContext}`
                    }]
                })
            });
            const data = await response.json();
            const text = data.content?.map(c => c.text || "").join("") || "";
            const clean = text.replace(/```json|```/g, "").trim();
            setExplanation(JSON.parse(clean));
        } catch (err) {
            setExplanation({ error: "Could not generate explanation. Please try again." });
        }
        setExplainLoading(false);
    };

    const handleRestoreHistory = (h) => {
        setInput(h.query);
        setSql(h.sql);
        setResults(null);
        setExplanation(null);
    };

    const dbConnected = !!(dbConfig.host || dbConfig.filepath);

    return (
        <div className="App">
            {/* DB Settings Modal */}
            {dbSettingsOpen && <DBSettingsPanel onClose={() => setDbSettingsOpen(false)} dbConfig={dbConfig} setDbConfig={setDbConfig} />}

            <header style={{
                padding: "18px 36px",
                borderBottom: "1px solid #111827",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
            }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{
                        width: 34, height: 34,
                        background: "linear-gradient(135deg, #3dffc0, #0099cc)",
                        borderRadius: 8,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 15, fontWeight: 700,
                        color: "#0a0a0f"
                    }}>⟨⟩</div>
                    <div>
                        <div style={{
                            fontFamily: "'Syne', sans-serif",
                            fontSize: 19, fontWeight: 800,
                            letterSpacing: "-0.02em",
                            color: "#fff",
                        }}>NL<span style={{ color: "#3dffc0" }}>2</span>SQL</div>
                        <div style={{
                            fontSize: 9, color: "#3a4a5c",
                            letterSpacing: "0.15em",
                            textTransform: "uppercase",
                        }}>Natural Language to Query</div>
                    </div>
                </div>
                <div style={{ fontSize: 11, display: "flex", gap: 12, alignItems: "center" }}>
                    {schemaLoaded && (
                        <span style={{ color: "#3dffc0", background: "rgba(61,255,192,0.07)", border: "1px solid rgba(61,255,192,0.18)", borderRadius: 5, padding: "3px 10px" }}>
                            ✦ Schema · {Object.keys(parsedSchema).length} tables
                        </span>
                    )}
                    <button onClick={() => setDbSettingsOpen(true)} style={{
                        display: "flex", alignItems: "center", gap: 6, padding: "5px 12px",
                        background: dbConnected ? "rgba(61,255,192,0.07)" : "transparent",
                        border: `1px solid ${dbConnected ? "rgba(61,255,192,0.25)" : "#1e2d40"}`,
                        borderRadius: 6, cursor: "pointer", fontFamily: "inherit", fontSize: 11,
                        color: dbConnected ? "#3dffc0" : "#4a6080", transition: "all 0.15s"
                    }}>
                        <span style={{ fontSize: 8 }}>●</span>
                        {dbConnected ? `${dbConfig.type} · ${dbConfig.host || dbConfig.filepath}` : "Connect DB"}
                    </button>
                    <span style={{ color: "#3dffc0" }}>● Live</span>
                    <span style={{ color: "#3a4a5c" }}>v3.0.0</span>
                </div>
            </header>

            <main style={{
                flex: 1,
                maxWidth: 1100,
                width: "100%",
                margin: "0 auto",
                padding: "28px 24px",
                display: "flex",
                gap: 20,
            }}>
                {/* Schema Sidebar */}
                <SchemaPanel
                    schemaOpen={schemaOpen}
                    schemaText={schemaText}
                    setSchemaText={setSchemaText}
                    parsedSchema={parsedSchema}
                    schemaLoaded={schemaLoaded}
                />

                {/* Main Content */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 18, minWidth: 0 }}>
                    <ChatBox
                        input={input}
                        setInput={setInput}
                        handleConvert={handleConvert}
                        loading={loading}
                        suggestions={suggestions}
                        showSuggestions={showSuggestions}
                        setShowSuggestions={setShowSuggestions}
                        schemaLoaded={schemaLoaded}
                        parsedSchema={parsedSchema}
                        schemaOpen={schemaOpen}
                        setSchemaOpen={setSchemaOpen}
                    />

                    <ResultView
                        sql={sql}
                        results={results}
                        loading={loading}
                        processingTime={processingTime}
                        elapsedMs={elapsedMs}
                        syntaxErrors={syntaxErrors}
                        queryCost={queryCost}
                        history={history}
                        explanation={explanation}
                        explainLoading={explainLoading}
                        handleExplain={handleExplain}
                        onRestoreHistory={handleRestoreHistory}
                    />
                </div>
            </main>
        </div>
    );
}

export default App;