import os
import sys
import subprocess


def ensure_dependencies():
    """Checks and installs required packages if missing."""
    required_packages = ["fastapi", "uvicorn", "pydantic"]
    missing = []
    
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def main():
    print("==================================================")
    print("   TaskCraft Full-Stack To-Do Application")
    print("==================================================")
    
    ensure_dependencies()
    
    import uvicorn
    
    host = "127.0.0.1"
    port = 8000
    
    print(f"\n🚀 Server starting on: http://{host}:{port}")
    print(f"📄 Interactive API Docs: http://{host}:{port}/docs")
    print("💡 Press Ctrl+C to stop the server.\n")
    
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
