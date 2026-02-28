// ── Query cost estimator ──────────────────────────────────────────────────────
export function estimateQueryCost(sqlText) {
    if (!sqlText) return null;
    const upper = sqlText.toUpperCase();
    const joinCount = (upper.match(/\bJOIN\b/g) || []).length;
    const hasNoLimit = !/\bLIMIT\b/.test(upper);
    const hasSubquery = (upper.match(/\bSELECT\b/g) || []).length > 1;
    const hasGroupBy = /\bGROUP BY\b/.test(upper);
    const hasDistinct = /\bDISTINCT\b/.test(upper);
    const hasWildcard = /SELECT\s+\*/.test(upper);

    let score = 0;
    let warnings = [];
    let estRows = "~1K";

    if (joinCount >= 3) { score += 40; warnings.push(`${joinCount} JOINs chained`); }
    else if (joinCount >= 1) { score += 15; }
    if (hasNoLimit) { score += 25; warnings.push("No LIMIT clause"); estRows = joinCount >= 2 ? "~100K+" : "~10K+"; }
    if (hasSubquery) { score += 20; warnings.push("Nested subquery"); }
    if (hasGroupBy) { score += 10; }
    if (hasDistinct) { score += 10; warnings.push("DISTINCT on large set"); }
    if (hasWildcard) { score += 5; warnings.push("SELECT * fetches all columns"); }

    const level = score >= 60 ? "heavy" : score >= 30 ? "moderate" : "light";
    return { score, level, warnings, estRows };
}

// ── Syntax error detector ─────────────────────────────────────────────────────
export function detectSyntaxErrors(sqlText) {
    const errors = [];
    const lines = sqlText.split("\n");

    const unclosedParen = (() => {
        let depth = 0, pos = -1;
        for (let i = 0; i < sqlText.length; i++) {
            if (sqlText[i] === "(") { depth++; pos = i; }
            if (sqlText[i] === ")") { depth--; }
        }
        return depth > 0 ? pos : -1;
    })();

    if (unclosedParen >= 0) {
        const lineIdx = sqlText.slice(0, unclosedParen).split("\n").length - 1;
        errors.push({ line: lineIdx, message: "Unclosed parenthesis" });
    }

    lines.forEach((line, i) => {
        const trimmed = line.trim().toUpperCase();
        if (/\bFROM\s+FROM\b/.test(trimmed)) errors.push({ line: i, message: "Duplicate FROM keyword" });
        if (/\bWHERE\s+WHERE\b/.test(trimmed)) errors.push({ line: i, message: "Duplicate WHERE keyword" });
        if (/\bSELECT\s+FROM\b/.test(trimmed)) errors.push({ line: i, message: "Missing column list between SELECT and FROM" });
    });

    return errors;
}

// ── SQL minifier ──────────────────────────────────────────────────────────────
export function minifySQL(sql) {
    return sql.replace(/\s+/g, " ").replace(/\s*([(),])\s*/g, "$1").trim();
}

// ── Token renderer for syntax highlighting ────────────────────────────────────
export function renderTokens(line, isErrorLine = false, React) {
    const parts = line.split(/('[^']*'|\b(?:SELECT|FROM|WHERE|JOIN|ON|GROUP\s+BY|ORDER\s+BY|LIMIT|DISTINCT|AND|OR|AS|INTERVAL|EXTRACT|DATE_TRUNC|COUNT|SUM|DATE|BY|DESC|ASC|HAVING|LEFT|RIGHT|INNER|OUTER|NOT|IN|IS|NULL|INSERT|UPDATE|DELETE|WITH|CASE|WHEN|THEN|END|ELSE)\b|\b\d+\b)/gi);
    return parts.map((part, i) => {
        if (/^'[^']*'$/.test(part)) return React.createElement('span', { key: i, style: { color: "#ff9e87" } }, part);
        if (/^\b(?:SELECT|FROM|WHERE|JOIN|ON|GROUP\s+BY|ORDER\s+BY|LIMIT|DISTINCT|AND|OR|AS|INTERVAL|EXTRACT|DATE_TRUNC|COUNT|SUM|DATE|BY|DESC|ASC|HAVING|LEFT|RIGHT|INNER|OUTER|NOT|IN|IS|NULL|INSERT|UPDATE|DELETE|WITH|CASE|WHEN|THEN|END|ELSE)\b$/i.test(part))
            return React.createElement('span', { key: i, style: { color: "#7eb8ff" } }, part);
        if (/^\d+$/.test(part)) return React.createElement('span', { key: i, style: { color: "#ffd787" } }, part);
        return React.createElement('span', { key: i, style: { color: isErrorLine ? "#ffaaaa" : undefined } }, part);
    });
}
