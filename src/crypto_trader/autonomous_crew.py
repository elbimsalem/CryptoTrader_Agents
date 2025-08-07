"""
Autonomous Cryptocurrency Trading Crew
Enhanced multi-agent system for autonomous crypto trading
"""
import logging
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task

# Import tools
from .tools.binance_direct_tool import BinanceDirectTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Import IONOS LLM configurations
from langchain_openai import ChatOpenAI
import os

def get_ionos_llm():
    """Get IONOS LLM configuration directly"""
    return ChatOpenAI(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("IONOS_BASE_URL", "https://openai.inference.de-txl.ionos.com/v1"),
        temperature=0.1,
        max_tokens=4000
    )

# Configure logging
logger = logging.getLogger("crypto_trader.autonomous_crew")

class AutonomousToolManager:
    """
    Enhanced tool manager for autonomous trading operations
    """
    _instance = None
    _tools: Dict[str, Any] = {}
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of AutonomousToolManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_binance_direct_tool(self) -> BinanceDirectTool:
        """Get or create the Binance Direct API tool instance"""
        if 'binance_direct' not in self._tools:
            try:
                self._tools['binance_direct'] = BinanceDirectTool()
                logger.debug("BinanceDirectTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize BinanceDirectTool: {e}")
                raise
        return self._tools['binance_direct']
    
    def get_serper_tool(self) -> SerperDevTool:
        """Get or create the SerperDev search tool instance"""
        if 'serper' not in self._tools:
            try:
                self._tools['serper'] = SerperDevTool()
                logger.debug("SerperDevTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SerperDevTool: {e}")
                raise
        return self._tools['serper']
    
    def get_scrape_tool(self) -> ScrapeWebsiteTool:
        """Get or create the website scraping tool instance"""
        if 'scrape' not in self._tools:
            try:
                self._tools['scrape'] = ScrapeWebsiteTool()
                logger.debug("ScrapeWebsiteTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ScrapeWebsiteTool: {e}")
                raise
        return self._tools['scrape']

@CrewBase
class AutonomousCryptoTradingCrew:
    """
    Advanced autonomous cryptocurrency trading crew with multi-asset capabilities,
    risk management, and automated execution.
    """
    agents_config = 'config/enhanced_agents.yaml'
    tasks_config = 'config/autonomous_tasks.yaml'
    
    def __init__(self, verbose: bool = True, paper_trading: bool = True):
        """
        Initialize the Autonomous Crypto Trading Crew.
        
        Args:
            verbose: Whether to enable verbose output from agents and tasks
            paper_trading: If True, simulate trades without actual execution
        """
        self.verbose = verbose
        self.paper_trading = paper_trading
        self.tool_manager = AutonomousToolManager.get_instance()
        logger.info(f"AutonomousCryptoTradingCrew initialized - Paper Trading: {paper_trading}")

    # Market Discovery and Analysis Agents
    @agent
    def market_scanner(self) -> Agent:
        """Agent that scans the market for trading opportunities"""
        return Agent(
            config=self.agents_config['market_scanner'],
            tools=[self.tool_manager.get_binance_direct_tool()],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def asset_selector(self) -> Agent:
        """Agent that selects optimal assets for trading"""
        return Agent(
            config=self.agents_config['asset_selector'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def market_data_analyst(self) -> Agent:
        """Enhanced market data analyst with direct API access"""
        return Agent(
            config=self.agents_config['market_data_analyst'],
            tools=[self.tool_manager.get_binance_direct_tool()],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def news_and_sentiment_researcher(self) -> Agent:
        """Enhanced news and sentiment researcher"""
        return Agent(
            config=self.agents_config['news_and_sentiment_researcher'],
            tools=[
                self.tool_manager.get_serper_tool(),
                self.tool_manager.get_scrape_tool()
            ],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def crypto_analyst(self) -> Agent:
        """Enhanced crypto analyst for comprehensive analysis"""
        return Agent(
            config=self.agents_config['crypto_analyst'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    # Portfolio and Risk Management Agents
    @agent
    def risk_manager(self) -> Agent:
        """Risk management specialist"""
        return Agent(
            config=self.agents_config['risk_manager'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def portfolio_manager(self) -> Agent:
        """Multi-asset portfolio manager"""
        return Agent(
            config=self.agents_config['portfolio_manager'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    # Execution and Monitoring Agents
    @agent
    def trade_executor(self) -> Agent:
        """Trade execution specialist"""
        return Agent(
            config=self.agents_config['trade_executor'],
            tools=[self.tool_manager.get_binance_direct_tool()],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def performance_monitor(self) -> Agent:
        """Performance monitoring and optimization"""
        return Agent(
            config=self.agents_config['performance_monitor'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )
    
    @agent
    def strategy_coordinator(self) -> Agent:
        """Master strategy coordinator"""
        return Agent(
            config=self.agents_config['strategy_coordinator'],
            llm=get_ionos_llm(),
            verbose=self.verbose
        )

    # Task Definitions
    @task
    def scan_market_opportunities_task(self) -> Task:
        """Scan market for trading opportunities"""
        return Task(
            config=self.tasks_config['scan_market_opportunities'],
            agent=self.market_scanner()
        )
    
    @task
    def select_trading_assets_task(self) -> Task:
        """Select optimal assets for trading"""
        return Task(
            config=self.tasks_config['select_trading_assets'],
            agent=self.asset_selector(),
            context=[self.scan_market_opportunities_task()]
        )
    
    @task
    def fetch_comprehensive_market_data_task(self) -> Task:
        """Fetch comprehensive market data for selected assets"""
        return Task(
            config=self.tasks_config['fetch_comprehensive_market_data'],
            agent=self.market_data_analyst(),
            context=[self.select_trading_assets_task()]
        )
    
    @task
    def research_market_intelligence_task(self) -> Task:
        """Research market intelligence and sentiment"""
        return Task(
            config=self.tasks_config['research_market_intelligence'],
            agent=self.news_and_sentiment_researcher(),
            context=[self.select_trading_assets_task()]
        )
    
    @task
    def perform_advanced_analysis_task(self) -> Task:
        """Perform comprehensive analysis of selected assets"""
        return Task(
            config=self.tasks_config['perform_advanced_analysis'],
            agent=self.crypto_analyst(),
            context=[
                self.fetch_comprehensive_market_data_task(),
                self.research_market_intelligence_task()
            ]
        )
    
    @task
    def assess_portfolio_risk_task(self) -> Task:
        """Assess portfolio risk and calculate position sizes"""
        return Task(
            config=self.tasks_config['assess_portfolio_risk'],
            agent=self.risk_manager(),
            context=[
                self.perform_advanced_analysis_task(),
                self.select_trading_assets_task()
            ]
        )
    
    @task
    def optimize_portfolio_allocation_task(self) -> Task:
        """Optimize portfolio allocation and strategy"""
        return Task(
            config=self.tasks_config['optimize_portfolio_allocation'],
            agent=self.portfolio_manager(),
            context=[
                self.assess_portfolio_risk_task(),
                self.perform_advanced_analysis_task()
            ]
        )
    
    @task
    def execute_trading_strategy_task(self) -> Task:
        """Execute the trading strategy"""
        return Task(
            config=self.tasks_config['execute_trading_strategy'],
            agent=self.trade_executor(),
            context=[
                self.optimize_portfolio_allocation_task(),
                self.assess_portfolio_risk_task()
            ]
        )
    
    @task
    def monitor_performance_task(self) -> Task:
        """Monitor and analyze performance"""
        return Task(
            config=self.tasks_config['monitor_performance'],
            agent=self.performance_monitor(),
            context=[self.execute_trading_strategy_task()]
        )
    
    @task
    def coordinate_autonomous_trading_task(self) -> Task:
        """Master coordination task"""
        return Task(
            config=self.tasks_config['coordinate_autonomous_trading'],
            agent=self.strategy_coordinator(),
            context=[
                self.monitor_performance_task(),
                self.execute_trading_strategy_task(),
                self.optimize_portfolio_allocation_task()
            ]
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates and configures the complete Autonomous Crypto Trading Crew.
        """
        try:
            return Crew(
                agents=[
                    self.market_scanner(),
                    self.asset_selector(),
                    self.market_data_analyst(),
                    self.news_and_sentiment_researcher(),
                    self.crypto_analyst(),
                    self.risk_manager(),
                    self.portfolio_manager(),
                    self.trade_executor(),
                    self.performance_monitor(),
                    self.strategy_coordinator()
                ],
                tasks=[
                    self.scan_market_opportunities_task(),
                    self.select_trading_assets_task(),
                    self.fetch_comprehensive_market_data_task(),
                    self.research_market_intelligence_task(),
                    self.perform_advanced_analysis_task(),
                    self.assess_portfolio_risk_task(),
                    self.optimize_portfolio_allocation_task(),
                    self.execute_trading_strategy_task(),
                    self.monitor_performance_task(),
                    self.coordinate_autonomous_trading_task()
                ],
                process=Process.sequential,
                verbose=self.verbose
            )
        except Exception as e:
            logger.error(f"Failed to create autonomous crew: {e}")
            raise

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validates input parameters for the autonomous trading crew.
        """
        # For autonomous mode, we need minimal inputs as the crew discovers opportunities
        required_keys = ['current_datetime', 'filename_datetime']
        
        for key in required_keys:
            if key not in inputs:
                error_msg = f"Missing required input: {key}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate paper trading mode
        if 'paper_trading' in inputs:
            if not isinstance(inputs['paper_trading'], bool):
                logger.warning("paper_trading should be boolean, defaulting to True")
                inputs['paper_trading'] = True
        
        return True

    def get_autonomous_inputs(self, additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create inputs for autonomous trading mode
        """
        from datetime import datetime
        
        now = datetime.now()
        base_inputs = {
            'current_datetime': now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'filename_datetime': now.strftime("%Y%m%d_%H%M%S"),
            'paper_trading': self.paper_trading,
            'mode': 'autonomous'
        }
        
        if additional_params:
            base_inputs.update(additional_params)
        
        return base_inputs