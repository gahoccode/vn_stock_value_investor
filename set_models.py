#!/usr/bin/env python3
"""
Set model configuration to gpt-4o-mini
"""

import os
from pathlib import Path

def set_models_to_gpt_4o_mini():
    """Update .env file to use gpt-4o-mini"""
    env_path = Path(".env")
    
    # Create new .env content with gpt-4o-mini
    new_env_content = """# API Keys for VN Stock Advisor
# Copy this file to .env and replace with your actual API keys

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_REASONING_MODEL=gpt-4o-mini

# Brave Search API Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Firecrawl API Configuration
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
"""
    
    # Write new content
    with open(env_path, 'w') as f:
        f.write(new_env_content)
    
    print("✅ Updated .env file to use gpt-4o-mini")
    print("⚠️  Please update the API keys with your actual values")

if __name__ == "__main__":
    set_models_to_gpt_4o_mini()
