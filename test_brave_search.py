#!/usr/bin/env python3
"""
Test script to debug Brave Search Tool issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vn_stock_advisor.tools.brave_search_tool import BraveSearchTool, BraveDevTool

def test_brave_search():
    """Test Brave Search Tool functionality"""
    
    print("🔍 Testing Brave Search Tool...")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.environ.get("BRAVE_API_KEY")
    print(f"BRAVE_API_KEY found: {'✅ Yes' if api_key else '❌ No'}")
    if api_key:
        print(f"API Key: {api_key[:10]}...")
    
    # Test BraveSearchTool
    print("\n📊 Testing BraveSearchTool...")
    try:
        tool = BraveSearchTool()
        result = tool._run("Vietnam stock market news VIC")
        print("✅ BraveSearchTool working")
        print(f"Result length: {len(result)} characters")
        if len(result) > 100:
            print("Sample:", result[:200] + "...")
        else:
            print("Full result:", result)
    except Exception as e:
        print(f"❌ BraveSearchTool error: {e}")
    
    # Test BraveDevTool (Serper-like interface)
    print("\n📊 Testing BraveDevTool...")
    try:
        tool = BraveDevTool()
        result = tool._run("Vietnam stock market analysis VNM")
        print("✅ BraveDevTool working")
        print(f"Result length: {len(result)} characters")
        if len(result) > 100:
            print("Sample:", result[:200] + "...")
        else:
            print("Full result:", result)
    except Exception as e:
        print(f"❌ BraveDevTool error: {e}")

if __name__ == "__main__":
    test_brave_search()
