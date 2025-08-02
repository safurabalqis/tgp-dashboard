import os

def create_flask_dashboard():
    """Auto-create complete Flask dashboard structure"""
    
    # Create directories
    directories = [
        "app",
        "app/templates",
        "app/static",
        "app/static/css",
        "app/static/js",
        "app/static/img",
        "app/routes",
        "app/models",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py for Python packages
        if directory.startswith('app'):
            with open(f"{directory}/__init__.py", "w") as f:
                f.write("")
    
    print("✅ Project structure created successfully!")
    print("📁 Folders created:")
    for directory in directories:
        print(f"   - {directory}/")

if __name__ == "__main__":
    create_flask_dashboard()