
"""
Data loader module for processing files and loading to database.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import pandas as pd
import numpy as np

from logger import get_logger
from config import get_config
from services.db_connector import get_db_connector, DatabaseConnector

logger = get_logger(__name__)


def sanitize_table_name(name: str) -> str:
    if not name:
        return "unnamed_table"
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    if sanitized and sanitized[0].isdigit():
        sanitized = f"t_{sanitized}"
    return sanitized.lower()[:64] if sanitized else "unnamed_table"


class DataLoader:
    """Handles loading data from files into the database."""
    
    def __init__(self, db_connector: DatabaseConnector = None):
        self.config = get_config()
        self.db = db_connector or get_db_connector()
        os.makedirs(self.config.UPLOAD_FOLDER, exist_ok=True)
        logger.info("DataLoader initialized")
    
    def _infer_sql_type(self, series: pd.Series) -> str:
        if pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"
        if pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        if pd.api.types.is_float_dtype(series):
            return "REAL"
        max_len = series.astype(str).str.len().max()
        if pd.isna(max_len):
            max_len = 255
        return f"VARCHAR({int(max_len) + 50})" if max_len <= 255 else "TEXT"
    
    def _generate_schema(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        columns = []
        for col_name in df.columns:
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(col_name))
            safe_name = re.sub(r"_+", "_", safe_name).strip("_").lower()
            if safe_name and safe_name[0].isdigit():
                safe_name = f"col_{safe_name}"
            if not safe_name:
                safe_name = f"column_{len(columns)}"
            columns.append({
                "original_name": col_name,
                "name": safe_name,
                "type": self._infer_sql_type(df[col_name]),
                "nullable": df[col_name].isna().any()
            })
        return {
            "table_name": sanitize_table_name(table_name),
            "columns": columns,
            "row_count": len(df),
            "generated_at": datetime.now().isoformat()
        }
    
    def read_file(self, file_path: str, sheet_name: str = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        logger.info(f"Reading: {file_path}")
        try:
            if not os.path.exists(file_path):
                return None, f"File not found: {file_path}"
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path, sheet_name=sheet_name) if sheet_name else pd.read_excel(file_path)
            elif ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                return None, f"Unsupported format: {ext}"
            
            logger.info(f"Read {len(df)} rows, {len(df.columns)} columns")
            return df, None
        except Exception as e:
            logger.error(f"Read error: {e}")
            return None, str(e)
    
    def get_excel_sheets(self, file_path: str) -> List[str]:
        try:
            return pd.ExcelFile(file_path).sheet_names
        except Exception as e:
            logger.error(f"Excel sheets error: {e}")
            return []
    
    def load_dataframe_to_db(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> Dict[str, Any]:
        logger.info(f"Loading to table: {table_name}")
        result = {
            "success": False,
            "table_name": None,
            "row_count": 0,
            "column_count": 0,
            "schema": None,
            "error": None
        }
        
        try:
            if not self.db.is_connected:
                self.db.connect()
            
            schema = self._generate_schema(df, table_name)
            safe_table = schema["table_name"]
            
            col_map = {c["original_name"]: c["name"] for c in schema["columns"]}
            df_renamed = df.rename(columns=col_map)
            
            df_renamed.to_sql(name=safe_table, con=self.db.engine, if_exists=if_exists, index=False, chunksize=1000)
            
            result["success"] = True
            result["table_name"] = safe_table
            result["row_count"] = len(df)
            result["column_count"] = len(df.columns)
            result["schema"] = schema
            logger.info(f"Loaded {len(df)} rows to '{safe_table}'")
        except Exception as e:
            logger.error(f"Load error: {e}")
            result["error"] = str(e)
        
        return result
    
    def load_file_to_db(self, file_path: str, table_name: str = None, sheet_name: str = None, if_exists: str = "replace") -> Dict[str, Any]:
        df, error = self.read_file(file_path, sheet_name)
        if error:
            return {"success": False, "error": error}
        
        if not table_name:
            base = os.path.splitext(os.path.basename(file_path))[0]
            table_name = sanitize_table_name(base)
        
        return self.load_dataframe_to_db(df, table_name, if_exists)
    
    def preview_file(self, file_path: str, sheet_name: str = None, rows: int = 10) -> Dict[str, Any]:
        df, error = self.read_file(file_path, sheet_name)
        if error:
            return {"success": False, "error": error}
        
        schema = self._generate_schema(df, "preview")
        return {
            "success": True,
            "preview_data": df.head(rows).to_dict(orient="records"),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": [c["name"] for c in schema["columns"]],
            "schema": schema
        }


_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader