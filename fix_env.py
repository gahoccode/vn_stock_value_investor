#!/usr/bin/env python3
"""
Fix .env file configuration issues
"""

import os
from pathlib import Path

def fix_env_file():
    """Fix the .env file with correct model names"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found. Creating from .env.example...")
        # Copy from .env.example
        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as src, open(env_path, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env from .env.example")
        else:
            print("❌ .env.example not found")
            return
    
    # Read current .env content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Fix model names
    fixed_content = content.replace("gpt-4-mini", "gpt-4o").replace("gpt-4o-mini", "gpt-4o")
    
    # Write back fixed content
    with open(env_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed model names in .env file")
    
    # Show current configuration
    print("\n📋 Current .env configuration:")
    print("=" * 30)
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if 'KEY' in line.upper():
                    key, value = line.strip().split('=', 1)
                    print(f"{key}=***")
                else:
                    print(line.strip())

if __name__ == "__main__":
    fix_env_file()
