import sys
import os

# Get the directory where wsgi.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add it to the Python path if not already there
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("Current directory:", os.getcwd())
print("Files in directory:", [f for f in os.listdir('.') if f.endswith('.py')])

try:
    # Import from main.py
    from main import app
    print("Successfully imported app from main.py")
except Exception as e:
    print(f"Import failed: {e}")
    print(f"Error type: {type(e)}")
    raise

if __name__ == "__main__":
    app.run()