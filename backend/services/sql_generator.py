from typing import Dict, Any, Optional, List
from config import get_config

config = get_config()


class SQLGenerator:
    """
    SQL Generator Service.

    - Supports MOCK mode for Phase 3 testing
    - Supports Real LLM backend
    - Includes strong SQL validation
    - Safe execution flow
    """

    FORBIDDEN_KEYWORDS = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "UPDATE",
        "INSERT",
        "GRANT",
        "REVOKE"
    ]

    def __init__(self, db, openai_client):
        self.db = db
        self.openai = openai_client

        # Toggle mock mode from config
        self.use_mock = getattr(config, "USE_MOCK_LLM", True)

    # --------------------------------------------------
    # SAMPLE DATA CONTEXT (Optional)
    # --------------------------------------------------

    def _get_sample_data_context(self, sample_rows: int = 3):
        """
        Returns sample rows from tables (Optional).
        Disabled by default in Phase 3.
        """
        return None

    # --------------------------------------------------
    # MOCK BACKEND 
    # --------------------------------------------------

    def _mock_generate_sql(self, question: str) -> Dict[str, Any]:
        q = question.lower()

        patterns = [
            (("customer", "how many"), "SELECT COUNT(*) FROM customers;"),
            (("customer",), "SELECT * FROM customers;"),
            (("order", "how many"), "SELECT COUNT(*) FROM orders;"),
            (("average",), "SELECT AVG(price) FROM products;"),
            (("avg",), "SELECT AVG(price) FROM products;"),
            (("product",), "SELECT * FROM products;"),
        ]

        for keywords, sql in patterns:
            if all(word in q for word in keywords):
                return {"success": True, "sql": sql}

        return {"success": True, "sql": "SELECT 1;"}

    # --------------------------------------------------
    # REAL LLM BACKEND
    # --------------------------------------------------

    def _llm_generate_sql(
        self,
        question: str,
        schema_context: str,
        sample_data: Optional[str] = None
    ) -> Dict[str, Any]:

        if not self.openai:
            return {
                "success": False,
                "error": "LLM client not initialized"
            }

        try:
            return self.openai.generate_sql(
                question=question,
                schema_context=schema_context,
                sample_data=sample_data
            )
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # --------------------------------------------------
    # PUBLIC SQL GENERATION
    # --------------------------------------------------

    def generate_sql(
        self,
        question: str,
        include_sample_data: bool = False,
        sample_rows: int = 3
    ) -> Dict[str, Any]:

        try:
            schema_context = self.db.get_schema_for_prompt()
        except Exception as e:
            return {"success": False, "error": f"Schema error: {str(e)}"}

        sample_data = None
        if include_sample_data:
            sample_data = self._get_sample_data_context(sample_rows)

        # Choose backend
        if self.use_mock:
            ai_response = self._mock_generate_sql(question)
        else:
            ai_response = self._llm_generate_sql(
                question,
                schema_context,
                sample_data
            )

        if not ai_response.get("success"):
            return {
                "success": False,
                "error": ai_response.get("error", "Unknown LLM error")
            }

        sql = ai_response.get("sql")

        if not sql:
            return {
                "success": False,
                "error": "No SQL generated"
            }

        validation = self.validate_sql(sql)

        return {
            "success": validation["is_safe"],
            "sql": sql,
            "validation": validation
        }

    # --------------------------------------------------
    # SAFE EXECUTION PIPELINE
    # --------------------------------------------------

    def generate_and_execute(
        self,
        question: str,
        include_sample_data: bool = False,
        auto_explain: bool = False
    ) -> Dict[str, Any]:

        generation = self.generate_sql(
            question,
            include_sample_data=include_sample_data
        )

        if not generation.get("success"):
            return generation

        if not generation["validation"]["is_safe"]:
            return {
                "success": False,
                "error": "Unsafe SQL detected"
            }

        try:
            # Stub execution for Phase 3
            execution_result = {
                "success": True,
                "row_count": 1,
                "data": [["Example"]],
                "execution_time": 0.01
            }

            generation["execution_result"] = execution_result

            if auto_explain:
                generation["explanation"] = (
                    "This query retrieves data from the database "
                    "based on the user's request."
                )

            return generation

        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}"
            }

    # --------------------------------------------------
    # QUERY SUGGESTIONS
    # --------------------------------------------------

    def get_query_suggestions(self, limit: int = 5) -> List[str]:
        suggestions = [
            "Show all customers",
            "Show all products",
            "How many orders are there?",
            "What is the average price of products?",
            "List all orders for customer John Doe"
        ]
        return suggestions[:limit]

    # --------------------------------------------------
    # SQL VALIDATION 
    # --------------------------------------------------

    def validate_sql(self, sql_query: str) -> Dict[str, Any]:

        upper_sql = sql_query.strip().upper()

        issues = []

        if not upper_sql.startswith("SELECT"):
            issues.append("Only SELECT queries are allowed")

        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in upper_sql:
                issues.append(f"Forbidden keyword detected: {keyword}")

        is_safe = len(issues) == 0

        return {
            "is_safe": is_safe,
            "is_valid": True,
            "issues": issues,
            "warnings": []
        }


# --------------------------------------------------
# Singleton Factory
# --------------------------------------------------

_sql_generator: Optional[SQLGenerator] = None


def get_sql_generator() -> SQLGenerator:
    global _sql_generator

    if _sql_generator is None:
        from services.db_connector import get_db_connector
        from services.openai_client import get_openai_client

        db = get_db_connector()
        openai_client = get_openai_client()

        _sql_generator = SQLGenerator(db, openai_client)

    return _sql_generator
