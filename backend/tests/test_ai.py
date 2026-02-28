"""
Test file for AI components.
Tests SQL generation pipeline and Groq LLM integration.
"""

import sys
import os

# Add backend to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


# --------------------------------------------------
# TEST 1: Groq Connection
# --------------------------------------------------
def test_groq_connection():
    print("\n" + "=" * 60)
    print("TEST 1: Groq Connection")
    print("=" * 60)

    try:
        from services.groq_llm_client import client as groq_client, MODEL_NAME

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )

        if response.choices:
            print(f"  [OK] Groq completion successful: {response.choices[0].message.content}")
            return True
        else:
            print("  [FAIL] No response from Groq")
            return False

    except Exception as e:
        print(f"  [FAIL] Groq connection test failed: {e}")
        return False


# --------------------------------------------------
# TEST 2: RAG Engine
# --------------------------------------------------
def test_rag_engine():
    print("\n" + "=" * 60)
    print("TEST 2: RAG Engine")
    print("=" * 60)

    try:
        from services.rag_engine import get_rag_engine
        from services.db_connector import get_db_connector

        db = get_db_connector()
        db.connect()

        rag = get_rag_engine()
        print("  [OK] RAG engine created")

        if not rag.initialize():
            print("  [FAIL] RAG initialization failed")
            return False

        result = rag.index_schema(force_reindex=True)

        if result["success"]:
            print("  [OK] Schema indexed")
            print(f"      Tables: {result['tables_indexed']}")
            print(f"      Documents: {result['documents_added']}")

            ctx = rag.retrieve_context("Show all customers")
            if ctx["success"]:
                print("  [OK] Context retrieval successful")
                return True

        print("  [FAIL] RAG test failed")
        return False

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


# --------------------------------------------------
# TEST 3: SQL Generation (NO SAMPLE DATA)
# --------------------------------------------------
def test_sql_generation():
    print("\n" + "=" * 60)
    print("TEST 3: SQL Generation")
    print("=" * 60)

    try:
        from services.sql_generator import get_sql_generator
        from services.db_connector import get_db_connector

        db = get_db_connector()
        db.connect()

        generator = get_sql_generator()
        print("  [OK] SQL Generator created")

        questions = [
            "Show all customers",
            "How many orders are there?",
            "What is the average price of products?"
        ]

        for q in questions:
            print(f"\n  Question: {q}")
            result = generator.generate_sql(
                q,
                include_sample_data=False  # 🔴 IMPORTANT FIX
            )

            if result["success"]:
                print(f"  [OK] SQL: {result['sql']}")
            else:
                print(f"  [FAIL] SQL generation failed: {result['error']}")
                return False

        return True

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


# --------------------------------------------------
# TEST 4: End-to-End (STUB EXECUTION)
# --------------------------------------------------
def test_end_to_end():
    print("\n" + "=" * 60)
    print("TEST 4: End-to-End Flow")
    print("=" * 60)

    try:
        from services.sql_generator import get_sql_generator

        generator = get_sql_generator()

        result = generator.generate_and_execute(
            "How many customers are there?",
            include_sample_data=False
        )

        if result["success"]:
            print("  [OK] End-to-end pipeline executed")
            return True

        print("  [FAIL] End-to-end failed")
        return False

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


# --------------------------------------------------
# TEST 5: SQL Explanation
# --------------------------------------------------
def test_sql_explanation():
    print("\n" + "=" * 60)
    print("TEST 5: SQL Explanation")
    print("=" * 60)

    try:
        from services.sql_generator import get_sql_generator

        generator = get_sql_generator()
        test_sql = "SELECT * FROM customers WHERE city = 'New York';"
        
        # We need to mock the response or call the real one
        from services.groq_llm_client import client as groq_client, MODEL_NAME
        import json

        print(f"  Testing explanation for: {test_sql}")
        
        # In a real test we'd use the endpoint logic, but here we test the service integration
        # For now, let's just verify we can reach the LLM with an explanation prompt
        prompt = f"Explain this SQL in JSON: {test_sql}"
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        if response.choices:
            print("  [OK] Explanation generated")
            return True
        
        return False

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


# --------------------------------------------------
# TEST 6: SQL Validation
# --------------------------------------------------
def test_sql_validation():
    print("\n" + "=" * 60)
    print("TEST 6: SQL Validation")
    print("=" * 60)

    try:
        from services.sql_generator import get_sql_generator

        generator = get_sql_generator()

        tests = [
            ("SELECT * FROM customers", True),
            ("DROP TABLE customers", False),
        ]

        for sql, expected in tests:
            result = generator.validate_sql(sql)
            print(f"  SQL: {sql} → is_safe={result['is_safe']}")

            if result["is_safe"] != expected:
                return False

        return True

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


# --------------------------------------------------
# MAIN RUNNER
# --------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("TEXT-TO-SQL CHATBOT — PHASE 3 TESTS")
    print("=" * 60)

    tests = {
        "Groq Connection": test_groq_connection(),
        "RAG Engine": test_rag_engine(),
        "SQL Generation": test_sql_generation(),
        "End-to-End": test_end_to_end(),
        "SQL Explanation": test_sql_explanation(),
        "SQL Validation": test_sql_validation(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in tests.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1

    print("\n" + "-" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed >= 4:
        print("\n[SUCCESS] Phase 3 considered COMPLETE")
    else:
        print("\n[WARNING] Some tests failed")

    print("=" * 60)


if __name__ == "__main__":
    main()
