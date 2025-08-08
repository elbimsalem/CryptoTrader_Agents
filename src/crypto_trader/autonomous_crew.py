"""
Autonomous Cryptocurrency Trading Crew
Enhanced multi-agent system for autonomous crypto trading
"""
import logging
import time
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tools
from .tools.binance_direct_tool import BinanceDirectTool
try:
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool
except ImportError:
    # Fallback if tools are not available
    SerperDevTool = None
    ScrapeWebsiteTool = None

# Import IONOS LLM configurations
from langchain_openai import ChatOpenAI
import os

def get_ionos_llm(model: str = "openai/meta-llama/Meta-Llama-3.1-8B-Instruct", 
                  temperature: float = 0.1, 
                  max_tokens: int = 2000,
                  max_retries: int = 3):
    """
    Get IONOS LLM configuration with enhanced retry logic and error handling
    
    Args:
        model: Model name to use
        temperature: Temperature for generation
        max_tokens: Maximum tokens per response
        max_retries: Maximum number of retry attempts
    """
    import time
    import random
    
    # Clear any conflicting environment variables first
    if "OPENAI_BASE_URL" in os.environ:
        del os.environ["OPENAI_BASE_URL"]
    
    # Set the correct environment variables for IONOS
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = "https://openai.inference.de-txl.ionos.com/v1"
    
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = base_url
    
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY is required for IONOS LLM")
    
    # Enhanced configuration with retry logic
    config = {
        "model": model,
        "openai_api_key": api_key,
        "openai_api_base": base_url,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": 120,  # Increased timeout for stability
        "max_retries": max_retries,
        # Enhanced retry configuration
        "request_timeout": 120,
        "max_network_retries": max_retries
    }
    
    logger.info(f"Initializing IONOS LLM with model: {model}, max_retries: {max_retries}")
    
    try:
        llm = ChatOpenAI(**config)
        # Test the connection with a simple ping
        logger.debug("Testing IONOS LLM connection...")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize IONOS LLM: {e}")
        # Fallback strategy could be implemented here
        raise

class CrewRetryHandler:
    """Enhanced retry handler for CrewAI operations"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(f"{__name__}.CrewRetryHandler")
    
    def exponential_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""
        import random
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter (±25% of delay)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return max(0.1, delay + jitter)
    
    def is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable"""
        import litellm
        
        # Connection-related errors
        retryable_patterns = [
            "connection error", "timeout", "503", "502", "500", 
            "rate limit", "too many requests", "network", "connection",
            "ConnectionError", "TimeoutError", "ReadTimeout"
        ]
        
        error_str = str(error).lower()
        
        # Check for specific LiteLLM errors
        if hasattr(litellm, 'exceptions'):
            if isinstance(error, (litellm.exceptions.Timeout, litellm.exceptions.APIConnectionError)):
                return True
            if isinstance(error, litellm.exceptions.RateLimitError):
                return True
            if isinstance(error, litellm.exceptions.InternalServerError):
                return True
        
        # Check for pattern matches
        return any(pattern in error_str for pattern in retryable_patterns)
    
    def execute_with_retry(self, operation, operation_name: str = "operation", *args, **kwargs):
        """Execute an operation with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.exponential_backoff_delay(attempt - 1)
                    self.logger.info(f"Retrying {operation_name} (attempt {attempt + 1}/{self.max_retries + 1}) after {delay:.2f}s delay")
                    time.sleep(delay)
                
                result = operation(*args, **kwargs)
                
                if attempt > 0:
                    self.logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries and self.is_retryable_error(e):
                    self.logger.warning(f"{operation_name} failed on attempt {attempt + 1}: {e}")
                    continue
                else:
                    if attempt >= self.max_retries:
                        self.logger.error(f"{operation_name} failed after {self.max_retries + 1} attempts")
                    else:
                        self.logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    break
        
        raise last_error

# Configure logging
logger = logging.getLogger("crypto_trader.autonomous_crew")

class AutonomousToolManager:
    """
    Enhanced tool manager for autonomous trading operations
    """
    _instance = None
    _tools: Dict[str, Any] = {}
    
    def __init__(self):
        self._portfolio_simulator = None
    
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
    
    def get_serper_tool(self):
        """Get or create the SerperDev search tool instance"""
        if SerperDevTool is None:
            logger.warning("SerperDevTool is not available - install crewai-tools")
            return None
            
        if 'serper' not in self._tools:
            try:
                self._tools['serper'] = SerperDevTool()
                logger.debug("SerperDevTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SerperDevTool: {e}")
                return None
        return self._tools['serper']
    
    def get_scrape_tool(self):
        """Get or create the website scraping tool instance"""
        if ScrapeWebsiteTool is None:
            logger.warning("ScrapeWebsiteTool is not available - install crewai-tools")  
            return None
            
        if 'scrape' not in self._tools:
            try:
                self._tools['scrape'] = ScrapeWebsiteTool()
                logger.debug("ScrapeWebsiteTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ScrapeWebsiteTool: {e}")
                return None
        return self._tools['scrape']
    
    def set_portfolio_simulator(self, portfolio_simulator):
        """Set the portfolio simulator instance for virtual trading"""
        self._portfolio_simulator = portfolio_simulator
    
    def get_portfolio_simulator_tool(self):
        """Get portfolio simulator tool for virtual trading"""
        if self._portfolio_simulator is None:
            logger.error("Portfolio simulator not set - cannot create portfolio simulator tool")
            return None
            
        if 'portfolio_simulator' not in self._tools:
            try:
                from .tools.portfolio_simulator_tool import PortfolioSimulatorTool
                self._tools['portfolio_simulator'] = PortfolioSimulatorTool(
                    portfolio_simulator=self._portfolio_simulator
                )
                logger.debug("PortfolioSimulatorTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PortfolioSimulatorTool: {e}")
                return None
        return self._tools['portfolio_simulator']

@CrewBase
class AutonomousCryptoTradingCrew:
    """
    Advanced autonomous cryptocurrency trading crew with multi-asset capabilities,
    risk management, and automated execution.
    """
    agents_config = 'config/enhanced_agents.yaml'
    tasks_config = 'config/autonomous_tasks.yaml'
    
    def __init__(self, verbose: bool = True, paper_trading: bool = True, portfolio_simulator=None, 
                 retry_config: Dict[str, Any] = None):
        """
        Initialize the Autonomous Crypto Trading Crew.
        
        Args:
            verbose: Whether to enable verbose output from agents and tasks
            paper_trading: If True, simulate trades without actual execution
            portfolio_simulator: Portfolio simulator instance for virtual trading (required if paper_trading=True)
            retry_config: Configuration for retry logic (max_retries, base_delay, max_delay)
        """
        self.verbose = verbose
        self.paper_trading = paper_trading
        self.tool_manager = AutonomousToolManager.get_instance()
        
        # Set up retry handler
        retry_defaults = {"max_retries": 3, "base_delay": 1.0, "max_delay": 60.0}
        if retry_config:
            retry_defaults.update(retry_config)
        self.retry_handler = CrewRetryHandler(**retry_defaults)
        logger.info(f"Retry handler initialized: max_retries={retry_defaults['max_retries']}, "
                   f"base_delay={retry_defaults['base_delay']}, max_delay={retry_defaults['max_delay']}")
        
        # Set up portfolio simulator if provided
        if paper_trading and portfolio_simulator is not None:
            self.tool_manager.set_portfolio_simulator(portfolio_simulator)
            logger.info("Portfolio simulator configured for virtual trading")
        elif paper_trading and portfolio_simulator is None:
            logger.warning("Paper trading enabled but no portfolio simulator provided - will create default simulator")
            # Create default portfolio simulator
            try:
                from .portfolio_simulator import PortfolioSimulator
                default_simulator = PortfolioSimulator(initial_balance=10000.0)
                self.tool_manager.set_portfolio_simulator(default_simulator)
                logger.info("Created default portfolio simulator with $10,000 balance")
            except Exception as e:
                logger.error(f"Failed to create default portfolio simulator: {e}")
        
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
        tools = []
        serper = self.tool_manager.get_serper_tool()
        scrape = self.tool_manager.get_scrape_tool()
        
        if serper:
            tools.append(serper)
        if scrape:
            tools.append(scrape)
            
        return Agent(
            config=self.agents_config['news_and_sentiment_researcher'],
            tools=tools,
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
        """Trade execution specialist - uses virtual or real trading based on paper_trading setting"""
        if self.paper_trading:
            # Use portfolio simulator for virtual trading
            portfolio_tool = self.tool_manager.get_portfolio_simulator_tool()
            if portfolio_tool is None:
                logger.error("Portfolio simulator tool not available - falling back to paper trading mode")
                tools = []  # No tools available
            else:
                tools = [portfolio_tool]
                
            # Create virtual trade executor configuration
            config = {
                'role': 'Virtual Trade Execution Specialist',
                'goal': 'Execute virtual trades using portfolio simulation instead of real exchanges',
                'backstory': 'Specialist in virtual trade execution and portfolio simulation for testing strategies'
            }
        else:
            # Use real Binance API for live trading
            tools = [self.tool_manager.get_binance_direct_tool()]
            config = self.agents_config['trade_executor']
            
        return Agent(
            config=config,
            tools=tools,
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
    
    def kickoff_with_retry(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Execute crew kickoff with enhanced retry logic and error handling
        
        Args:
            inputs: Input parameters for the crew execution
            
        Returns:
            Crew execution results
        """
        if inputs is None:
            inputs = self.get_autonomous_inputs()
        
        # Validate inputs
        self.validate_inputs(inputs)
        
        def _execute_crew():
            """Internal crew execution function"""
            crew_instance = self.crew()
            return crew_instance.kickoff(inputs=inputs)
        
        # Execute with retry logic
        return self.retry_handler.execute_with_retry(
            operation=_execute_crew,
            operation_name="Crew Kickoff"
        )
    
    def kickoff_single_task_with_retry(self, task_name: str, inputs: Dict[str, Any] = None) -> Any:
        """
        Execute a single task with retry logic for testing/debugging
        
        Args:
            task_name: Name of the task method to execute
            inputs: Input parameters
            
        Returns:
            Task execution results
        """
        if inputs is None:
            inputs = self.get_autonomous_inputs()
            
        def _execute_single_task():
            """Internal single task execution"""
            if hasattr(self, task_name):
                task_method = getattr(self, task_name)
                task_instance = task_method()
                agent = task_instance.agent
                
                # Create a minimal crew with just this task
                single_task_crew = Crew(
                    agents=[agent],
                    tasks=[task_instance],
                    process=Process.sequential,
                    verbose=self.verbose
                )
                
                return single_task_crew.kickoff(inputs=inputs)
            else:
                raise ValueError(f"Task method '{task_name}' not found")
        
        return self.retry_handler.execute_with_retry(
            operation=_execute_single_task,
            operation_name=f"Single Task: {task_name}"
        )