from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool, FirecrawlScrapeWebsiteTool
from vn_stock_advisor.tools.brave_search_tool import BraveSearchTool
from vn_stock_advisor.tools.custom_tool import FundDataTool, TechDataTool, FileReadTool
from pydantic import BaseModel, Field
from typing import List, Literal
from dotenv import load_dotenv
import os, json
import warnings
warnings.filterwarnings("ignore") # Suppress unimportant warnings

# Load environment variables
load_dotenv()

# Get API keys and model names from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_REASONING_MODEL = os.getenv("OPENAI_REASONING_MODEL", "gpt-4o-mini")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

# Create an LLM with a temperature of 0 to ensure deterministic outputs
from crewai import LLM

# Initialize LLMs with OpenAI GPT-4o-mini
openai_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0,
    max_tokens=4096
)

openai_reasoning_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.1,
    max_tokens=8192
)

# Initialize the tools
file_read_tool = FileReadTool(file_path="knowledge/PE_PB_industry_average.json")
fund_tool=FundDataTool()
tech_tool=TechDataTool(result_as_answer=True)
scrape_tool = FirecrawlScrapeWebsiteTool(
    onlyMainContent=True
)
search_tool = BraveSearchTool()
web_search_tool = WebsiteSearchTool(
    config=dict(
        llm={
            "provider": "openai",
            "config": {
                "model": OPENAI_MODEL,
                "api_key": OPENAI_API_KEY
            }
        },
        embedder={
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"
            }
        }
    )
)

# Create a JSON knowledge source
json_source = JSONKnowledgeSource(
    file_paths=["PE_PB_industry_average.json"]
)

# Create Pydantic Models for Structured Output
class InvestmentDecision(BaseModel):
    stock_ticker: str = Field(..., description="Mã cổ phiếu")
    full_name: str = Field(..., description="Tên đầy đủ công ty")
    industry: str =Field(..., description="Lĩnh vực kinh doanh")
    today_date: str = Field(..., description="Ngày phân tích")
    decision: str = Field(..., description="Quyết định mua, giữ hay bán cổ phiếu")
    macro_reasoning: str = Field(..., description="Giải thích quyết định từ góc nhìn kinh tế vĩ mô và các chính sách quan trọng")
    fund_reasoning: str = Field(..., description="Giải thích quyết định từ góc độ phân tích cơ bản")
    tech_reasoning: str = Field(..., description="Giải thích quyết định từ góc độ phân tích kỹ thuật")

@CrewBase
class VnStockAdvisor():
    """VnStockAdvisor crew"""

    # Create type-hinted class attributes that expects a list of agents and a list of tasks
    agents: List[BaseAgent] # ← auto-filled with all the @agent-decorated outputs
    tasks: List[Task]       # ← auto-filled with all the @task-decorated outputs

    @agent
    def stock_news_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_news_researcher'],
            tools=[search_tool, scrape_tool],
            llm=openai_llm,
            verbose=True
        )

    @agent
    def fundamental_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["fundamental_analyst"],
            verbose=True,
            llm=openai_llm,
            tools=[fund_tool, file_read_tool],
            knowledge_sources=[json_source],
            max_rpm=10,
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": OPENAI_API_KEY,
                }
            }
        )

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_analyst"],
            verbose=True,
            llm=openai_llm,
            tools=[tech_tool],
            max_rpm=10
        )
    
    @agent
    def investment_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["investment_strategist"],
            verbose=True,
            llm=openai_reasoning_llm,
            max_rpm=10
        )

    @task
    def news_collecting(self) -> Task:
        return Task(
            config=self.tasks_config["news_collecting"],
            async_execution=True,
            output_file="market_analysis.md"
        )

    @task
    def fundamental_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["fundamental_analysis"],
            async_execution=True,
            output_file="fundamental_analysis.md"
        )

    @task
    def technical_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["technical_analysis"],
            async_execution=True,
            output_file="technical_analysis.md"
        )
    
    @task
    def investment_decision(self) -> Task:
        return Task(
            config=self.tasks_config["investment_decision"],
            context=[self.news_collecting(), self.fundamental_analysis(), self.technical_analysis()],
            output_json=InvestmentDecision,
            output_file="final_decision.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the VnStockAdvisor crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )