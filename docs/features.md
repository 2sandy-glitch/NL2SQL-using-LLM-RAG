# ✨ Features — AI-Powered Text-to-SQL RAG Chatbot

A comprehensive breakdown of every feature in the NL2SQL chatbot — organized by layer and purpose.

---

## Table of Contents

- [Core Intelligence](#-core-intelligence)
- [RAG Pipeline](#-rag-pipeline)
- [Security & Guardrails](#-security--guardrails)
- [Multi-Database Support](#️-multi-database-support)
- [API Layer](#-api-layer)
- [Frontend Experience](#-frontend-experience)
- [Developer Experience](#-developer-experience)
- [Planned / Roadmap](#-planned--roadmap)

---

## 🧠 Core Intelligence

### Natural Language → SQL Translation

The heart of the application. Users type plain English questions and the system generates precise, validated SQL queries.

- **LLM Backend** — Groq API with **Llama 3.1 8B Instant** for fast, high-quality SQL generation
- **Schema-Grounded Prompts** — Every LLM call includes the actual database schema so the model never hallucinates table or column names
- **PostgreSQL-Aware Quoting** — Automatically handles double-quoted identifiers for mixed-case table/column names (e.g., `FROM "CustomerOrders"`)
- **Mock Mode** — Built-in mock SQL generator (`USE_MOCK_LLM=True`) for offline development and testing without API calls
- **Fallback Chain** — If the primary context source fails, the system gracefully falls back through: RAG context → full schema dump → error

### AI-Powered SQL Explanation

One-click, clause-by-clause breakdown of any generated SQL query.

- Powered by the same Groq LLM backend
- Schema-aware explanations — the model knows your tables/columns for accurate, contextual descriptions
- Presented in a dedicated **Explain Tab** in the UI

### Smart Query Suggestions

Pre-built natural language prompts to help users get started immediately.

- Dynamically fetched from the backend (`/suggestions` endpoint)
- Contextual defaults based on common query patterns
- Click-to-fill for instant query generation

---

## 🔎 RAG Pipeline

### ChromaDB Vector Store

Instead of dumping the entire database schema into every LLM prompt, the RAG engine indexes your schema and retrieves only the most relevant context per query.

| Component | Details |
|---|---|
| **Vector Database** | ChromaDB with persistent storage |
| **Embedding Model** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Indexed Documents** | Table descriptions, column metadata, sample data rows |
| **Collection** | `schema_embeddings` — auto-created on first connection |

### How It Works

1. **Schema Indexing** — On database connection, every table and column is converted into a natural language document and embedded into ChromaDB
2. **Semantic Hints** — Column names are enriched with semantic tags (e.g., `price` → "monetary value", `email` → "email address", `is_active` → "boolean flag")
3. **Sample Data Indexing** — Sample rows from each table are embedded for richer context
4. **Smart Retrieval** — User questions are embedded and matched against the schema vectors; only the top-k most relevant tables/columns are sent to the LLM
5. **Change Detection** — Schema hash tracking avoids unnecessary re-indexing when the schema hasn't changed

### RAG Stats & Reindexing

- **`GET /rag/stats`** — View index health: document count, collection name, persist directory
- **`POST /rag/reindex`** — Force a full re-index when schema changes aren't auto-detected

---

## 🔒 Security & Guardrails

Enterprise-grade SQL validation ensures the LLM can never generate or execute destructive queries.

### Multi-Layer Validation

```
User Question → LLM → Generated SQL → SQLGenerator Validation → SQLValidator Validation → Execution
```

Both `SQLGenerator` and `SQLValidator` enforce overlapping security checks for defense-in-depth.

### Blocked Operations

| Category | Blocked Keywords / Patterns |
|---|---|
| **Destructive DML** | `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` |
| **Schema Modification** | `DROP`, `ALTER`, `CREATE`, `REPLACE` |
| **Privilege Escalation** | `GRANT`, `REVOKE`, `EXEC`, `CALL` |
| **SQL Injection Patterns** | `--` (comments), `/* */` (block comments), `UNION SELECT`, `SLEEP()` |
| **Multi-Statement** | Semicolons within the query body (chained statements) |

### Query Constraints

| Constraint | Value | Description |
|---|---|---|
| **SELECT-Only** | Enforced | Only `SELECT` queries are permitted |
| **Max Query Length** | 1,000 chars | Prevents prompt-injection via oversized queries |
| **Default LIMIT** | 100 rows | Auto-injected if no `LIMIT` clause is present |
| **Max LIMIT** | 500 rows | Caps any `LIMIT` clause to prevent full-table scans |
| **System Schema Block** | Enforced | Blocks `information_schema`, `pg_catalog`, `mysql`, `sys` |

### Risk Scoring

Every query receives a **risk score** (0–100+) based on detected issues:

- `+50` — Non-SELECT query detected
- `+40` — Forbidden keyword found
- `+40` — System table access attempted
- `+30` — Multiple SQL statements detected

Queries with any non-zero issues are **blocked from execution**.

---

## 🗄️ Multi-Database Support

Connect to any of the three supported database engines through a unified SQLAlchemy-powered connector.

| Database | Driver | Default Port | Status |
|---|---|---|---|
| **SQLite** | Built-in (`sqlite3`) | N/A (file-based) | ✅ Production Ready |
| **PostgreSQL** | `psycopg2-binary` | 5432 | ✅ Production Ready |
| **MySQL** | `pymysql` | 3306 | ✅ Production Ready |

### Connection Features

- **Test Before Connect** — `POST /test-connection` validates credentials without committing
- **Live Schema Introspection** — On connect, the full schema (tables, columns, types) is extracted and indexed
- **Auto-RAG Indexing** — Schema is automatically embedded into ChromaDB on every new connection
- **Connection Status** — Real-time connection state indicator in the UI header (`● Live` / `○ Offline`)
- **Dynamic Reconfiguration** — Switch databases on the fly via the DB Settings panel

### Data Loading

- **CSV Import** — Upload CSV files directly into the connected database
- **Excel Import** — Upload `.xlsx` files with automatic type inference
- Powered by `pandas`, `numpy`, and `openpyxl`

---

## 📡 API Layer

Full REST API built with **FastAPI** + **Uvicorn**, with automatic OpenAPI documentation.

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/status` | Server status & configuration |
| `POST` | `/generate-sql` | Convert natural language → SQL (RAG-powered) |
| `POST` | `/execute-sql` | Validate and execute SQL against the connected DB |
| `POST` | `/explain-sql` | AI-powered clause-by-clause SQL explanation |
| `POST` | `/test-connection` | Test database connectivity without connecting |
| `POST` | `/connect-db` | Connect to DB and auto-index schema into RAG |
| `GET` | `/schema` | Get parsed schema of the connected database |
| `GET` | `/suggestions` | Get sample query suggestions |
| `GET` | `/history` | Retrieve query history |
| `POST` | `/history` | Save a query to history |
| `GET` | `/rag/stats` | RAG index statistics |
| `POST` | `/rag/reindex` | Force re-index schema into ChromaDB |

### API Features

- **Interactive Docs** — Swagger UI at `/docs` and ReDoc at `/redoc` when running
- **CORS Enabled** — Frontend ↔ Backend communication across different ports
- **Pydantic Validation** — All request/response bodies are type-validated
- **Structured Error Responses** — Consistent `{ success, error, data }` format
- **Loguru Logging** — Structured, file-rotated logs with configurable verbosity

---

## 🎨 Frontend Experience

A modern, polished React 18 single-page application with a premium developer-tool aesthetic.

### Theme System

- **Dark / Light Mode** — Seamless toggle via CSS custom properties
- Theme state managed through React Context (`ThemeContext.js`)
- Smooth transitions between modes with no flash-of-unstyled-content

### Chat Interface

- **Natural Language Input** — Large, focused input area for typing questions
- **Schema-Aware Autocomplete** — As you type, real-time suggestions for table and column names from the connected database
- **Click-to-Query Suggestions** — Pre-built query cards for instant exploration
- **Real-Time Processing Timer** — Live millisecond counter during query generation (50ms refresh interval)

### SQL Display & Analysis

- **Syntax Highlighting** — Color-coded SQL with keyword, string, and number differentiation + line numbers
- **Query Cost Estimation** — Instant complexity analysis displayed via `QueryCostBanner` before execution
- **Syntax Error Detection** — Real-time detection of common SQL syntax issues
- **One-Click Explain** — Trigger AI explanation of any displayed SQL query

### Results View

- **Tabbed Interface** — Switch between SQL, Results, Explain, and History tabs
- **Responsive Data Grid** — Results displayed in an animated table with row-slide animations
- **Execution Error Display** — Clear, actionable error messages when SQL execution fails
- **Empty State** — Welcoming empty state with guided first steps

### Data Export

- **CSV Export** — One-click download of query results as `.csv`
- **JSON Export** — One-click download of query results as `.json`

### Query History

- **Session Persistence** — Query history persisted to the backend across sessions
- **Restore Capability** — Click any historical query to restore it to the input + SQL view
- **Processing Time Tracking** — Each history entry records generation time in milliseconds
- **50-Entry Cap** — Keeps the most recent 50 queries to prevent clutter

### Database Settings Panel

- **Modal Configuration** — Clean modal UI for entering connection credentials
- **Database Type Selector** — Switch between SQLite, PostgreSQL, and MySQL
- **Test Connection** — Verify credentials before committing
- **One-Click Connect** — Connects and auto-populates the schema panel

---

## 🛠️ Developer Experience

### Configuration

- **Environment-Driven** — All configuration via `.env` file (see `.env.example`)
- **Configurable LLM** — Switch between Groq, OpenAI, HuggingFace, or local Ollama
- **Mock Mode** — Full offline development with `USE_MOCK_LLM=True`
- **Debug Mode** — Verbose logging and error details with `DEBUG=True`

### Code Quality

- **Ruff** — Fast Python linter
- **Black** — Opinionated code formatter
- **MyPy** — Static type checking
- **Pytest + Coverage** — Comprehensive test suite with HTML coverage reports

### Logging

- **Loguru** — Structured, colorful logging with automatic file rotation
- Configurable log level via `LOG_LEVEL` environment variable
- Separate logger instances per module for clean filtering

### Architecture Patterns

- **Singleton Services** — `SQLGenerator`, `RAGEngine`, and `DatabaseConnector` use singleton factories for consistent state
- **Adapter Pattern** — `GroqClientWrapper` adapts the Groq API client to the internal `generate_sql()` interface
- **Defense-in-Depth** — Overlapping validation in both `SQLGenerator` and `SQLValidator`
- **Graceful Degradation** — RAG failures fall back to full schema; missing sample data doesn't block generation

---

## 🗺️ Planned / Roadmap

| Feature | Status |
|---|---|
| **Docker Deployment** | 🔜 Dockerfile + docker-compose.yml scaffolded |
| **Multi-Turn Conversation** | 📋 Planned — context-aware follow-up queries |
| **Query Caching** | 📋 Planned — avoid redundant LLM calls for repeated questions |
| **User Authentication** | 📋 Planned — role-based access control |
| **Additional LLM Providers** | 📋 Planned — OpenAI, Ollama, HuggingFace backends |
| **Natural Language to Chart** | 📋 Planned — auto-generate visualizations from query results |

---

<div align="center">

**[← Back to Main README](../README.md)** · **[Installation Guide →](installation.md)** · **[User Manual →](user_manual.md)**

</div>
