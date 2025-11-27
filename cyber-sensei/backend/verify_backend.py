import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

print("--- STARTING VERIFICATION ---")
try:
    print("Attempting to import app.main...")
    from app.main import app
    print("Successfully imported app.main")
except Exception as e:
    print(f"Error importing app.main: {e}")
    traceback.print_exc()
print("--- END VERIFICATION ---")
