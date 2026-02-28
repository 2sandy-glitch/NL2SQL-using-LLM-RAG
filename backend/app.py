from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from services.sql_generator import get_sql_generator
from services.groq_llm_client import client as groq_client, MODEL_NAME as GROQ_MODEL
import json

app = FastAPI(
    title="Text-to-SQL Chatbot API",
    description="Convert natural language to SQL queries",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sql_generator = get_sql_generator()

# Request models
class SQLGenerateRequest(BaseModel):
    question: str
    include_sample_data: bool = False
    sample_rows: int = 3

class SQLExplainRequest(BaseModel):
    sql: str
    schema_context: Optional[str] = None

# Routes
@app.get("/")
def root():
    return {"message": "Text-to-SQL Chatbot API", "docs": "/docs"}

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/generate-sql")
def generate_sql(request: SQLGenerateRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    result = sql_generator.generate_sql(
        request.question,
        include_sample_data=request.include_sample_data,
        sample_rows=request.sample_rows
    )
    return result

@app.post("/explain-sql")
def explain_sql(request: SQLExplainRequest):
    if not request.sql:
        raise HTTPException(status_code=400, detail="SQL query is required")

    schema_hint = ""
    if request.schema_context:
        schema_hint = f"\n\nDatabase schema:\n{request.schema_context[:1500]}"

    prompt = f"""You are a SQL expert. Explain this SQL query in plain English for a non-technical user. Break it down clause by clause.

Return ONLY a JSON object with this exact structure (no markdown, no extra text):
{{
  "summary": "One sentence summary of what this query does",
  "clauses": [
    {{ "clause": "the SQL clause", "explanation": "plain English explanation" }}
  ],
  "tables_used": ["table1", "table2"],
  "complexity": "Simple"
}}

Complexity must be one of: Simple, Moderate, Complex.

SQL:
{request.sql}{schema_hint}"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )

        raw_text = response.choices[0].message.content.strip()
        # Clean up any markdown fencing
        clean = raw_text.replace("```json", "").replace("```", "").strip()
        explanation = json.loads(clean)
        return {"success": True, "explanation": explanation}

    except json.JSONDecodeError:
        return {"success": False, "error": "Failed to parse explanation response"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/suggestions")
def suggestions(limit: int = 5):
    suggestions = sql_generator.get_query_suggestions(limit=limit)
    return {"suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)