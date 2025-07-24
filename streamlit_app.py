"""
VN Stock Advisor - Streamlit GUI
A user-friendly interface for the CrewAI multi-agent stock analysis system
"""

import streamlit as st
import os
import json
import sys
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_REASONING_MODEL = os.getenv("OPENAI_REASONING_MODEL", "gpt-4o-mini")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

import time
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="VN Stock Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .buy-signal {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    .sell-signal {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    .hold-signal {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    .stProgress .st-bo {
        background-color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = "HPG"

def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def check_api_keys():
    """Check if required API keys are configured"""
    required_keys = ["OPENAI_API_KEY", "BRAVE_API_KEY", "FIRECRAWL_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        st.warning("⚠️ Missing API keys. Running in demo mode.")
        st.info(f"Missing: {', '.join(missing_keys)}")
        st.info("Set these in your .env file:")
        for key in missing_keys:
            st.code(f"{key}=your_key_here")
        
        demo_mode = True
    else:
        demo_mode = False

    return demo_mode

def run_analysis(symbol, analysis_date):
    """Run the CrewAI analysis for a given symbol"""
    demo_mode = check_api_keys()
    
    if demo_mode:
        # Demo mode - return mock results
        return generate_demo_results(symbol, analysis_date)
    
    try:
        # Change to project directory
        os.chdir("/Users/tamle/Projects/vn_stock_value_investor")
        
        # Import and run the crew
        sys.path.insert(0, 'src')
        from vn_stock_advisor.crew import VnStockAdvisor
        
        inputs = {
            "symbol": symbol,
            "current_date": str(analysis_date)
        }
        
        # Run the crew
        crew = VnStockAdvisor().crew()
        result = crew.kickoff(inputs=inputs)
        
        return result
    except Exception as e:
        st.error(f"Error running analysis: {str(e)}")
        return None

def load_analysis_results(symbol):
    """Load the analysis results from generated files"""
    results = {}
    
    # Check for generated files
    output_files = {
        'market_analysis': 'market_analysis.md',
        'fundamental_analysis': 'fundamental_analysis.md',
        'technical_analysis': 'technical_analysis.md',
        'investment_decision': 'final_decision.json'
    }
    
    for key, filename in output_files.items():
        file_path = Path(filename)
        if file_path.exists():
            if filename.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    results[key] = json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    results[key] = f.read()
        else:
            results[key] = None
    
    return results

def display_investment_decision(decision_data):
    """Display the investment decision in a formatted way"""
    if not decision_data:
        st.warning("No investment decision data available")
        return
    
    # Create columns for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stock Ticker", decision_data.get('stock_ticker', 'N/A'))
    with col2:
        st.metric("Company Name", decision_data.get('full_name', 'N/A'))
    with col3:
        st.metric("Industry", decision_data.get('industry', 'N/A'))
    with col4:
        st.metric("Analysis Date", decision_data.get('today_date', 'N/A'))
    
    # Display decision with color coding
    decision = decision_data.get('decision', 'HOLD').upper()
    
    if decision == 'BUY':
        st.markdown('<div class="buy-signal">🟢 BUY SIGNAL</div>', unsafe_allow_html=True)
    elif decision == 'SELL':
        st.markdown('<div class="sell-signal">🔴 SELL SIGNAL</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hold-signal">🟡 HOLD SIGNAL</div>', unsafe_allow_html=True)
    
    # Display reasoning sections
    st.subheader("📊 Investment Analysis")
    
    tabs = st.tabs(["📈 Macro Analysis", "📊 Fundamental Analysis", "📉 Technical Analysis"])
    
    with tabs[0]:
        st.markdown(decision_data.get('macro_reasoning', 'No macro analysis available'))
    
    with tabs[1]:
        st.markdown(decision_data.get('fund_reasoning', 'No fundamental analysis available'))
    
    with tabs[2]:
        st.markdown(decision_data.get('tech_reasoning', 'No technical analysis available'))

def generate_demo_results(symbol, analysis_date):
    """Generate demo results for testing without API keys"""
    demo_company = {
        "HPG": {"name": "Hoa Phat Group", "industry": "Steel Manufacturing"},
        "VNM": {"name": "Vinamilk", "industry": "Dairy Products"},
        "VCB": {"name": "Vietcombank", "industry": "Banking"},
        "VIC": {"name": "Vingroup", "industry": "Real Estate"},
        "GAS": {"name": "PetroVietnam Gas", "industry": "Energy"},
    }
    
    company_info = demo_company.get(symbol, {"name": f"{symbol} Corporation", "industry": "General"})
    
    # Create demo files
    market_analysis = f"""
    # Market Analysis for {symbol}
    
    ## Recent News
    - **{symbol}** announced strong Q4 2024 earnings with 15% growth
    - Market sentiment is positive with institutional investors increasing positions
    - Industry outlook remains favorable for {company_info['industry']}
    
    ## Key Developments
    - New product launches driving revenue growth
    - Strategic partnerships expanding market reach
    - Cost optimization initiatives showing results
    
    ## Market Sentiment
    - **Bullish**: 65% of analysts maintain BUY ratings
    - **Neutral**: 25% recommend HOLD
    - **Bearish**: 10% suggest SELL
    """
    
    fundamental_analysis = f"""
    # Fundamental Analysis for {symbol}
    
    ## Financial Ratios
    - **P/E Ratio**: 12.5 (Industry avg: 15.2)
    - **P/B Ratio**: 1.8 (Industry avg: 2.1)
    - **ROE**: 18.5% (Above industry average)
    - **ROA**: 8.2% (Strong profitability)
    - **Debt/Equity**: 0.45 (Conservative debt levels)
    
    ## Revenue Trends
    - **2022**: 15,000B VND
    - **2023**: 18,500B VND (+23% YoY)
    - **2024E**: 22,000B VND (+19% YoY)
    
    ## Competitive Position
    - Market leader in {company_info['industry']}
    - Strong brand recognition
    - Diversified revenue streams
    """
    
    technical_analysis = f"""
    # Technical Analysis for {symbol}
    
    ## Price Action
    - **Current Price**: 45,000 VND
    - **52-week High**: 52,000 VND
    - **52-week Low**: 38,000 VND
    - **Support Level**: 42,000 VND
    - **Resistance Level**: 48,000 VND
    
    ## Technical Indicators
    - **RSI**: 58 (Neutral momentum)
    - **MACD**: Bullish crossover detected
    - **SMA 20**: Above current price (bullish)
    - **SMA 50**: Strong support level
    - **Volume**: Above average indicating institutional interest
    
    ## Chart Patterns
    - Ascending triangle formation
    - Higher lows pattern indicating accumulation
    - Breakout potential above 48,000 VND
    """
    
    investment_decision = {
        "stock_ticker": symbol,
        "full_name": company_info["name"],
        "industry": company_info["industry"],
        "today_date": str(analysis_date),
        "decision": "BUY",
        "macro_reasoning": f"The Vietnamese economy shows strong growth momentum with {company_info['industry']} sector outperforming. Government policies support industry development and foreign investment flows remain positive.",
        "fund_reasoning": f"{company_info['name']} demonstrates strong fundamentals with above-average ROE and conservative debt levels. Revenue growth of 20%+ indicates robust business model and market position.",
        "tech_reasoning": f"Technical indicators show bullish momentum with MACD crossover and price above key moving averages. Support at 42,000 VND provides downside protection with upside target at 52,000 VND."
    }
    
    # Write demo files
    with open('market_analysis.md', 'w', encoding='utf-8') as f:
        f.write(market_analysis)
    
    with open('fundamental_analysis.md', 'w', encoding='utf-8') as f:
        f.write(fundamental_analysis)
    
    with open('technical_analysis.md', 'w', encoding='utf-8') as f:
        f.write(technical_analysis)
    
    with open('final_decision.json', 'w', encoding='utf-8') as f:
        json.dump(investment_decision, f, indent=2, ensure_ascii=False)
    
    return "Demo analysis completed successfully"

def display_markdown_report(markdown_content, title):
    """Display markdown content in a formatted way"""
    if markdown_content:
        st.subheader(title)
        st.markdown(markdown_content)
    else:
        st.info(f"{title} not yet generated")

def main():
    """Main Streamlit app"""
    
    # Load environment variables
    load_env_file()
    
    # Header
    st.markdown('<h1 class="main-header">🇻🇳 VN Stock Advisor</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>AI-Powered Stock Analysis System</p>", unsafe_allow_html=True)
    
    # Demo mode indicator
    if st.session_state.get('demo_mode', False):
        st.info("🎮 **DEMO MODE** - Using sample data for demonstration")
    
    # Check API keys
    missing_keys = check_api_keys()
    if missing_keys:
        # Check if we have any API keys at all
        essential_keys = [
            'OPENAI_API_KEY', 'BRAVE_API_KEY', 'FIRECRAWL_API_KEY'
        ]
        
        has_any_key = any(os.environ.get(key) for key in essential_keys)
        
        if not has_any_key:
            st.error("⚠️ No API Keys Found - Please check your .env file")
            st.info("Make sure your .env file is in the project root directory")
            if st.button("🔄 Reload Environment"):
                load_dotenv(override=True)
                st.rerun()
        else:
            st.warning("⚠️ Some API Keys Missing - Running with limited functionality")
        
        if not st.session_state.get('demo_mode', False) and missing_keys:
            # Show demo mode option
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Missing keys:", missing_keys)
            with col2:
                if st.button("🎮 Use Demo Mode"):
                    st.session_state.demo_mode = True
                    st.rerun()
        
        if not st.session_state.get('demo_mode', False) and not has_any_key:
            st.stop()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Please configure the following API keys in your .env file:")
            for key in missing_keys:
                st.code(f"{key}=your_api_key_here")
        
        with col2:
            if st.button("🎮 Use Demo Mode"):
                st.session_state.demo_mode = True
                st.rerun()
        
        if not st.session_state.get('demo_mode', False):
            st.stop()
    
    # Initialize session state
    if 'current_symbol' not in st.session_state:
        st.session_state.current_symbol = "HPG"
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    # Sidebar
    st.sidebar.header("🔧 Analysis Configuration")
    
    # Stock symbol input
    symbol_input = st.sidebar.text_input(
        "Stock Symbol",
        value=st.session_state.current_symbol,
        placeholder="e.g., HPG, VNM, VCB"
    )
    
    # Validate and process symbol
    symbol = symbol_input.strip().upper() if symbol_input else ""
    
    # Analysis date
    analysis_date = st.sidebar.date_input(
        "Analysis Date",
        value=date.today(),
        help="Select the date for stock analysis"
    )
    
    # Run analysis button
    if st.sidebar.button("🚀 Run Analysis", type="primary"):
        if not symbol:
            st.sidebar.error("Please enter a stock symbol")
            st.stop()
        
        st.session_state.current_symbol = symbol
        
        # Progress bar
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        # Clear previous results
        st.session_state.analysis_complete = False
        st.session_state.analysis_results = {}
        
        try:
            # Run analysis
            status_text.text("🔄 Running multi-agent analysis...")
            progress_bar.progress(25)
            
            # Run the crew analysis
            result = run_analysis(symbol, analysis_date)
            
            progress_bar.progress(75)
            status_text.text("📊 Loading results...")
            
            # Load results
            results = load_analysis_results(symbol)
            st.session_state.analysis_results = results
            st.session_state.analysis_complete = True
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.session_state.analysis_complete = False
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
    
    # Main content area
    if st.session_state.analysis_complete:
        results = st.session_state.analysis_results
        
        # Display investment decision
        if results.get('investment_decision'):
            st.markdown("---")
            display_investment_decision(results['investment_decision'])
        
        # Display detailed reports
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_markdown_report(results.get('market_analysis'), "📰 Market News Analysis")
        
        with col2:
            display_markdown_report(results.get('fundamental_analysis'), "📈 Fundamental Analysis")
        
        # Technical analysis
        display_markdown_report(results.get('technical_analysis'), "📊 Technical Analysis")
        
        # Download results
        st.markdown("---")
        st.subheader("📥 Download Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if results.get('market_analysis'):
                st.download_button(
                    label="📰 Market Report",
                    data=results['market_analysis'],
                    file_name=f"{symbol}_market_analysis.md",
                    mime="text/markdown"
                )
        
        with col2:
            if results.get('fundamental_analysis'):
                st.download_button(
                    label="📈 Fundamental Report",
                    data=results['fundamental_analysis'],
                    file_name=f"{symbol}_fundamental_analysis.md",
                    mime="text/markdown"
                )
        
        with col3:
            if results.get('technical_analysis'):
                st.download_button(
                    label="📊 Technical Report",
                    data=results['technical_analysis'],
                    file_name=f"{symbol}_technical_analysis.md",
                    mime="text/markdown"
                )
        
        with col4:
            if results.get('investment_decision'):
                st.download_button(
                    label="💡 Decision JSON",
                    data=json.dumps(results['investment_decision'], indent=2, ensure_ascii=False),
                    file_name=f"{symbol}_investment_decision.json",
                    mime="application/json"
                )
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to VN Stock Advisor
        
        This AI-powered system uses **4 specialized agents** to provide comprehensive stock analysis:
        
        ### 🤖 AI Agents
        - **News Researcher**: Collects and analyzes latest market news
        - **Fundamental Analyst**: Analyzes financial ratios and company performance
        - **Technical Analyst**: Examines price patterns and technical indicators
        - **Investment Strategist**: Synthesizes all insights for final decision
        
        ### 📊 Analysis Features
        - Real-time news sentiment analysis
        - Fundamental metrics (P/E, P/B, ROE, EPS, etc.)
        - Technical indicators (RSI, MACD, Moving averages)
        - Investment recommendation (Buy/Sell/Hold)
        
        ### 🚀 How to Use
        1. Enter a Vietnamese stock symbol (e.g., HPG, VNM, VCB)
        2. Select analysis date
        3. Click "Run Analysis" to start the multi-agent process
        4. View comprehensive reports and investment decision
        
        **Get started by entering a stock symbol in the sidebar!**
        """)
        
        # Sample stocks
        st.info("💡 **Popular Vietnamese Stocks:** HPG, VNM, VCB, BID, CTG, GAS, VIC, MSN")

if __name__ == "__main__":
    main()
