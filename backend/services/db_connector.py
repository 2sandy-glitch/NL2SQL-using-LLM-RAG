
"""
Database connection and query execution module.
"""

import time
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from logger import get_logger
from config import get_config

logger = get_logger(__name__)


class DatabaseConnector:
    """Handles database connections and query execution."""
    
    def __init__(self, db_uri: str = None):
        self.config = get_config()
        self.db_uri = db_uri or self.config.DATABASE_URI
        self.engine: Optional[Engine] = None
        self._connected = False
        logger.info("DatabaseConnector initialized")
    
    def connect(self) -> bool:
        try:
            logger.info("Connecting to database...")
            self.engine = create_engine(self.db_uri, pool_pre_ping=True, echo=False)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self._connected = True
            logger.info("Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        if self.engine:
            self.engine.dispose()
            self._connected = False
            logger.info("Database disconnected")
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self.engine is not None
    
    @contextmanager
    def get_connection(self):
        if not self.is_connected:
            self.connect()
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()
    
    def execute_query(self, sql_query: str, params: Dict = None) -> Dict[str, Any]:
        logger.info(f"Executing: {sql_query[:80]}...")
        start_time = time.time()
        
        result = {
            "success": False,
            "data": None,
            "row_count": 0,
            "columns": [],
            "execution_time": 0,
            "error": None
        }
        
        try:
            if not self.is_connected:
                self.connect()
            
            is_select = sql_query.strip().upper().startswith("SELECT")
            
            with self.get_connection() as conn:
                if is_select:
                    df = pd.read_sql(text(sql_query), conn, params=params)
                    result["data"] = df.to_dict(orient="records")
                    result["row_count"] = len(df)
                    result["columns"] = list(df.columns)
                else:
                    exec_result = conn.execute(text(sql_query), params or {})
                    conn.commit()
                    result["row_count"] = exec_result.rowcount
                    result["data"] = {"affected_rows": exec_result.rowcount}
            
            result["success"] = True
        except Exception as e:
            logger.error(f"Query error: {e}")
            result["error"] = str(e)
        finally:
            result["execution_time"] = round(time.time() - start_time, 4)
        
        return result
    
    def get_all_tables(self) -> List[str]:
        try:
            if not self.is_connected:
                self.connect()
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        try:
            if not self.is_connected:
                self.connect()
            inspector = inspect(self.engine)
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                })
            return {"table_name": table_name, "columns": columns}
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return {}
    
    def get_full_schema(self) -> Dict[str, Any]:
        tables = self.get_all_tables()
        return {table: self.get_table_schema(table) for table in tables}
    
    def get_schema_for_prompt(self) -> str:
        full_schema = self.get_full_schema()
        if not full_schema:
            return "No tables found."
        
        lines = ["Database Schema:", "=" * 40]
        for table_name, schema in full_schema.items():
            lines.append(f"\nTable: {table_name}")
            for col in schema.get("columns", []):
                lines.append(f"  - {col['name']} ({col['type']})")
        return "\n".join(lines)
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        result = self.execute_query(f"SELECT * FROM `{table_name}` LIMIT {limit}")
        return result["data"] if result["success"] else []


_db_connector: Optional[DatabaseConnector] = None


def get_db_connector() -> DatabaseConnector:
    global _db_connector
    if _db_connector is None:
        _db_connector = DatabaseConnector()
    return _db_connector
