"""
Utility functions for the Text-to-SQL Chatbot application.
"""

import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps

# Import logger - handle case where it might not be set up yet
try:
    from logger import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger(__name__)


def timer_decorator(func):
    """
    Decorator to measure and log function execution time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def validate_sql_query(sql_query: str) -> Dict[str, Any]:
    """
    Validate a generated SQL query for safety and correctness.
    
    Args:
        sql_query: SQL query string to validate
    
    Returns:
        Dictionary with 'valid', 'query_type', 'warnings', and 'errors' keys
    """
    logger.debug(f"Validating SQL query: {sql_query}")
    
    result = {
        "valid": True,
        "query_type": None,
        "warnings": [],
        "errors": []
    }
    
    if not sql_query or not sql_query.strip():
        result["valid"] = False
        result["errors"].append("Empty query")
        return result
    
    # Normalize query
    normalized_query = sql_query.strip().upper()
    
    # Detect query type
    if normalized_query.startswith("SELECT"):
        result["query_type"] = "SELECT"
    elif normalized_query.startswith("INSERT"):
        result["query_type"] = "INSERT"
        result["warnings"].append("INSERT queries modify data")
    elif normalized_query.startswith("UPDATE"):
        result["query_type"] = "UPDATE"
        result["warnings"].append("UPDATE queries modify data")
    elif normalized_query.startswith("DELETE"):
        result["query_type"] = "DELETE"
        result["warnings"].append("DELETE queries remove data")
    elif normalized_query.startswith("DROP"):
        result["valid"] = False
        result["query_type"] = "DROP"
        result["errors"].append("DROP queries are not allowed for safety")
    elif normalized_query.startswith("TRUNCATE"):
        result["valid"] = False
        result["query_type"] = "TRUNCATE"
        result["errors"].append("TRUNCATE queries are not allowed for safety")
    elif normalized_query.startswith("ALTER"):
        result["valid"] = False
        result["query_type"] = "ALTER"
        result["errors"].append("ALTER queries are not allowed for safety")
    elif normalized_query.startswith("CREATE"):
        result["query_type"] = "CREATE"
        result["warnings"].append("CREATE queries modify schema")
    else:
        result["query_type"] = "OTHER"
    
    # Check for SQL injection patterns
    dangerous_patterns = [
        r";\s*DROP",
        r";\s*DELETE",
        r";\s*TRUNCATE",
        r";\s*ALTER",
        r"--",
        r"/\*.*\*/",
        r"UNION\s+SELECT",
        r"INTO\s+OUTFILE",
        r"INTO\s+DUMPFILE",
        r"LOAD_FILE",
        r"BENCHMARK\s*\(",
        r"SLEEP\s*\("
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            result["valid"] = False
            result["errors"].append(f"Potentially dangerous pattern detected: {pattern}")
    
    logger.info(f"Query validation result: valid={result['valid']}, type={result['query_type']}")
    return result


def sanitize_table_name(name: str) -> str:
    """
    Sanitize a table name by removing special characters.
    
    Args:
        name: Original table name
    
    Returns:
        Sanitized table name
    """
    if not name:
        return "unnamed_table"
    
    # Remove special characters, keep alphanumeric and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"t_{sanitized}"
    
    # Handle empty result
    if not sanitized:
        sanitized = "unnamed_table"
    
    # Limit length (MySQL max is 64)
    sanitized = sanitized[:64]
    
    logger.debug(f"Sanitized table name: '{name}' -> '{sanitized}'")
    return sanitized.lower()


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Format database schema information for use in LLM prompts.
    
    Args:
        schema_info: Dictionary containing schema information
    
    Returns:
        Formatted schema string
    """
    formatted_lines = []
    
    for table_name, columns in schema_info.items():
        formatted_lines.append(f"Table: {table_name}")
        formatted_lines.append("Columns:")
        
        for col in columns:
            col_str = f"  - {col['name']} ({col['type']})"
            if col.get('primary_key'):
                col_str += " [PRIMARY KEY]"
            if col.get('nullable') is False:
                col_str += " [NOT NULL]"
            formatted_lines.append(col_str)
        
        formatted_lines.append("")
    
    return "\n".join(formatted_lines)


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
    
    Returns:
        True if allowed, False otherwise
    """
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_response(
    success: bool, 
    data: Any = None, 
    message: str = None, 
    error: str = None
) -> Dict[str, Any]:
    """
    Generate a standardized API response.
    
    Args:
        success: Whether the operation was successful
        data: Response data
        message: Success message
        error: Error message
    
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    if error:
        response["error"] = error
    
    return response


class SchemaCache:
    """
    Simple in-memory cache for database schema.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self.ttl_seconds = ttl_seconds
        logger.debug(f"SchemaCache initialized with TTL={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl_seconds:
                logger.debug(f"Cache HIT for key: {key}")
                return self._cache[key]
            else:
                logger.debug(f"Cache EXPIRED for key: {key}")
                del self._cache[key]
                del self._timestamps[key]
        
        logger.debug(f"Cache MISS for key: {key}")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cache value."""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        logger.debug(f"Cache SET for key: {key}")
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._timestamps.clear()
        logger.info("Cache cleared")