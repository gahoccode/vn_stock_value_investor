#!/usr/bin/env python3
"""
Simple test for Brave Search Tool
"""

import os
import requests

def test_brave_api_direct():
    """Test Brave API directly"""
    
    api_key = os.environ.get("BRAVE_API_KEY")
    print(f"API Key: {api_key[:10]}...")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    params = {
        "q": "Vietnam stock market VIC",
        "count": 5,
        "country": "ALL",
        "search_lang": "vi"
    }
    
    try:
        response = requests.get("https://api.search.brave.com/res/v1/web/search", 
                              headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('web', {}).get('results', []))} results")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_brave_api_direct()
