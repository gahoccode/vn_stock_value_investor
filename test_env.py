#!/usr/bin/env python3
"""
Test script to verify environment variables are loading correctly
"""

import os
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

print("🔍 Environment Variables Check")
print("=" * 50)

# Set default model values if not provided
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o')
os.environ.setdefault('OPENAI_REASONING_MODEL', 'gpt-4o')

# Check for required API keys
required_keys = [
    'OPENAI_API_KEY',
    'BRAVE_API_KEY',
    'FIRECRAWL_API_KEY'
]
missing_keys = [key for key in required_keys if not os.environ.get(key)]

if missing_keys:
    print("⚠️  Missing API keys:", missing_keys)
    print("Please set these environment variables:")
    for key in missing_keys:
        print(f"  export {key}=your_key_here")
    print("\nOr create a .env file with these keys.")
    sys.exit(1)

print("✅ All required API keys are set!")

# Display configuration
model = os.environ.get('OPENAI_MODEL', 'gpt-4o (default)')
reasoning_model = os.environ.get('OPENAI_REASONING_MODEL', 'gpt-4o (default)')
print(f"✅ OPENAI_MODEL: {model}")
print(f"✅ OPENAI_REASONING_MODEL: {reasoning_model}")

print("\n📁 Current Working Directory:", os.getcwd())
print("📁 .env file exists:", os.path.exists('.env'))

print("\n💡 To fix this, ensure your .env file is in:", os.path.abspath('.'))
