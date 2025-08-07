"""
Test Mode Crew for Extended Autonomous Trading Simulation
Combines autonomous trading analysis with portfolio simulation and reporting
"""
import logging
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task

# Import base autonomous crew
from .autonomous_crew import AutonomousCryptoTradingCrew, AutonomousToolManager

# Import test mode components
from .portfolio_simulator import PortfolioSimulator, DailyReport
from .tools.portfolio_simulator_tool import PortfolioSimulatorTool

# Import LLM configurations
from langchain_openai import ChatOpenAI
import os

def get_test_mode_llm():
    """Get LLM configuration for test mode agents"""
    return ChatOpenAI(
        model="openai/meta-llama/Meta-Llama-3.1-8B-Instruct",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("IONOS_BASE_URL", "https://openai.inference.de-txl.ionos.com/v1"),
        temperature=0.1,
        max_tokens=3000
    )

# Configure logging
logger = logging.getLogger("crypto_trader.test_mode_crew")

class TestModeToolManager:
    """Tool manager for test mode operations"""
    
    def __init__(self, portfolio_simulator: PortfolioSimulator):
        self.base_tool_manager = AutonomousToolManager.get_instance()
        self.portfolio_simulator = portfolio_simulator
        self._tools = {}
    
    def get_portfolio_simulator_tool(self) -> PortfolioSimulatorTool:
        """Get portfolio simulator tool"""
        if 'portfolio_simulator' not in self._tools:
            self._tools['portfolio_simulator'] = PortfolioSimulatorTool(
                portfolio_simulator=self.portfolio_simulator
            )
        return self._tools['portfolio_simulator']
    
    def get_binance_direct_tool(self):
        """Get Binance Direct tool from base manager"""
        return self.base_tool_manager.get_binance_direct_tool()
    
    def get_serper_tool(self):
        """Get Serper tool from base manager"""
        return self.base_tool_manager.get_serper_tool()

@CrewBase
class TestModeCryptoTradingCrew():
    """
    Extended crew for autonomous crypto trading with portfolio simulation
    and comprehensive reporting capabilities
    """
    
    agents_config = 'config/enhanced_agents.yaml'
    tasks_config = 'config/autonomous_tasks.yaml'
    
    def __init__(self, initial_balance: float = 10000.0, verbose: bool = False):
        super().__init__()
        self.verbose = verbose
        
        # Initialize portfolio simulator
        self.portfolio_simulator = PortfolioSimulator(initial_balance=initial_balance)
        
        # Initialize tool manager
        self.tool_manager = TestModeToolManager(self.portfolio_simulator)
        
        # Load configurations
        self._load_configs()
        
        # Initialize base autonomous crew
        self.base_crew = AutonomousCryptoTradingCrew(verbose=verbose)
        
        logger.info(f"TestModeCryptoTradingCrew initialized with ${initial_balance:,.2f} starting balance")
    
    def _load_configs(self):
        """Load test mode agent and task configurations"""
        try:
            import os
            current_dir = os.path.dirname(__file__)
            
            # Load test mode agents
            test_agents_path = os.path.join(current_dir, 'config', 'test_mode_agents.yaml')
            with open(test_agents_path, 'r') as f:
                self.test_agents_data = yaml.safe_load(f)
            
            # Load test mode tasks
            test_tasks_path = os.path.join(current_dir, 'config', 'test_mode_tasks.yaml')
            with open(test_tasks_path, 'r') as f:
                self.test_tasks_data = yaml.safe_load(f)
                
        except Exception as e:
            logger.error(f"Failed to load test mode configurations: {e}")
            self.test_agents_data = {}
            self.test_tasks_data = {}
    
    # Test Mode Agents
    @agent
    def portfolio_simulator_agent(self) -> Agent:
        """Virtual Portfolio Manager & Trade Simulator"""
        return Agent(
            config=self.test_agents_data.get('portfolio_simulator', {
                'role': 'Virtual Portfolio Manager',
                'goal': 'Execute virtual trades and track portfolio performance',
                'backstory': 'Expert at portfolio simulation and trade execution'
            }),
            tools=[self.tool_manager.get_portfolio_simulator_tool()],
            llm=get_test_mode_llm(),
            verbose=self.verbose
        )
    
    @agent  
    def daily_reporter_agent(self) -> Agent:
        """Performance Analyst & Report Generator"""
        return Agent(
            config=self.test_agents_data.get('daily_reporter', {
                'role': 'Performance Analyst',
                'goal': 'Generate comprehensive daily performance reports',
                'backstory': 'Specialist in trading performance analysis and reporting'
            }),
            tools=[],
            llm=get_test_mode_llm(),
            verbose=self.verbose
        )
    
    @agent
    def trade_logger_agent(self) -> Agent:
        """Trade Execution Logger & Audit Specialist"""
        return Agent(
            config=self.test_agents_data.get('trade_logger', {
                'role': 'Trade Logger',
                'goal': 'Maintain comprehensive trading logs and audit trails',
                'backstory': 'Expert at documentation and compliance tracking'
            }),
            tools=[],
            llm=get_test_mode_llm(),
            verbose=self.verbose
        )
    
    @agent
    def market_benchmark_agent(self) -> Agent:
        """Market Benchmark & Comparison Analyst"""
        return Agent(
            config=self.test_agents_data.get('market_benchmark', {
                'role': 'Benchmark Analyst',
                'goal': 'Compare performance against market benchmarks',
                'backstory': 'Specialist in comparative performance analysis'
            }),
            tools=[self.tool_manager.get_binance_direct_tool()],
            llm=get_test_mode_llm(),
            verbose=self.verbose
        )
    
    # Test Mode Tasks
    @task
    def execute_virtual_trades_task(self) -> Task:
        """Execute virtual trades based on crew recommendations"""
        return Task(
            config=self.test_tasks_data.get('execute_virtual_trades', {
                'description': 'Execute virtual trades using portfolio simulator',
                'expected_output': 'Virtual trade execution report'
            }),
            agent=self.portfolio_simulator_agent(),
            context=[self.base_crew.coordinate_autonomous_trading_task()]
        )
    
    @task
    def log_trading_actions_task(self) -> Task:
        """Log all trading decisions and actions"""
        return Task(
            config=self.test_tasks_data.get('log_trading_actions', {
                'description': 'Log comprehensive trading session information',
                'expected_output': 'Complete trading session log'
            }),
            agent=self.trade_logger_agent(),
            context=[
                self.execute_virtual_trades_task(),
                self.base_crew.coordinate_autonomous_trading_task()
            ]
        )
    
    @task
    def generate_daily_report_task(self) -> Task:
        """Generate daily performance report"""
        return Task(
            config=self.test_tasks_data.get('generate_daily_report', {
                'description': 'Generate comprehensive daily performance report',
                'expected_output': 'Daily performance analysis report'
            }),
            agent=self.daily_reporter_agent(),
            context=[
                self.log_trading_actions_task(),
                self.execute_virtual_trades_task()
            ]
        )
    
    @task
    def benchmark_performance_task(self) -> Task:
        """Compare performance against market benchmarks"""
        return Task(
            config=self.test_tasks_data.get('benchmark_performance', {
                'description': 'Analyze performance vs market benchmarks',
                'expected_output': 'Benchmark comparison analysis'
            }),
            agent=self.market_benchmark_agent(),
            context=[self.generate_daily_report_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the complete test mode crew"""
        try:
            # Get all base crew agents and tasks
            base_agents = [
                self.base_crew.market_scanner(),
                self.base_crew.asset_selector(), 
                self.base_crew.market_data_analyst(),
                self.base_crew.news_and_sentiment_researcher(),
                self.base_crew.crypto_analyst(),
                self.base_crew.risk_manager(),
                self.base_crew.portfolio_manager(),
                self.base_crew.trade_executor(),
                self.base_crew.performance_monitor(),
                self.base_crew.strategy_coordinator()
            ]
            
            base_tasks = [
                self.base_crew.scan_market_opportunities_task(),
                self.base_crew.select_trading_assets_task(),
                self.base_crew.fetch_comprehensive_market_data_task(),
                self.base_crew.research_market_intelligence_task(),
                self.base_crew.perform_advanced_analysis_task(),
                self.base_crew.assess_portfolio_risk_task(),
                self.base_crew.optimize_portfolio_allocation_task(),
                self.base_crew.execute_trading_strategy_task(),
                self.base_crew.monitor_performance_task(),
                self.base_crew.coordinate_autonomous_trading_task()
            ]
            
            # Add test mode agents and tasks
            test_agents = [
                self.portfolio_simulator_agent(),
                self.trade_logger_agent(),
                self.daily_reporter_agent(),
                self.market_benchmark_agent()
            ]
            
            test_tasks = [
                self.execute_virtual_trades_task(),
                self.log_trading_actions_task(),
                self.generate_daily_report_task(),
                self.benchmark_performance_task()
            ]
            
            return Crew(
                agents=base_agents + test_agents,
                tasks=base_tasks + test_tasks,
                process=Process.sequential,
                verbose=self.verbose
            )
            
        except Exception as e:
            logger.error(f"Failed to create test mode crew: {e}")
            raise
    
    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Get current portfolio summary"""
        return self.portfolio_simulator.get_portfolio_summary(current_prices)
    
    def should_generate_daily_report(self) -> bool:
        """Check if daily report should be generated"""
        return self.portfolio_simulator.should_generate_daily_report()
    
    def generate_daily_report(self, current_prices: Dict[str, float]) -> DailyReport:
        """Generate daily report using portfolio simulator"""
        return self.portfolio_simulator.generate_daily_report(current_prices)
    
    def reset_simulation(self, new_balance: Optional[float] = None):
        """Reset the portfolio simulation"""
        self.portfolio_simulator.reset_portfolio(new_balance)
        logger.info("Portfolio simulation reset")
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        return {
            'days_running': (datetime.now().date() - self.portfolio_simulator.start_date).days + 1,
            'total_trades': len(self.portfolio_simulator.trades),
            'total_reports': len(self.portfolio_simulator.daily_reports),
            'current_balance': self.portfolio_simulator.current_balance,
            'positions_count': len(self.portfolio_simulator.positions)
        }

def run_test_mode_crew(initial_balance: float = 10000.0, verbose: bool = False) -> Any:
    """
    Run the test mode autonomous trading crew
    
    Args:
        initial_balance: Starting portfolio balance in USD
        verbose: Enable verbose logging
        
    Returns:
        Crew execution results
    """
    try:
        # Create inputs
        inputs = {
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename_datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'initial_balance': initial_balance,
            'test_mode': True
        }
        
        # Create and run crew
        test_crew = TestModeCryptoTradingCrew(
            initial_balance=initial_balance,
            verbose=verbose
        )
        
        logger.info(f"Starting test mode crew with ${initial_balance:,.2f} initial balance")
        result = test_crew.kickoff(inputs=inputs)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in test mode crew execution: {e}")
        raise