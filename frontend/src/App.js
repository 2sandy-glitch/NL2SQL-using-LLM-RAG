import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ChatBox from './components/ChatBox';
import ResultView from './components/ResultView';

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

    useEffect(() => {
        fetchSuggestions();
    }, []);

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

        try {
            const res = await axios.post(`${API_BASE}/generate-sql`, {
                question: query,
                include_sample_data: true, // Request sample data to populate results
                sample_rows: 5,
            });

            if (res.data.success) {
                setSql(res.data.sql);
                setResults(res.data.sample_data || []);
            } else {
                setSql(`-- Error: ${res.data.error}`);
            }
        } catch (err) {
            console.error('REQUEST FAILED', err);
            setSql(`-- Error: ${err?.response?.data?.detail || err.message || 'Request failed'}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
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
                    <span style={{ color: "#3dffc0" }}>● Live</span>
                    <span style={{ color: "#3a4a5c" }}>v1.0.0</span>
                </div>
            </header>

            <main style={{
                flex: 1,
                maxWidth: 860,
                width: "100%",
                margin: "0 auto",
                padding: "28px 24px",
                display: "flex",
                flexDirection: "column",
                gap: 18,
            }}>
                <ChatBox
                    input={input}
                    setInput={setInput}
                    handleConvert={handleConvert}
                    loading={loading}
                    suggestions={suggestions}
                    showSuggestions={showSuggestions}
                    setShowSuggestions={setShowSuggestions}
                />

                <ResultView
                    sql={sql}
                    results={results}
                    loading={loading}
                />
            </main>
        </div>
    );
}

export default App;