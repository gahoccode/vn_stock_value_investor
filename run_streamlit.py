#!/usr/bin/env python3
"""
VN Stock Advisor Streamlit Launcher
Simple launcher script to run the Streamlit GUI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit app"""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Add src to Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir / 'src')
    
    print("🚀 Launching VN Stock Advisor Streamlit GUI...")
    print("📍 Opening at http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.port=8501',
            '--server.address=localhost'
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try running: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
