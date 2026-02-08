"""
RAG (Retrieval Augmented Generation) Engine for Text-to-SQL Chatbot.
Uses ChromaDB for vector storage and retrieval of schema context.
"""

import os
import hashlib
from typing import Dict, List, Optional, Any

import chromadb
from chromadb.config import Settings

from logger import get_logger
from config import get_config
from services.db_connector import get_db_connector, DatabaseConnector

logger = get_logger(__name__)


class RAGEngine:
    """
    Handles RAG operations for context-aware SQL generation.
    Stores schema information as embeddings for retrieval.
    """
    
    def __init__(self, db_connector: DatabaseConnector = None):
        self.config = get_config()
        self.db = db_connector or get_db_connector()
        self.chroma_client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self._initialized = False
        
        # Collection name for schema embeddings
        self.collection_name = "schema_embeddings"
        
        logger.info("RAGEngine created")
    
    def initialize(self) -> bool:
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            persist_dir = self.config.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)
            
            # Initialize ChromaDB with persistence
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Database schema embeddings for Text-to-SQL"}
            )
            
            self._initialized = True
            logger.info(f"RAGEngine initialized. Collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAGEngine: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        """Check if RAG engine is initialized."""
        return self._initialized and self.collection is not None
    
    def index_schema(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index the current database schema into ChromaDB.
        
        Args:
            force_reindex: If True, delete existing and reindex
            
        Returns:
            Dict with indexing results
        """
        result = {
            "success": False,
            "tables_indexed": 0,
            "documents_added": 0,
            "error": None
        }
        
        try:
            if not self.is_initialized:
                if not self.initialize():
                    result["error"] = "Failed to initialize RAG engine"
                    return result
            
            # Connect to database if not connected
            if not self.db.is_connected:
                self.db.connect()
            
            # Get current schema hash to check if reindexing needed
            full_schema = self.db.get_full_schema()
            schema_hash = self._compute_schema_hash(full_schema)
            
            # Check if already indexed (unless force reindex)
            if not force_reindex:
                existing = self.collection.get(ids=[f"schema_hash_{schema_hash}"])
                if existing and existing["ids"]:
                    logger.info("Schema already indexed, skipping")
                    result["success"] = True
                    result["message"] = "Schema already indexed"
                    return result
            
            # Clear existing documents if force reindex
            if force_reindex:
                self._clear_collection()
            
            # Prepare documents for indexing
            documents = []
            metadatas = []
            ids = []
            
            for table_name, schema in full_schema.items():
                # Create document for the table
                table_doc = self._create_table_document(table_name, schema)
                documents.append(table_doc)
                metadatas.append({
                    "type": "table",
                    "table_name": table_name,
                    "column_count": len(schema.get("columns", []))
                })
                ids.append(f"table_{table_name}")
                
                # Create documents for each column
                for col in schema.get("columns", []):
                    col_doc = self._create_column_document(table_name, col)
                    documents.append(col_doc)
                    metadatas.append({
                        "type": "column",
                        "table_name": table_name,
                        "column_name": col["name"],
                        "column_type": col["type"]
                    })
                    ids.append(f"column_{table_name}_{col['name']}")
            
            # Add schema hash document
            documents.append(f"Schema hash: {schema_hash}")
            metadatas.append({"type": "hash"})
            ids.append(f"schema_hash_{schema_hash}")
            
            # Add sample data documents
            sample_docs = self._create_sample_data_documents(full_schema)
            for doc, meta, doc_id in sample_docs:
                documents.append(doc)
                metadatas.append(meta)
                ids.append(doc_id)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            result["success"] = True
            result["tables_indexed"] = len(full_schema)
            result["documents_added"] = len(documents)
            logger.info(f"Indexed {len(documents)} documents from {len(full_schema)} tables")
            
        except Exception as e:
            logger.error(f"Error indexing schema: {e}")
            result["error"] = str(e)
        
        return result
    
    def retrieve_context(
        self,
        query: str,
        n_results: int = 10,
        include_samples: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve relevant schema context for a query.
        
        Args:
            query: User's natural language query
            n_results: Number of results to retrieve
            include_samples: Whether to include sample data
            
        Returns:
            Dict with retrieved context
        """
        result = {
            "success": False,
            "context": "",
            "tables": [],
            "columns": [],
            "error": None
        }
        
        try:
            if not self.is_initialized:
                if not self.initialize():
                    result["error"] = "RAG engine not initialized"
                    return result
            
            # Query the collection
            query_result = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not query_result or not query_result["documents"]:
                result["error"] = "No results found"
                return result
            
            # Process results
            tables = set()
            columns = []
            context_parts = []
            
            for doc, meta, distance in zip(
                query_result["documents"][0],
                query_result["metadatas"][0],
                query_result["distances"][0]
            ):
                if meta["type"] == "table":
                    tables.add(meta["table_name"])
                    context_parts.append(doc)
                elif meta["type"] == "column":
                    tables.add(meta["table_name"])
                    columns.append({
                        "table": meta["table_name"],
                        "column": meta["column_name"],
                        "type": meta["column_type"],
                        "relevance": 1 - distance  # Convert distance to similarity
                    })
                    context_parts.append(doc)
            
            # Build context string
            context = self._build_context_string(list(tables), context_parts)
            
            result["success"] = True
            result["context"] = context
            result["tables"] = list(tables)
            result["columns"] = columns
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            result["error"] = str(e)
        
        return result
    
    def get_relevant_schema(
        self,
        query: str,
        max_tables: int = 5
    ) -> str:
        """
        Get relevant schema as formatted string for prompts.
        
        Args:
            query: User's query
            max_tables: Maximum tables to include
            
        Returns:
            Formatted schema string
        """
        # First, retrieve context
        context_result = self.retrieve_context(query, n_results=20)
        
        if not context_result["success"]:
            # Fallback to full schema
            return self.db.get_schema_for_prompt()
        
        # Get full schema for relevant tables
        relevant_tables = context_result["tables"][:max_tables]
        
        if not relevant_tables:
            return self.db.get_schema_for_prompt()
        
        # Build schema string for relevant tables
        lines = ["Relevant Database Schema:", "=" * 40]
        
        for table_name in relevant_tables:
            schema = self.db.get_table_schema(table_name)
            lines.append(f"\nTable: {table_name}")
            for col in schema.get("columns", []):
                lines.append(f"  - {col['name']} ({col['type']})")
        
        return "\n".join(lines)
    
    def _create_table_document(
        self,
        table_name: str,
        schema: Dict
    ) -> str:
        """Create a document string for a table."""
        columns = schema.get("columns", [])
        col_descriptions = [
            f"{col['name']} ({col['type']})" 
            for col in columns
        ]
        
        return (
            f"Table '{table_name}' contains {len(columns)} columns: "
            f"{', '.join(col_descriptions)}. "
            f"This table can be queried using SELECT statements."
        )
    
    def _create_column_document(
        self,
        table_name: str,
        column: Dict
    ) -> str:
        """Create a document string for a column."""
        col_name = column["name"]
        col_type = column["type"]
        
        # Add semantic hints based on column name
        hints = []
        name_lower = col_name.lower()
        
        if "id" in name_lower:
            hints.append("identifier/primary key")
        if "name" in name_lower:
            hints.append("text/name field")
        if "date" in name_lower or "time" in name_lower:
            hints.append("datetime field")
        if "price" in name_lower or "amount" in name_lower or "cost" in name_lower:
            hints.append("monetary value")
        if "count" in name_lower or "quantity" in name_lower:
            hints.append("numeric count")
        if "email" in name_lower:
            hints.append("email address")
        if "status" in name_lower or "state" in name_lower:
            hints.append("status/state field")
        if "is_" in name_lower or "has_" in name_lower:
            hints.append("boolean flag")
        
        hint_str = f" Used for: {', '.join(hints)}." if hints else ""
        
        return (
            f"Column '{col_name}' in table '{table_name}' "
            f"has type {col_type}.{hint_str}"
        )
    
    def _create_sample_data_documents(
        self,
        full_schema: Dict,
        sample_rows: int = 2
    ) -> List[tuple]:
        """Create documents from sample data."""
        documents = []
        
        for table_name in full_schema:
            try:
                sample = self.db.get_sample_data(table_name, sample_rows)
                if sample:
                    doc = f"Sample data from {table_name}: {sample}"
                    meta = {
                        "type": "sample",
                        "table_name": table_name
                    }
                    doc_id = f"sample_{table_name}"
                    documents.append((doc, meta, doc_id))
            except Exception as e:
                logger.warning(f"Could not get sample for {table_name}: {e}")
        
        return documents
    
    def _build_context_string(
        self,
        tables: List[str],
        context_parts: List[str]
    ) -> str:
        """Build a formatted context string."""
        lines = [
            "Retrieved Context:",
            "-" * 40,
            f"Relevant tables: {', '.join(tables)}",
            "",
            "Details:"
        ]
        
        for part in context_parts[:10]:  # Limit context size
            lines.append(f"- {part}")
        
        return "\n".join(lines)
    
    def _compute_schema_hash(self, schema: Dict) -> str:
        """Compute hash of schema for change detection."""
        schema_str = str(sorted(schema.items()))
        return hashlib.md5(schema_str.encode()).hexdigest()[:16]
    
    def _clear_collection(self):
        """Clear all documents from collection."""
        try:
            # Get all IDs and delete
            existing = self.collection.get()
            if existing and existing["ids"]:
                self.collection.delete(ids=existing["ids"])
            logger.info("Collection cleared")
        except Exception as e:
            logger.warning(f"Error clearing collection: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG index."""
        if not self.is_initialized:
            return {"initialized": False}
        
        try:
            count = self.collection.count()
            return {
                "initialized": True,
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.config.CHROMA_PERSIST_DIR
            }
        except Exception as e:
            return {"initialized": True, "error": str(e)}


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAGEngine singleton."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine