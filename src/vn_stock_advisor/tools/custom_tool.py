from typing import Type, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from vnstock import Vnstock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class MyToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Mã cổ phiếu.")

class FundDataTool(BaseTool):
    name: str = "Công cụ tra cứu dữ liệu cổ phiếu phục vụ phân tích cơ bản."
    description: str = "Công cụ tra cứu dữ liệu cổ phiếu phục vụ phân tích cơ bản."
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, argument: str) -> str:
        try:
            # Validate input
            if not argument or not isinstance(argument, str):
                return "Error: Invalid stock symbol provided"
            
            argument = argument.strip().upper()
            
            # Initialize the class 
            stock = Vnstock().stock(symbol=argument, source="TCBS")
            financial_ratios = stock.finance.ratio(period="quarter")
            income_df = stock.finance.income_statement(period="quarter")
            company = Vnstock().stock(symbol=argument, source='TCBS').company

            # Validate data availability
            if financial_ratios.empty or income_df.empty:
                return f"Error: No data available for symbol {argument}"

            # Get company full name & industry with safe access
            profile_data = company.profile()
            overview_data = company.overview()
            
            full_name = profile_data.get("company_name").iloc[0] if not profile_data.empty else argument
            industry = overview_data.get("industry").iloc[0] if not overview_data.empty else "Unknown"

            # Get data from the latest row of DataFrame for financial ratios
            latest_ratios = financial_ratios.iloc[0] if not financial_ratios.empty else None

            # Get last 4 quarters of income statement
            last_4_quarters = income_df.head(4)
            
            # Helper function to safely extract and format ratios
            def safe_extract_ratio(df, column_name, default="N/A"):
                """Safely extract ratio value from DataFrame with proper handling of NaN values"""
                if df is None or df.empty:
                    return default
                
                # Try multiple possible column names for each ratio
                column_mapping = {
                    'price_to_earning': ['price_to_earning', 'pe', 'P/E', 'p_e_ratio'],
                    'price_to_book': ['price_to_book', 'pb', 'P/B', 'p_b_ratio'],
                    'roe': ['roe', 'ROE', 'return_on_equity', 'return_on_equity_percent'],
                    'roa': ['roa', 'ROA', 'return_on_assets', 'return_on_assets_percent'],
                    'earning_per_share': ['earning_per_share', 'eps', 'EPS', 'earnings_per_share'],
                    'debt_on_equity': ['debt_on_equity', 'de', 'D/E', 'debt_equity_ratio'],
                    'gross_profit_margin': ['gross_profit_margin', 'gross_margin', 'profit_margin'],
                    'value_before_ebitda': ['value_before_ebitda', 'ev_ebitda', 'ev_ebitda_ratio']
                }
                
                possible_names = column_mapping.get(column_name, [column_name])
                
                for name in possible_names:
                    if name in df.index if isinstance(df, pd.Series) else name in df.columns:
                        value = df[name] if isinstance(df, pd.Series) else df[name].iloc[0]
                        if pd.notna(value) and str(value).strip():
                            # Format as percentage for ratios that should be percentages
                            if column_name in ['roe', 'roa', 'gross_profit_margin']:
                                return f"{float(value):.2f}%"
                            else:
                                return f"{float(value):.2f}" if isinstance(value, (int, float)) else str(value)
                
                return default

            # Extract financial ratios data with proper handling
            pe_ratio = safe_extract_ratio(latest_ratios, "price_to_earning")
            pb_ratio = safe_extract_ratio(latest_ratios, "price_to_book")
            roe = safe_extract_ratio(latest_ratios, "roe")
            roa = safe_extract_ratio(latest_ratios, "roa")
            eps = safe_extract_ratio(latest_ratios, "earning_per_share")
            de = safe_extract_ratio(latest_ratios, "debt_on_equity")
            profit_margin = safe_extract_ratio(latest_ratios, "gross_profit_margin")
            evebitda = safe_extract_ratio(latest_ratios, "value_before_ebitda")

            # Format quarterly income data
            quarterly_trends = []
            for i, (_, quarter) in enumerate(last_4_quarters.iterrows()):          
                # Handle formatting of values properly
                revenue = quarter.get("revenue", "N/A")
                revenue_formatted = f"{revenue:,.0f} VND" if isinstance(revenue, (int, float)) else revenue
                
                gross_profit = quarter.get("gross_profit", "N/A")
                gross_profit_formatted = f"{gross_profit:,.0f} VND" if isinstance(gross_profit, (int, float)) else gross_profit
                
                post_tax_profit = quarter.get("post_tax_profit", "N/A")
                post_tax_profit_formatted = f"{post_tax_profit:,.0f} VND" if isinstance(post_tax_profit, (int, float)) else post_tax_profit
                
                quarter_info = f"""
                Quý T - {i + 1}:
                - Doanh thu thuần: {revenue_formatted}
                - Lợi nhuận gộp: {gross_profit_formatted}
                - Lợi nhuận sau thuế: {post_tax_profit_formatted}
                """
                quarterly_trends.append(quarter_info)
            
            return f"""Mã cổ phiếu: {argument}
            Tên công ty: {full_name}
            Ngành: {industry}
            Ngày phân tích: {datetime.now().strftime('%Y-%m-%d')}
            
            Tỷ lệ P/E: {pe_ratio}
            Tỷ lệ P/B: {pb_ratio}
            Tỷ lệ ROE: {roe}
            Tỷ lệ ROA: {roa}
            Biên lợi nhuận: {profit_margin}
            Lợi nhuận trên mỗi cổ phiếu EPS (VND): {eps}
            Hệ số nợ trên vốn chủ sở hữu D/E: {de}
            Tỷ lệ EV/EBITDA: {evebitda}

            XU HƯỚNG 4 QUÝ GẦN NHẤT:
            {"".join(quarterly_trends)}
            """
        except Exception as e:
            return f"Lỗi khi lấy dữ liệu: {e}"
        
class TechDataTool(BaseTool):
    name: str = "Công cụ tra cứu dữ liệu cổ phiếu phục vụ phân tích kĩ thuật."
    description: str = "Công cụ tra cứu dữ liệu cổ phiếu phục vụ phân tích kĩ thuật, cung cấp các chỉ số như SMA, EMA, RSI, MACD, Bollinger Bands, và vùng hỗ trợ/kháng cự."
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, argument: str) -> str:
        try:
            # Validate input
            if not argument or not isinstance(argument, str):
                return "Error: Invalid stock symbol provided"
            
            argument = argument.strip().upper()
            
            # Initialize vnstock and get historical price data
            stock = Vnstock().stock(symbol=argument, source="TCBS")
            company = Vnstock().stock(symbol=argument, source='TCBS').company

            # Get company full name & industry with safe access
            profile_data = company.profile()
            overview_data = company.overview()
            
            full_name = profile_data.get("company_name").iloc[0] if not profile_data.empty else argument
            industry = overview_data.get("industry").iloc[0] if not overview_data.empty else "Unknown"
            
            # Get price data for the last 200 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=200)
            price_data = stock.quote.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1D"  # Daily data
            )
            
            if price_data.empty or len(price_data) < 5:
                return f"Không tìm thấy dữ liệu lịch sử cho cổ phiếu {argument}"
            
            # Validate required columns exist
            required_columns = ['close', 'volume']
            if not all(col in price_data.columns for col in required_columns):
                return f"Error: Missing required data columns for {argument}"
            
            # Calculate technical indicators
            tech_data = self._calculate_indicators(price_data)
            
            # Identify support and resistance levels
            support_resistance = self._find_support_resistance(price_data)
            
            # Get recent price and volume data with safe access
            current_price = price_data['close'].iloc[-1] if len(price_data) > 0 else 0
            recent_prices = price_data['close'].iloc[-5:-1] if len(price_data) >= 5 else price_data['close']
            current_volume = price_data['volume'].iloc[-1] if len(price_data) > 0 else 0
            recent_volumes = price_data['volume'].iloc[-5:-1] if len(price_data) >= 5 else price_data['volume']
            
            # Format result with safe access
            latest_indicators = tech_data.iloc[-1] if not tech_data.empty else {}
            
            result = f"""Mã cổ phiếu: {argument}
            Tên công ty: {full_name}
            Ngành: {industry}
            Ngày phân tích: {datetime.now().strftime('%Y-%m-%d')}
            Giá hiện tại: {current_price:,.2f} VND
            Khối lượng giao dịch: {current_volume:,.0f} cp

            GIÁ ĐÓNG CỬA GẦN NHẤT:
            - T-1: {recent_prices.iloc[-1]:,.2f} VND (Khối lượng: {recent_volumes.iloc[-1]:,.0f} cp)
            - T-2: {recent_prices.iloc[-2]:,.2f} VND (Khối lượng: {recent_volumes.iloc[-2]:,.0f} cp)
            - T-3: {recent_prices.iloc[-3]:,.2f} VND (Khối lượng: {recent_volumes.iloc[-3]:,.0f} cp)
            - T-4: {recent_prices.iloc[-4]:,.2f} VND (Khối lượng: {recent_volumes.iloc[-4]:,.0f} cp)
            
            CHỈ SỐ KỸ THUẬT:
            - SMA (20): {latest_indicators['SMA_20']:,.2f}
            - SMA (50): {latest_indicators['SMA_50']:,.2f}
            - SMA (200): {latest_indicators['SMA_200']:,.2f}
            - EMA (12): {latest_indicators['EMA_12']:,.2f}
            - EMA (26): {latest_indicators['EMA_26']:,.2f}
            
            - RSI (14): {latest_indicators['RSI_14']:.2f}
            - MACD: {latest_indicators['MACD']:.2f}
            - MACD Signal: {latest_indicators['MACD_Signal']:.2f}
            - MACD Histogram: {latest_indicators['MACD_Hist']:.2f}
            
            - Bollinger Upper: {latest_indicators['BB_Upper']:,.2f}
            - Bollinger Middle: {latest_indicators['BB_Middle']:,.2f}
            - Bollinger Lower: {latest_indicators['BB_Lower']:,.2f}

            CHỈ SỐ KHỐI LƯỢNG:
            - Khối lượng hiện tại: {current_volume:,.0f} cp
            - Trung bình 10 phiên: {latest_indicators['Volume_SMA_10']:,.0f} cp
            - Trung bình 20 phiên: {latest_indicators['Volume_SMA_20']:,.0f} cp
            - Trung bình 50 phiên: {latest_indicators['Volume_SMA_50']:,.0f} cp
            - Tỷ lệ Khối lượng / Trung bình 20: {latest_indicators['Volume_Ratio_20']:.2f}
            - On-Balance Volume (OBV): {latest_indicators['OBV']:,.0f}
            
            VÙNG HỖ TRỢ VÀ KHÁNG CỰ:
            {support_resistance}
            
            NHẬN ĐỊNH KỸ THUẬT:
            {self._get_technical_analysis(latest_indicators, current_price, support_resistance)}
            """
            return result
            
        except Exception as e:
            return f"Lỗi khi lấy dữ liệu kỹ thuật: {e}"
    
    def _calculate_indicators(self, df):
        """Calculate various technical indicators."""
        # Make a copy to avoid modifying original data
        data = df.copy()
        
        # Simple Moving Averages
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        data['SMA_50'] = data['close'].rolling(window=50).mean()
        data['SMA_200'] = data['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        data['RSI_14'] = 100 - (100 / (1 + rs))
        data['RSI_14'] = data['RSI_14'].fillna(50)  # Fill NaN values with neutral RSI
        
        # Bollinger Bands
        data['BB_Middle'] = data['close'].rolling(window=20).mean()
        std_dev = data['close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (std_dev * 2)
        data['BB_Lower'] = data['BB_Middle'] - (std_dev * 2)

        # Calculate volume moving averages
        data['Volume_SMA_10'] = data['volume'].rolling(window=10).mean()
        data['Volume_SMA_20'] = data['volume'].rolling(window=20).mean()
        data['Volume_SMA_50'] = data['volume'].rolling(window=50).mean()
        
        # Calculate volume ratio compared to average
        data['Volume_Ratio_10'] = data['volume'] / data['Volume_SMA_10']
        data['Volume_Ratio_20'] = data['volume'] / data['Volume_SMA_20']
        
        # On-Balance Volume (OBV)
        data['OBV'] = 0
        data.loc[0, 'OBV'] = data.loc[0, 'volume']
        for i in range(1, len(data)):
            if data.loc[i, 'close'] > data.loc[i-1, 'close']:
                data.loc[i, 'OBV'] = data.loc[i-1, 'OBV'] + data.loc[i, 'volume']
            elif data.loc[i, 'close'] < data.loc[i-1, 'close']:
                data.loc[i, 'OBV'] = data.loc[i-1, 'OBV'] - data.loc[i, 'volume']
            else:
                data.loc[i, 'OBV'] = data.loc[i-1, 'OBV']
        
        return data
    
    def _find_support_resistance(self, df, window=10, threshold=0.03):
        """Find support and resistance levels."""
        data = df.copy()
        
        # Find potential pivot points
        data['local_max'] = data['high'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[len(x)//2] == max(x), raw=False
        )
        data['local_min'] = data['low'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[len(x)//2] == min(x), raw=False
        )
        
        # Get pivot high/low points
        resistance_levels = data[data['local_max'] == 1]['high'].values
        support_levels = data[data['local_min'] == 1]['low'].values
        
        # Group close resistance/support levels
        current_price = data['close'].iloc[-1]
        
        # Function to cluster price levels
        def cluster_levels(levels, threshold_pct):
            if len(levels) == 0:
                return []
                
            levels = sorted(levels)
            clusters = [[levels[0]]]
            
            for level in levels[1:]:
                last_cluster = clusters[-1]
                last_value = last_cluster[-1]
                
                # If this level is within threshold% of the last value, add to the same cluster
                if abs((level - last_value) / last_value) < threshold_pct:
                    last_cluster.append(level)
                else:
                    clusters.append([level])
            
            # Calculate average for each cluster
            return [np.mean(cluster) for cluster in clusters]
        
        # Cluster and filter resistance levels
        resistance_levels = cluster_levels(resistance_levels, threshold)
        resistance_levels = [r for r in resistance_levels if r > current_price]
        resistance_levels = sorted(resistance_levels)[:3]  # Get nearest 3 levels
        
        # Cluster and filter support levels
        support_levels = cluster_levels(support_levels, threshold)
        support_levels = [s for s in support_levels if s < current_price]
        support_levels = sorted(support_levels, reverse=True)[:3]  # Get nearest 3 levels
        
        # Format result
        result = "Vùng kháng cự:\n"
        for i, level in enumerate(resistance_levels, 1):
            result += f"- R{i}: {level:,.2f} VND\n"
        
        result += "\nVùng hỗ trợ:\n"
        for i, level in enumerate(support_levels, 1):
            result += f"- S{i}: {level:,.2f} VND\n"
            
        return result
    
    def _get_technical_analysis(self, indicators, current_price, support_resistance):
        """Generate technical analysis text based on indicators."""
        analysis = []
        
        # Trend analysis based on SMAs
        if current_price > indicators['SMA_200'] and indicators['SMA_50'] > indicators['SMA_200']:
            analysis.append("- Xu hướng dài hạn: TĂNG (Giá trên SMA 200, SMA 50 trên SMA 200)")
        elif current_price < indicators['SMA_200'] and indicators['SMA_50'] < indicators['SMA_200']:
            analysis.append("- Xu hướng dài hạn: GIẢM (Giá dưới SMA 200, SMA 50 dưới SMA 200)")
        else:
            analysis.append("- Xu hướng dài hạn: TRUNG LẬP (Tín hiệu trái chiều giữa các SMA)")
        
        # Short-term trend
        if current_price > indicators['SMA_20'] and indicators['SMA_20'] > indicators['SMA_50']:
            analysis.append("- Xu hướng ngắn hạn: TĂNG (Giá trên SMA 20, SMA 20 trên SMA 50)")
        elif current_price < indicators['SMA_20'] and indicators['SMA_20'] < indicators['SMA_50']:
            analysis.append("- Xu hướng ngắn hạn: GIẢM (Giá dưới SMA 20, SMA 20 dưới SMA 50)")
        else:
            analysis.append("- Xu hướng ngắn hạn: TRUNG LẬP (Tín hiệu trái chiều giữa SMA ngắn hạn)")
        
        # RSI analysis
        if indicators['RSI_14'] > 70:
            analysis.append("- RSI: QUÁ MUA (RSI > 70), có khả năng điều chỉnh giảm")
        elif indicators['RSI_14'] < 30:
            analysis.append("- RSI: QUÁ BÁN (RSI < 30), có khả năng hồi phục")
        else:
            analysis.append(f"- RSI: TRUNG TÍNH ({indicators['RSI_14']:.2f})")
        
        # MACD analysis
        if indicators['MACD'] > indicators['MACD_Signal']:
            analysis.append("- MACD: TÍCH CỰC (MACD trên Signal Line)")
        else:
            analysis.append("- MACD: TIÊU CỰC (MACD dưới Signal Line)")
        
        # Bollinger Bands analysis
        if current_price > indicators['BB_Upper']:
            analysis.append("- Bollinger Bands: QUÁ MUA (Giá trên dải trên BB)")
        elif current_price < indicators['BB_Lower']:
            analysis.append("- Bollinger Bands: QUÁ BÁN (Giá dưới dải dưới BB)")
        else:
            position = (current_price - indicators['BB_Lower']) / (indicators['BB_Upper'] - indicators['BB_Lower'])
            if position > 0.8:
                analysis.append("- Bollinger Bands: GẦN VÙNG QUÁ MUA (Giá gần dải trên BB)")
            elif position < 0.2:
                analysis.append("- Bollinger Bands: GẦN VÙNG QUÁ BÁN (Giá gần dải dưới BB)")
            else:
                analysis.append("- Bollinger Bands: TRUNG TÍNH (Giá trong khoảng giữa dải BB)")
        
        # Volume ratio analysis
        volume_ratio_20 = indicators['Volume_Ratio_20']
        if volume_ratio_20 > 2.0:
            analysis.append("- Khối lượng: RẤT CAO (>200% trung bình 20 phiên)")
        elif volume_ratio_20 > 1.5:
            analysis.append("- Khối lượng: CAO (150-200% trung bình 20 phiên)")
        elif volume_ratio_20 < 0.5:
            analysis.append("- Khối lượng: THẤP (<50% trung bình 20 phiên)")
        else:
            analysis.append("- Khối lượng: BÌNH THƯỜNG (50-150% trung bình 20 phiên)")

        # Volume trend analysis
        if (indicators['Volume_SMA_10'] > indicators['Volume_SMA_20'] and 
            indicators['Volume_SMA_20'] > indicators['Volume_SMA_50']):
            analysis.append("- Xu hướng khối lượng: TĂNG (SMA 10 > SMA 20 > SMA 50)")
        elif (indicators['Volume_SMA_10'] < indicators['Volume_SMA_20'] and 
            indicators['Volume_SMA_20'] < indicators['Volume_SMA_50']):
            analysis.append("- Xu hướng khối lượng: GIẢM (SMA 10 < SMA 20 < SMA 50)")
        else:
            analysis.append("- Xu hướng khối lượng: TRUNG LẬP")

        # OBV trend analysis
        current_volume = indicators['volume']
        if current_volume > indicators['Volume_SMA_20'] * 1.5:
            if current_price > indicators['SMA_20']:
                analysis.append("- Tín hiệu khối lượng: TÍCH CỰC (Khối lượng cao kèm giá tăng)")
            else:
                analysis.append("- Tín hiệu khối lượng: TIÊU CỰC (Khối lượng cao kèm giá giảm)")

        return "\n".join(analysis)
    
# Re-write basic FileReadTool but with utf-8 encoding
class FileReadToolSchema(BaseModel):
    """Input for FileReadTool."""

    file_path: str = Field(..., description="Mandatory file full path to read the file")
    start_line: Optional[int] = Field(1, description="Line number to start reading from (1-indexed)")
    line_count: Optional[int] = Field(None, description="Number of lines to read. If None, reads the entire file")


class FileReadTool(BaseTool):
    """A tool for reading file contents.

    This tool inherits its schema handling from BaseTool to avoid recursive schema
    definition issues. The args_schema is set to FileReadToolSchema which defines
    the required file_path parameter. The schema should not be overridden in the
    constructor as it would break the inheritance chain and cause infinite loops.

    The tool supports two ways of specifying the file path:
    1. At construction time via the file_path parameter
    2. At runtime via the file_path parameter in the tool's input

    Args:
        file_path (Optional[str]): Path to the file to be read. If provided,
            this becomes the default file path for the tool.
        **kwargs: Additional keyword arguments passed to BaseTool.

    Example:
        >>> tool = FileReadTool(file_path="/path/to/file.txt")
        >>> content = tool.run()  # Reads /path/to/file.txt
        >>> content = tool.run(file_path="/path/to/other.txt")  # Reads other.txt
        >>> content = tool.run(file_path="/path/to/file.txt", start_line=100, line_count=50)  # Reads lines 100-149
    """

    name: str = "Read a file's content"
    description: str = "A tool that reads the content of a file. To use this tool, provide a 'file_path' parameter with the path to the file you want to read. Optionally, provide 'start_line' to start reading from a specific line and 'line_count' to limit the number of lines read."
    args_schema: Type[BaseModel] = FileReadToolSchema
    file_path: Optional[str] = None

    def __init__(self, file_path: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the FileReadTool.

        Args:
            file_path (Optional[str]): Path to the file to be read. If provided,
                this becomes the default file path for the tool.
            **kwargs: Additional keyword arguments passed to BaseTool.
        """
        if file_path is not None:
            kwargs["description"] = (
                f"A tool that reads file content. The default file is {file_path}, but you can provide a different 'file_path' parameter to read another file. You can also specify 'start_line' and 'line_count' to read specific parts of the file."
            )

        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(
        self,
        **kwargs: Any,
    ) -> str:
        file_path = kwargs.get("file_path", self.file_path)
        
        # Helper function to clean and parse parameter values
        def clean_and_parse_param(value, param_name, default_value):
            """Clean and parse parameter values, handling malformed inputs"""
            if value is None:
                return default_value
            
            if isinstance(value, str):
                # Clean the string by removing common malformed characters
                cleaned = value.strip()
                # Remove trailing characters like '}', '```', newlines, etc.
                cleaned = cleaned.rstrip('}`\n\r\t ')
                
                # Handle None-like strings
                if cleaned.lower() in ['none', 'null', '']:
                    return None if param_name == 'line_count' else default_value
                
                # Try to parse as integer
                try:
                    parsed_int = int(cleaned)
                    return parsed_int if parsed_int > 0 else default_value
                except ValueError:
                    # If parsing fails, return default
                    return None if param_name == 'line_count' else default_value
            
            # Handle non-string values
            if isinstance(value, (int, float)):
                return int(value) if value > 0 else default_value
            
            return default_value
        
        # Handle start_line parameter with enhanced cleaning
        start_line_raw = kwargs.get("start_line", 1)
        start_line = clean_and_parse_param(start_line_raw, 'start_line', 1)
        
        # Handle line_count parameter with enhanced cleaning
        line_count_raw = kwargs.get("line_count", None)
        line_count = clean_and_parse_param(line_count_raw, 'line_count', None)

        if file_path is None:
            return (
                "Error: No file path provided. Please provide a file path either in the constructor or as an argument."
            )

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                if start_line == 1 and line_count is None:
                    return file.read()

                start_idx = max(start_line - 1, 0)

                selected_lines = [
                    line
                    for i, line in enumerate(file)
                    if i >= start_idx and (line_count is None or i < start_idx + line_count)
                ]

                if not selected_lines and start_idx > 0:
                    return f"Error: Start line {start_line} exceeds the number of lines in the file."

                return "".join(selected_lines)
        except FileNotFoundError:
            return f"Error: File not found at path: {file_path}"
        except PermissionError:
            return f"Error: Permission denied when trying to read file: {file_path}"
        except Exception as e:
            return f"Error: Failed to read file {file_path}. {str(e)}"