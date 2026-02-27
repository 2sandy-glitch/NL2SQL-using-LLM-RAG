import React from "react";

export default function EmptyState() {
    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "48px 24px", gap: 20 }}>
            <svg width="120" height="96" viewBox="0 0 120 96" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="dbGrad" x1="0" y1="0" x2="120" y2="96" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stopColor="#3dffc0" stopOpacity="0.15" />
                        <stop offset="100%" stopColor="#0099cc" stopOpacity="0.05" />
                    </linearGradient>
                </defs>
                <ellipse cx="60" cy="22" rx="32" ry="10" fill="url(#dbGrad)" stroke="#1e3a50" strokeWidth="1.5" />
                <rect x="28" y="22" width="64" height="42" fill="url(#dbGrad)" stroke="none" />
                <line x1="28" y1="22" x2="28" y2="64" stroke="#1e3a50" strokeWidth="1.5" />
                <line x1="92" y1="22" x2="92" y2="64" stroke="#1e3a50" strokeWidth="1.5" />
                <ellipse cx="60" cy="42" rx="32" ry="10" fill="none" stroke="#1e3a50" strokeWidth="1" strokeDasharray="4 3" />
                <ellipse cx="60" cy="64" rx="32" ry="10" fill="url(#dbGrad)" stroke="#1e3a50" strokeWidth="1.5" />
                <path d="M36 26 Q48 23 56 25" stroke="#3dffc0" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
                <circle cx="100" cy="14" r="2" fill="#3dffc0" opacity="0.5" />
                <circle cx="108" cy="30" r="1.5" fill="#7eb8ff" opacity="0.4" />
                <circle cx="16" cy="38" r="1.5" fill="#3dffc0" opacity="0.3" />
                <circle cx="12" cy="20" r="2" fill="#ffd787" opacity="0.3" />
                <path d="M60 80 L60 90 M55 85 L60 90 L65 85" stroke="#2a3a50" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                <text x="60" y="96" textAnchor="middle" fill="#2a3a50" fontSize="8" fontFamily="IBM Plex Mono, monospace" letterSpacing="2">TYPE A QUERY</text>
            </svg>
            <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#3a4a5c", marginBottom: 6, letterSpacing: "0.05em" }}>No query run yet</div>
                <div style={{ fontSize: 11, color: "#1e2d40", lineHeight: 1.6 }}>Describe what data you need in plain English<br />and it will be converted to SQL instantly.</div>
            </div>
        </div>
    );
}
