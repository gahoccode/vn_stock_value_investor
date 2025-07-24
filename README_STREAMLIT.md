# VN Stock Advisor - Streamlit GUI

## Overview
This is a user-friendly web interface for the VN Stock Advisor multi-agent AI system. The Streamlit GUI provides an intuitive way to run stock analysis and view comprehensive reports without using the command line.

## Features

### 🎯 Core Features
- **Interactive Stock Analysis**: Enter any Vietnamese stock symbol and get comprehensive analysis
- **Real-time Progress Tracking**: See analysis progress with progress bars and status updates
- **Multi-format Reports**: View and download analysis reports in markdown and JSON formats
- **Visual Decision Display**: Color-coded buy/sell/hold recommendations
- **Historical Analysis**: Choose any analysis date for backtesting

### 📊 Analysis Components
- **Market News Analysis**: Latest news and sentiment analysis
- **Fundamental Analysis**: P/E, P/B, ROE, EPS, financial ratios
- **Technical Analysis**: RSI, MACD, Moving averages, support/resistance levels
- **Investment Decision**: Synthesized recommendation with reasoning

### 💾 Export Options
- Download individual reports (Market, Fundamental, Technical)
- Download complete investment decision as JSON
- Export analysis for record-keeping

## Installation

### Prerequisites
- Python 3.10-3.12
- All API keys configured in `.env` file (see main README.md)

### Quick Setup

1. **Install Streamlit and dependencies**:
```bash
pip install -r requirements-streamlit.txt
```

2. **Verify API Keys**: Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-1.5-flash
   GEMINI_REASONING_MODEL=gemini-1.5-pro
   BRAVE_API_KEY=your_brave_search_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   ```

3. **Run the Streamlit app**:
```bash
streamlit run streamlit_app.py
```

## Usage

### Basic Usage
1. Open the web interface at `http://localhost:8501`
2. Enter a Vietnamese stock symbol (e.g., HPG, VNM, VCB)
3. Select the analysis date
4. Click "Run Analysis"
5. View comprehensive reports and investment decision

### Popular Vietnamese Stocks
- **Banking**: VCB, BID, CTG, TCB
- **Real Estate**: VIC, VHM, NVL, PDR
- **Steel**: HPG, HSG, NKG
- **Consumer**: VNM, MSN, SAB
- **Energy**: GAS, PLX, POW

### Sample Analysis
Try these symbols for testing:
- **HPG** - Hoa Phat Group (Steel)
- **VNM** - Vietnam Dairy Products
- **VCB** - Vietcombank

## Interface Guide

### Sidebar Controls
- **Stock Symbol**: Enter Vietnamese stock ticker
- **Analysis Date**: Choose date for analysis
- **Run Analysis**: Start the multi-agent process

### Main Dashboard
- **Investment Decision**: Color-coded recommendation
- **Key Metrics**: Stock ticker, company name, industry
- **Analysis Tabs**: Separate tabs for macro, fundamental, and technical analysis
- **Download Section**: Export reports in various formats

### Progress Indicators
- Progress bar shows analysis stages
- Status messages indicate current agent activity
- Error handling with helpful messages

## File Structure

```
vn_stock_value_investor/
├── streamlit_app.py          # Main Streamlit application
├── requirements-streamlit.txt # Streamlit-specific dependencies
├── README_STREAMLIT.md       # This file
├── src/
│   └── vn_stock_advisor/    # Original CrewAI code
├── .env                      # API keys configuration
└── [generated files]
    ├── market_analysis.md   # News analysis report
    ├── fundamental_analysis.md # Financial analysis
    ├── technical_analysis.md   # Technical analysis
    └── final_decision.json     # Investment decision
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**:
```bash
pip install -e .  # Install project in development mode
```

2. **API Key Issues**:
- Verify all API keys are correctly set in `.env`
- Check for typos in environment variable names
- Ensure API keys have proper permissions

3. **Streamlit Not Found**:
```bash
pip install streamlit
```

4. **Permission Errors**:
- Ensure write permissions in project directory
- Check if output files can be created

### Performance Tips
- **First run**: May take 2-5 minutes due to API calls
- **Subsequent runs**: Usually faster due to cached data
- **Rate limits**: Respect API rate limits to avoid errors

## Development

### Adding New Features
1. Modify `streamlit_app.py` for UI changes
2. Add new visualization components in the dashboard
3. Extend the analysis display sections

### Custom Styling
The app includes custom CSS for Vietnamese-friendly styling. Modify the CSS section in `streamlit_app.py` to customize appearance.

### Testing
Test with various Vietnamese stock symbols to ensure compatibility and accuracy.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all API keys are working
3. Ensure Vietnamese stock symbols are valid
4. Check internet connectivity for API calls

## License
MIT License - See main README.md for details
