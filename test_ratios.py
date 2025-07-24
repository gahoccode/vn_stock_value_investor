#!/usr/bin/env python3
"""
Test script to verify financial ratio extraction is working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vn_stock_advisor.tools.custom_tool import FundDataTool

def test_ratio_extraction():
    """Test financial ratio extraction for a known Vietnamese stock"""
    
    # Test with a well-known Vietnamese stock
    test_symbols = ['VIC', 'VNM', 'FPT', 'HPG']
    
    tool = FundDataTool()
    
    print("🔍 Testing Financial Ratio Extraction...")
    print("=" * 50)
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 Testing symbol: {symbol}")
            print("-" * 30)
            
            result = tool._run(symbol)
            print(result)
            
            # Check if ratios are properly extracted
            if "N/A" not in result or result.count("N/A") < 5:
                print(f"✅ {symbol}: Ratios extracted successfully")
            else:
                print(f"⚠️  {symbol}: Some ratios missing (check data availability)")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
        
        print()

if __name__ == "__main__":
    test_ratio_extraction()
