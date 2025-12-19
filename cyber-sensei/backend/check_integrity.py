import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import *

def check_models():
    print("Checking database models integrity...")
    try:
        # Create in-memory SQLite database to test schema generation
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=engine)
        print("✅ Schema creation successful - All models are valid.")
        return True
    except Exception as e:
        print(f"❌ Model check failed: {str(e)}")
        # Print full traceback for debugging if needed
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if check_models():
        sys.exit(0)
    else:
        sys.exit(1)
