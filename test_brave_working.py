#!/usr/bin/env python3
"""
Working test for Brave Search Tool with fixed parameters
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vn_stock_advisor.tools.brave_search_tool import BraveSearchTool

def test_working():
    print("🎯 Testing Brave Search Tool with Fixed Parameters")
    print("=" * 50)
    
    # Test with minimal, safe parameters
    try:
        tool = BraveSearchTool()
        
        print("\n✅ Testing with minimal parameters...")
        result = tool._run("Vietnam stock market", count=5)
        
        if "Error" in result and "API key" in result:
            print("❌ API Key Issue:", result)
        elif "⚠️" in result:
            print("⚠️  API Response:", result)
        else:
            print("✅ SUCCESS! Search completed successfully")
            print(f"📊 Result length: {len(result)} characters")
            
            # Show sample results
            lines = result.split('\n')
            for line in lines[:8]:
                if line.strip():
                    print(f"   {line}")
                    
            if len(lines) > 8:
                print("   ... (more results)")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_working()
