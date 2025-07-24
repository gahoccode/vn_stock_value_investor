#!/usr/bin/env python3
"""
Direct test for Brave Search Tool
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Test the tools directly
from vn_stock_advisor.tools.brave_search_tool import BraveSearchTool, BraveDevTool

def test_direct():
    print("Testing Brave Search Tools...")
    
    # Test BraveSearchTool
    try:
        print("\n1. Testing BraveSearchTool...")
        tool = BraveSearchTool()
        print(f"   API Key: {tool._api_key[:10] if tool._api_key else 'None'}")
        
        # Test with a simple query
        result = tool._run("Vietnam stock market", count=3, country="ALL")
        print(f"   Success! Result length: {len(result)}")
        if len(result) > 100:
            print("   Sample:", result[:300] + "...")
        else:
            print("   Result:", result)
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test BraveDevTool
    try:
        print("\n2. Testing BraveDevTool...")
        tool = BraveDevTool()
        print(f"   API Key: {tool._api_key[:10] if tool._api_key else 'None'}")
        
        # Test with a simple query
        result = tool._run("Vietnam stock news")
        print(f"   ✅ Success! Result length: {len(result)}")
        if len(result) > 100:
            print("   Sample:", result[:300] + "...")
        else:
            print("   Result:", result)
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
