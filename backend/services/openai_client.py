"""
OpenAI API client for the Text-to-SQL Chatbot.
Handles all interactions with OpenAI's GPT models.
"""

import os
from typing import Dict, List, Optional, Any

from openai import OpenAI
from openai import APIError, RateLimitError, APIConnectionError

from logger import get_logger
from config import get_config

logger = get_logger(__name__)


class OpenAIClient:
    """Handles OpenAI API interactions."""
    
    def __init__(self):
        self.config = get_config()
        self.client: Optional[OpenAI] = None
        self.model = self.config.OPENAI_MODEL
        self._initialized = False
        logger.info("OpenAIClient created")
    
    def initialize(self) -> bool:
        """Initialize the OpenAI client with API key."""
        try:
            api_key = self.config.OPENAI_API_KEY
            
            if not api_key or api_key == "your-openai-api-key-here":
                logger.error("OpenAI API key not configured")
                return False
            
            self.client = OpenAI(api_key=api_key)
            
            # Test connection with a simple request
            self.client.models.list()
            
            self._initialized = True
            logger.info(f"OpenAI client initialized with model: {self.model}")
            return True
            
        except APIConnectionError as e:
            logger.error(f"Failed to connect to OpenAI API: {e}")
            return False
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized and self.client is not None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        stop: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenAI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in response
            stop: Stop sequences
            
        Returns:
            Dict with success status, response content, and metadata
        """
        result = {
            "success": False,
            "content": None,
            "usage": None,
            "error": None
        }
        
        if not self.is_initialized:
            if not self.initialize():
                result["error"] = "OpenAI client not initialized"
                return result
        
        try:
            logger.info(f"Sending chat completion request ({len(messages)} messages)")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop
            )
            
            result["success"] = True
            result["content"] = response.choices[0].message.content
            result["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Response received. Tokens used: {result['usage']['total_tokens']}")
            
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            result["error"] = "Rate limit exceeded. Please try again later."
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            result["error"] = f"API error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def generate_sql(
        self,
        user_question: str,
        schema_context: str,
        sample_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question.
        
        Args:
            user_question: The user's natural language question
            schema_context: Database schema information
            sample_data: Optional sample data for context
            
        Returns:
            Dict with generated SQL and metadata
        """
        # Build the system prompt
        system_prompt = self._build_system_prompt(schema_context, sample_data)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        # Get completion
        response = self.chat_completion(
            messages=messages,
            temperature=0.0,  # Deterministic for SQL generation
            max_tokens=500
        )
        
        if response["success"]:
            # Extract SQL from response
            sql_query = self._extract_sql(response["content"])
            response["sql"] = sql_query
            response["raw_response"] = response["content"]
        
        return response
    
    def _build_system_prompt(
        self,
        schema_context: str,
        sample_data: Optional[str] = None
    ) -> str:
        """Build the system prompt for SQL generation."""
        
        prompt = f"""You are an expert SQL query generator. Your task is to convert natural language questions into valid SQL queries.

## Database Schema
{schema_context}

## Rules
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use only the tables and columns that exist in the schema above
3. Return ONLY the SQL query, no explanations
4. Use proper SQL syntax for SQLite database
5. If the question cannot be answered with the given schema, respond with: "CANNOT_GENERATE: <reason>"
6. Always use table aliases for clarity in JOIN queries
7. Use appropriate aggregate functions (COUNT, SUM, AVG, MIN, MAX) when needed
8. Include ORDER BY for better result presentation when appropriate
9. Use LIMIT clause for queries that might return many rows

## Important
- Column names are case-sensitive
- Use single quotes for string values
- Date format is 'YYYY-MM-DD'
"""
        
        if sample_data:
            prompt += f"""
## Sample Data (for reference)
{sample_data}
"""
        
        prompt += """
## Response Format
Return only the SQL query, nothing else. Do not include markdown code blocks or explanations.
"""
        
        return prompt
    
    def _extract_sql(self, response: str) -> str:
        """Extract SQL query from response, handling markdown code blocks."""
        if not response:
            return ""
        
        content = response.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```sql"):
            content = content[6:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        return content.strip()
    
    def explain_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        Generate a natural language explanation of a SQL query.
        
        Args:
            sql_query: The SQL query to explain
            
        Returns:
            Dict with explanation
        """
        messages = [
            {
                "role": "system",
                "content": """You are a SQL expert. Explain the given SQL query in simple, 
                non-technical language that a beginner can understand. 
                Break down each part of the query and explain what it does."""
            },
            {
                "role": "user",
                "content": f"Explain this SQL query:\n\n{sql_query}"
            }
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )


# Singleton instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create OpenAIClient singleton."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client