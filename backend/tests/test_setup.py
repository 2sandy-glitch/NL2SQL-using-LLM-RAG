"""
Test file to verify project setup is correct.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from config import get_config
        print("  [OK] config module imported successfully")
        
        from logger import get_logger, setup_logging
        print("  [OK] logger module imported successfully")
        
        from services.utils import validate_sql_query, sanitize_table_name
        print("  [OK] utils module imported successfully")
        
        print("\n[OK] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config import get_config
        config = get_config()
        
        assert hasattr(config, 'APP_NAME'), "Missing APP_NAME"
        assert hasattr(config, 'DB_HOST'), "Missing DB_HOST"
        assert hasattr(config, 'OPENAI_API_KEY'), "Missing OPENAI_API_KEY"
        
        print(f"  [OK] App Name: {config.APP_NAME}")
        print(f"  [OK] Debug Mode: {config.DEBUG}")
        print(f"  [OK] Log Level: {config.LOG_LEVEL}")
        
        print("\n[OK] Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Configuration error: {e}")
        return False


def test_logger():
    """Test logger setup."""
    print("\nTesting logger...")
    
    try:
        from logger import get_logger, setup_logging
        
        # Setup logging
        setup_logging()
        
        # Get a logger
        logger = get_logger("test")
        
        # Test logging
        logger.info("Test info message")
        logger.debug("Test debug message")
        
        print("  [OK] Logger initialized successfully")
        print("  [OK] Log messages written successfully")
        
        # Check if log directory exists
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if os.path.exists(log_dir):
            print(f"  [OK] Log directory exists: {log_dir}")
        
        print("\n[OK] Logger working correctly!")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Logger error: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from services.utils import validate_sql_query, sanitize_table_name
        
        # Test SQL validation - valid SELECT
        result = validate_sql_query("SELECT * FROM users")
        assert result["valid"] == True, f"Expected valid=True, got {result}"
        assert result["query_type"] == "SELECT", f"Expected SELECT, got {result['query_type']}"
        print("  [OK] SQL validation working (SELECT query)")
        
        # Test dangerous query detection - DROP
        result = validate_sql_query("DROP TABLE users;")
        assert result["valid"] == False, f"Expected valid=False for DROP, got {result}"
        print("  [OK] Dangerous query detection working (DROP blocked)")
        
        # Test SQL injection detection
        result = validate_sql_query("SELECT * FROM users; DROP TABLE users;")
        assert result["valid"] == False, f"Expected valid=False for injection, got {result}"
        print("  [OK] SQL injection detection working")
        
        # Test table name sanitization
        sanitized = sanitize_table_name("My Table Name!")
        assert sanitized == "my_table_name", f"Expected 'my_table_name', got '{sanitized}'"
        print("  [OK] Table name sanitization working")
        
        # Test table name with numbers at start
        sanitized = sanitize_table_name("123table")
        assert sanitized.startswith("t_"), f"Expected to start with 't_', got '{sanitized}'"
        print("  [OK] Table name number prefix handling working")
        
        print("\n[OK] Utility functions working successfully!")
        return True
        
    except AssertionError as e:
        print(f"  [FAIL] Assertion error: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Utility error: {e}")
        return False


def main():
    """Run all setup tests."""
    print("=" * 60)
    print("    TEXT-TO-SQL CHATBOT - SETUP VERIFICATION")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_config()
    all_passed &= test_logger()
    all_passed &= test_utils()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  [SUCCESS] ALL TESTS PASSED! Phase 1 Setup is complete.")
        print("  Ready to proceed to Phase 2: Database Setup & Data Loader")
    else:
        print("  [FAILED] SOME TESTS FAILED. Please check the errors above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)