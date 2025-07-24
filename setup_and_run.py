#!/usr/bin/env python3
"""
VN Stock Advisor - Complete Setup and Run Script
Handles virtual environment activation and Streamlit launch
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup the environment and run Streamlit"""
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Add src to Python path
    src_path = str(project_dir / 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = src_path
    
    # Check if .env file exists
    env_file = project_dir / '.env'
    if not env_file.exists():
        print("⚠️  .env file not found. Please create one with your API keys.")
        print("Example .env file:")
        required_keys = [
            'OPENAI_API_KEY',
            'OPENAI_MODEL',
            'OPENAI_REASONING_MODEL',
            'BRAVE_API_KEY',
            'FIRECRAWL_API_KEY'
        ]
        for key in required_keys:
            print(f"{key}=your_{key.lower().replace('_', '')}_api_key")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import streamlit
        import crewai
        import vnstock
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing missing packages...")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit'], check=True)
        print("✅ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting VN Stock Advisor Streamlit GUI...")
        print("📍 Opening at http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the server")
        print()
        
        # Run streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.port=8501',
            '--server.address=localhost'
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try running: python -m streamlit run streamlit_app.py")

def main():
    """Main function"""
    print("🔧 VN Stock Advisor - Streamlit Setup")
    print("=" * 40)
    
    # Setup environment
    if not setup_environment():
        return
    
    # Check dependencies
    if not check_dependencies():
        if not install_dependencies():
            print("❌ Could not install required dependencies")
            return
    
    # Run Streamlit
    run_streamlit()

if __name__ == "__main__":
    main()
