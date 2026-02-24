import React from 'react';

const ResultView = ({ data }) => {
    return (
        <div className="result-container">
            <div className="card explanation">
                <h3><i className="icon">💡</i> AI Explanation</h3>
                <p>{data.explanation || "This query joins the sales and product tables to find the requested values."}</p>
            </div>

            <div className="card sql-block">
                <h3><i className="icon">📂</i> Generated SQL</h3>
                <pre>
                    <code>{data.sql}</code>
                </pre>
            </div>

            {data.results && (
                <div className="card table-view">
                    <h3><i className="icon">📊</i> Query Results</h3>
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    {Object.keys(data.results[0] || {}).map((key) => (
                                        <th key={key}>{key}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.results.map((row, i) => (
                                    <tr key={i}>
                                        {Object.values(row).map((val, j) => (
                                            <td key={j}>{val}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

