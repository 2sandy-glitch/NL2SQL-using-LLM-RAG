import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://127.0.0.1:5000';

function App() {
    const [question, setQuestion] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);

    useEffect(() => {
        fetchSuggestions();
    }, []);

    const fetchSuggestions = async () => {
        try {
            console.log('GET =>', `${API_BASE}/suggestions`);
            const res = await axios.get(`${API_BASE}/suggestions`);
            console.log('SUGGESTIONS <=', res.data);
            setSuggestions(res.data.suggestions || []);
        } catch (err) {
            console.error('Failed to fetch suggestions', err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('SUBMIT clicked. question=', question);

        if (!question.trim()) return;

        setLoading(true);
        setResult(null);

        try {
            console.log('POST =>', `${API_BASE}/generate-sql`);
            const res = await axios.post(`${API_BASE}/generate-sql`, {
                question: question,
                include_sample_data: false,
                sample_rows: 3,
            });
            console.log('RESPONSE <=', res.data);
            setResult(res.data);
        } catch (err) {
            console.error('REQUEST FAILED', err);
            setResult({
                success: false,
                error: err?.response?.data?.detail || err.message || 'Request failed',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>🤖 Text-to-SQL Chatbot</h1>
                <p>Ask questions about your database in natural language</p>
            </header>

            <div className="container">
                <div className="suggestions">
                    <h3>💡 Try these questions:</h3>
                    {suggestions.map((s, i) => (
                        <button
                            key={i}
                            onClick={() => setQuestion(s)}
                            className="suggestion-btn"
                            type="button"
                        >
                            {s}
                        </button>
                    ))}
                </div>

                <form onSubmit={handleSubmit} className="query-form">
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question about your data..."
                        className="query-input"
                    />
                    <button type="submit" disabled={loading} className="submit-btn">
                        {loading ? 'Generating...' : 'Generate SQL'}
                    </button>
                </form>

                {result && (
                    <div className={`result ${result.success ? 'success' : 'error'}`}>
                        {result.success ? (
                            <>
                                <h3>✅ Generated SQL:</h3>
                                <pre className="sql-code">{result.sql}</pre>

                                {result.validation && (
                                    <div className="validation">
                                        <p>Safety: {result.validation.is_safe ? '✅ Safe' : '❌ Unsafe'}</p>
                                        <p>Valid: {result.validation.is_valid ? '✅ Valid' : '❌ Invalid'}</p>

                                        {result.validation.warnings?.length > 0 && (
                                            <p>⚠️ Warnings: {result.validation.warnings.join(', ')}</p>
                                        )}

                                        {result.validation.issues?.length > 0 && (
                                            <p>❌ Issues: {result.validation.issues.join(', ')}</p>
                                        )}
                                    </div>
                                )}
                            </>
                        ) : (
                            <>
                                <h3>❌ Error:</h3>
                                <p>{result.error}</p>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;