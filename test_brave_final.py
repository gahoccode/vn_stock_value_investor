#!/usr/bin/env python3
"""
Final test for Brave Search Tool
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vn_stock_advisor.tools.brave_search_tool import BraveSearchTool, BraveDevTool

def test_final():
    print("🎯 Final Brave Search Tool Test")
    print("=" * 40)
    
    # Test with minimal parameters
    try:
        print("\n1. Testing BraveSearchTool with minimal params...")
        tool = BraveSearchTool()
        
        # Test with a simple query and minimal parameters
        result = tool._run("Vietnam stock market VIC", count=3)
        
        if "Error" in result and "API key" in result:
            print(f"   ⚠️  {result}")
        elif "Error" in result:
            print(f"   ⚠️  API Error: {result}")
        else:
            print(f"   ✅ Success! Got {len(result)} characters of results")
            lines = result.split('\n')
            for line in lines[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"   {line}")
                    
    except Exception as e:
        print(f"   ❌ Tool Error: {e}")
    
    # Test BraveDevTool
    try:
        print("\n2. Testing BraveDevTool...")
        tool = BraveDevTool()
        result = tool._run("Vietnam stock news")
        
        if "Error" in result and "API key" in result:
            print(f"   ⚠️  {result}")
        elif "Error" in result:
            print(f"   ⚠️  API Error: {result}")
        else:
            print(f"   ✅ Success! Got {len(result)} characters of results")
            lines = result.split('\n')
            for line in lines[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"   {line}")
                    
    except Exception as e:
        print(f"   ❌ Tool Error: {e}")

if __name__ == "__main__":
    test_final()
