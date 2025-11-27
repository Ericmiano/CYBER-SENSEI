import os
import sys
from unittest.mock import patch

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_security_module():
    print("Testing security module configuration...")
    
    # Case 1: Development (default) - Should generate key
    if "app.security" in sys.modules:
        del sys.modules["app.security"]
    
    os.environ.pop("JWT_SECRET_KEY", None)
    os.environ["ENV"] = "development"
    
    try:
        import app.security
        print(f"✓ Development mode: Generated key successfully: {app.security.SECRET_KEY[:5]}...")
    except Exception as e:
        print(f"✗ Development mode failed: {e}")
        return False

    # Case 2: Production with missing key - Should fail
    if "app.security" in sys.modules:
        del sys.modules["app.security"]
        
    os.environ["ENV"] = "production"
    os.environ.pop("JWT_SECRET_KEY", None)
    
    try:
        import app.security
        print("✗ Production mode: Failed to raise error for missing key")
        return False
    except ValueError as e:
        print(f"✓ Production mode: Correctly raised error: {e}")
    except Exception as e:
        print(f"✗ Production mode: Raised wrong error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_security_module()
    sys.exit(0 if success else 1)
