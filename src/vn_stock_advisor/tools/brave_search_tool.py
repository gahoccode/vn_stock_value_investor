"""
Brave Search Tool for VN Stock Advisor
Replaces SerperDevTool with Brave Search API
"""

import os
import requests
import time
from typing import Type, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class BraveSearchInput(BaseModel):
    """Input schema for Brave Search Tool"""
    query: str = Field(..., description="The search query")
    count: int = Field(default=10, description="Number of results to return")
    country: str = Field(default="vn", description="Country code for search results")
    freshness: str = Field(default="", description="Time filter (day, week, month, year)")

class BraveSearchTool(BaseTool):
    """
    Brave Search Tool for web searches using Brave Search API
    
    This tool provides web search capabilities using Brave Search API,
    optimized for Vietnamese stock market research.
    """
    
    name: str = "Brave Search Tool"
    description: str = "Search the web using Brave Search API for Vietnamese stock market information"
    args_schema: Type[BaseModel] = BraveSearchInput
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        # Store API key in a way that doesn't conflict with Pydantic
        self._api_key = api_key or os.environ.get("BRAVE_API_KEY")
        self._base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def _run(self, query: str, count: int = 10, country: str = "ALL", freshness: str = "") -> str:
        """
        Execute search using Brave Search API
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            country: Country code for search results
            freshness: Time filter (day, week, month, year)
        
        Returns:
            Formatted search results as string
        """
        try:
            if not self._api_key:
                return "Error: Brave Search API key not found. Please set BRAVE_API_KEY environment variable."
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self._api_key
            }
            
            # Build minimal parameter set to avoid 422 errors
            params = {
                "q": query,
                "count": min(count, 20)  # Brave API limit
            }
            
            # Only add country if it's a valid Brave API country code
            valid_countries = {'AR', 'AU', 'AT', 'BE', 'BR', 'CA', 'CL', 'DK', 'FI', 'FR', 'DE', 
                             'HK', 'IN', 'ID', 'IT', 'JP', 'KR', 'MY', 'MX', 'NL', 'NZ', 'NO', 
                             'CN', 'PL', 'PT', 'PH', 'RU', 'SA', 'ZA', 'ES', 'SE', 'CH', 'TW', 
                             'TR', 'GB', 'US'}
            
            if country and country in valid_countries:
                params["country"] = country
            
            # Add freshness if provided (valid values: day, week, month, year)
            valid_freshness = {'day', 'week', 'month', 'year'}
            if freshness and freshness in valid_freshness:
                params["freshness"] = freshness
            
            response = requests.get(self._base_url, headers=headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                return "⚠️ Brave Search API rate limit reached. Please wait a moment and try again."
            elif response.status_code == 422:
                # Parameter validation error - use fallback simple query
                try:
                    # Retry with minimal parameters
                    simple_params = {"q": query, "count": min(count, 10)}
                    simple_response = requests.get(self._base_url, headers=headers, params=simple_params)
                    simple_response.raise_for_status()
                    data = simple_response.json()
                except Exception as fallback_error:
                    return f"⚠️ Search service temporarily unavailable. Please try again later."
            
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            results = []
            
            # Web results
            web_results = data.get("web", {}).get("results", [])
            if web_results:
                results.append("🔍 **Web Search Results:**")
                for i, result in enumerate(web_results[:count], 1):
                    title = result.get("title", "No title")
                    url = result.get("url", "")
                    description = result.get("description", "No description")
                    age = result.get("age", "")
                    
                    results.append(f"{i}. **{title}**")
                    if age:
                        results.append(f"   📅 {age}")
                    results.append(f"   {description}")
                    results.append(f"   🔗 {url}")
                    results.append("")
            
            # News results
            news_results = data.get("news", {}).get("results", [])
            if news_results:
                results.append("📰 **News Results:**")
                for i, result in enumerate(news_results[:min(count, 5)], 1):
                    title = result.get("title", "No title")
                    url = result.get("url", "")
                    description = result.get("description", "No description")
                    age = result.get("age", "")
                    source = result.get("meta", {}).get("url", "")
                    
                    results.append(f"{i}. **{title}**")
                    if age:
                        results.append(f"   📅 {age}")
                    if source:
                        results.append(f"   🏢 Source: {source}")
                    results.append(f"   {description}")
                    results.append(f"   🔗 {url}")
                    results.append("")
            
            if not results:
                return "No search results found for the given query."
            
            return "\n".join(results)
            
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                return "⚠️ Brave Search API is temporarily rate limited. Please try again in a few moments."
            elif "422" in str(e):
                return "⚠️ Search parameters need adjustment. Using simplified search..."
            else:
                return f"⚠️ Search service temporarily unavailable: {str(e)}"
        except Exception as e:
            return f"⚠️ Error processing search results: {str(e)}"

# Alternative class for backward compatibility (similar to SerperDevTool interface)
class BraveDevTool(BaseTool):
    """
    Brave Search Tool with Serper-like interface for easy replacement
    """
    
    name: str = "Brave Search Tool"
    description: str = "Search the web using Brave Search API for Vietnamese stock market information"
    args_schema: Type[BaseModel] = BraveSearchInput
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        # Use private attributes to avoid Pydantic field validation issues
        self._api_key = api_key or os.environ.get("BRAVE_API_KEY")
        self._country = kwargs.get("country", "ALL")
        self._locale = kwargs.get("locale", "vn")
        self._location = kwargs.get("location", "Hanoi, Hanoi, Vietnam")
        self._n_results = kwargs.get("n_results", 20)
    
    def _run(self, query: str, **kwargs) -> str:
        """
        Execute search with Serper-like interface
        """
        # Extract parameters similar to SerperDevTool
        count = kwargs.get('n_results', self._n_results)
        country = kwargs.get('country', self._country)
        
        # Create Brave search tool instance
        brave_tool = BraveSearchTool(api_key=self._api_key)
        return brave_tool._run(
            query=query,
            count=count,
            country=country,
            freshness="week"  # Focus on recent news
        )
