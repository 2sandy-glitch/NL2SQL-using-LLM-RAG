import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Text-to-SQL Chatbot API", "docs": "/docs"}

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_suggestions():
    response = client.get("/suggestions")
    assert response.status_code == 200
    assert "suggestions" in response.json()
    assert isinstance(response.json()["suggestions"], list)

def test_generate_sql():
    # Test with a simple question
    payload = {
        "question": "Show all customers",
        "include_sample_data": False
    }
    response = client.post("/generate-sql", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sql" in data
    assert "success" in data

def test_explain_sql():
    # Test with a simple SQL query
    payload = {
        "sql": "SELECT * FROM customers;",
        "schema_context": "Table customers has columns id, name, email."
    }
    response = client.post("/explain-sql", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "explanation" in data
    explanation = data["explanation"]
    assert "summary" in explanation
    assert "clauses" in explanation
    assert "complexity" in explanation

def test_generate_sql_no_question():
    payload = {
        "question": "",
        "include_sample_data": False
    }
    response = client.post("/generate-sql", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()

def test_explain_sql_no_sql():
    payload = {
        "sql": "",
    }
    response = client.post("/explain-sql", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()
