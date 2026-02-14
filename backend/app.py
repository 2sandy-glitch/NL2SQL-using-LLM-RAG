from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from services.sql_generator import get_sql_generator

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

@app.get("/suggestions")
def suggestions(limit: int = 5):
    suggestions = sql_generator.get_query_suggestions(limit=limit)
    return {"suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)