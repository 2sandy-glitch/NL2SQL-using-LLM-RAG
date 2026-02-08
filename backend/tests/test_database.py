'EOF'
"""
Test file for database connection and data loading.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_database_connection():
    print("\nTesting database connection...")
    try:
        from services.db_connector import get_db_connector
        
        db = get_db_connector()
        
        if db.connect():
            print("  [OK] Database connection successful")
            
            result = db.execute_query("SELECT 1 as test")
            if result["success"]:
                print("  [OK] Test query executed successfully")
                return True
            else:
                print("  [FAIL] Test query failed")
                return False
        else:
            print("  [FAIL] Could not connect to database")
            return False
    except Exception as e:
        print(f"  [FAIL] Database connection error: {e}")
        return False


def test_data_loader():
    print("\nTesting data loader...")
    try:
        from services.data_loader import get_data_loader
        
        loader = get_data_loader()
        print("  [OK] DataLoader initialized")
        
        sample_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample", "customers.csv")
        
        if os.path.exists(sample_csv):
            preview = loader.preview_file(sample_csv, rows=5)
            
            if preview["success"]:
                print("  [OK] File preview successful")
                print(f"      - Rows: {preview['total_rows']}")
                print(f"      - Columns: {preview['total_columns']}")
                return True
            else:
                print("  [FAIL] File preview failed")
                return False
        else:
            print("  [WARN] Sample data not found")
            return True
    except Exception as e:
        print(f"  [FAIL] Data loader error: {e}")
        return False


def test_load_data():
    print("\nTesting data loading to database...")
    try:
        from services.data_loader import get_data_loader
        from services.db_connector import get_db_connector
        
        db = get_db_connector()
        if not db.is_connected:
            db.connect()
        
        loader = get_data_loader()
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample")
        
        for table in ["customers", "products", "orders", "employees"]:
            csv_path = os.path.join(base_path, f"{table}.csv")
            if os.path.exists(csv_path):
                result = loader.load_file_to_db(csv_path, table, "replace")
                if result["success"]:
                    print(f"  [OK] Loaded {result['row_count']} rows to '{table}'")
                else:
                    print(f"  [FAIL] Failed to load {table}")
                    return False
        
        tables = db.get_all_tables()
        print(f"  [OK] Total tables in database: {len(tables)}")
        
        schema = db.get_schema_for_prompt()
        print(f"  [OK] Schema generated ({len(schema)} chars)")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Data loading error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("    TEXT-TO-SQL CHATBOT - DATABASE TESTS (PHASE 2)")
    print("=" * 60)
    
    all_passed = True
    all_passed &= test_database_connection()
    all_passed &= test_data_loader()
    all_passed &= test_load_data()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  [SUCCESS] ALL DATABASE TESTS PASSED!")
        print("  Ready to proceed to Phase 3: AI Model Integration")
    else:
        print("  [WARNING] Some tests failed. Check errors above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    main()
