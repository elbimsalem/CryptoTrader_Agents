"""
Autonomous Cryptocurrency Trading System
Main entry point for autonomous multi-asset trading operations
"""
import os
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime

from crypto_trader.autonomous_crew import AutonomousCryptoTradingCrew
from crypto_trader.ionos_llm import print_model_assignments

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("autonomous_crypto_trader")

def setup_environment() -> bool:
    """
    Set up the environment by loading environment variables from .env file.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        logger.info(f".env loaded from: {dotenv_path}")
    else:
        logger.warning(f".env file not found at {dotenv_path}. Using environment variables.")
    
    # Check for necessary API keys
    missing_critical_keys = False
    
    # IONOS Cloud API Key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found. Required for IONOS Cloud LLM access.")
        missing_critical_keys = True
    
    # Binance API Keys (required for live trading)
    if not os.getenv("BINANCE_API_KEY") or not os.getenv("BINANCE_API_SECRET"):
        logger.warning("Binance API credentials not found. Running in paper trading mode only.")
    
    # Optional but recommended
    if not os.getenv("SERPER_API_KEY"):
        logger.warning("SERPER_API_KEY not found. News research capabilities may be limited.")
    
    return not missing_critical_keys

def prepare_output_directory(output_dir: str) -> Path:
    """Create and prepare the output directory for storing results."""
    project_root = Path(__file__).resolve().parent.parent.parent
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_path}")
    return output_path

def save_trading_strategy(content: Any, output_dir: Path, filename: str) -> Path:
    """Save the autonomous trading strategy to a file."""
    file_path = output_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        if hasattr(content, '__str__'):
            f.write(str(content))
        else:
            f.write(content)
    return file_path

def create_autonomous_inputs(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create inputs for autonomous trading mode."""
    now = datetime.now()
    
    return {
        'current_datetime': now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        'filename_datetime': now.strftime("%Y%m%d_%H%M%S"),
        'paper_trading': config.get('paper_trading', True),
        'max_positions': config.get('max_positions', 5),
        'max_allocation_per_asset': config.get('max_allocation_per_asset', 0.3),
        'target_portfolio_volatility': config.get('target_portfolio_volatility', 0.20),
        'mode': 'autonomous'
    }

def run_autonomous_crew(inputs: Dict[str, Any], output_dir: Path) -> Optional[str]:
    """Initialize and run the Autonomous Crypto Trading Crew."""
    crew_instance = AutonomousCryptoTradingCrew(
        verbose=inputs.get('verbose', True),
        paper_trading=inputs.get('paper_trading', True)
    ).crew()
    
    logger.info("🚀 Starting Autonomous Cryptocurrency Trading System...")
    logger.info(f"📊 Mode: {'Paper Trading' if inputs.get('paper_trading', True) else 'Live Trading'}")
    
    try:
        result = crew_instance.kickoff(inputs=inputs)
        
        logger.info("\n✅ Autonomous trading analysis completed!")
        output_filename = f"autonomous_trading_strategy_{inputs['filename_datetime']}.md"
        file_path = save_trading_strategy(result, output_dir, output_filename)
        logger.info(f"📝 Strategy saved to: {file_path}")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error during autonomous trading execution: {e}", exc_info=True)
        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Cryptocurrency Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in paper trading mode (default)
  python -m crypto_trader.autonomous_main
  
  # Run with custom parameters
  python -m crypto_trader.autonomous_main --max-positions 3 --max-allocation 0.25
  
  # Live trading mode (requires Binance API credentials)
  python -m crypto_trader.autonomous_main --live-trading --confirm
  
  # Show model assignments
  python -m crypto_trader.autonomous_main --show-models
        """
    )
    
    parser.add_argument("--paper-trading", action="store_true", default=True,
                        help="Enable paper trading mode (default)")
    parser.add_argument("--live-trading", action="store_true", default=False,
                        help="Enable live trading mode (requires confirmation)")
    parser.add_argument("--confirm", action="store_true", default=False,
                        help="Confirm live trading mode")
    
    parser.add_argument("--max-positions", type=int, default=5,
                        help="Maximum number of concurrent positions (default: 5)")
    parser.add_argument("--max-allocation", type=float, default=0.3,
                        help="Maximum allocation per asset (default: 0.3)")
    parser.add_argument("--target-volatility", type=float, default=0.20,
                        help="Target portfolio volatility (default: 0.20)")
    
    parser.add_argument("--output", "-o", type=str, default="output",
                        help="Output directory (default: output)")
    parser.add_argument("--verbose", "-v", action="store_true", default=True,
                        help="Enable verbose logging")
    parser.add_argument("--show-models", action="store_true", default=False,
                        help="Show IONOS model assignments and exit")
    
    return parser.parse_args()

def main():
    """Main function for autonomous cryptocurrency trading."""
    args = parse_arguments()
    
    # Show model assignments if requested
    if args.show_models:
        print_model_assignments()
        return
    
    # Set logging level
    if args.verbose:
        logging.getLogger("crypto_trader").setLevel(logging.DEBUG)
    
    # Validate live trading confirmation
    if args.live_trading and not args.confirm:
        logger.error("❌ Live trading requires --confirm flag for safety")
        logger.error("⚠️  Live trading involves real money and risk!")
        return
    
    # Setup environment
    if not setup_environment():
        logger.error("❌ Environment setup failed. Check API keys.")
        return
    
    # Additional live trading checks
    if args.live_trading:
        if not os.getenv("BINANCE_API_KEY") or not os.getenv("BINANCE_API_SECRET"):
            logger.error("❌ Live trading requires Binance API credentials")
            return
        
        logger.warning("⚠️  LIVE TRADING MODE ENABLED - REAL MONEY AT RISK!")
        logger.warning("⚠️  System will execute actual trades on Binance")
        
        # Final confirmation
        confirmation = input("Type 'CONFIRM LIVE TRADING' to proceed: ")
        if confirmation != "CONFIRM LIVE TRADING":
            logger.info("Live trading cancelled by user")
            return
    
    # Create configuration
    config = {
        'paper_trading': not args.live_trading,
        'max_positions': args.max_positions,
        'max_allocation_per_asset': args.max_allocation,
        'target_portfolio_volatility': args.target_volatility,
        'verbose': args.verbose
    }
    
    # Validate configuration
    if not (1 <= config['max_positions'] <= 10):
        logger.error("Max positions must be between 1 and 10")
        return
    
    if not (0.05 <= config['max_allocation_per_asset'] <= 0.5):
        logger.error("Max allocation per asset must be between 5% and 50%")
        return
    
    if not (0.1 <= config['target_portfolio_volatility'] <= 0.5):
        logger.error("Target portfolio volatility must be between 10% and 50%")
        return
    
    # Prepare output directory
    output_dir = prepare_output_directory(args.output)
    
    # Create inputs for autonomous trading
    inputs = create_autonomous_inputs(config)
    
    logger.info("🤖 Autonomous Crypto Trading System Configuration:")
    logger.info(f"   📊 Trading Mode: {'Live Trading' if not inputs['paper_trading'] else 'Paper Trading'}")
    logger.info(f"   📈 Max Positions: {inputs['max_positions']}")
    logger.info(f"   🎯 Max Allocation per Asset: {inputs['max_allocation_per_asset']:.1%}")
    logger.info(f"   📉 Target Portfolio Volatility: {inputs['target_portfolio_volatility']:.1%}")
    
    # Run the autonomous trading crew
    result = run_autonomous_crew(inputs, output_dir)
    
    # Display results
    if result:
        logger.info("✅ Autonomous trading analysis completed successfully!")
        logger.info("📊 Check the output file for detailed strategy and recommendations")
    else:
        logger.error("❌ Autonomous trading analysis failed")

if __name__ == "__main__":
    main()