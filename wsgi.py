import os
import sys

print("Current directory:", os.getcwd())
print("Files in directory:", [f for f in os.listdir('.') if f.endswith('.py')])

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import main
    print("Successfully imported App module")
    from main import app
    print("Successfully imported app from App")
except Exception as e:
    print(f"Import failed: {e}")
    print(f"Error type: {type(e)}")
    raise

if __name__ == "__main__":
    app.run()