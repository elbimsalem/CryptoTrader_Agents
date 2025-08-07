#!/usr/bin/env python3
"""
Smart Scheduler Runner for Autonomous Cryptocurrency Trading
Easy-to-use script for running the intelligent trading scheduler
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crypto_trader.smart_scheduler import SmartScheduler, ScheduleConfig

def main():
    print("🚀 Autonomous Crypto Trading - Smart Scheduler")
    print("=" * 50)
    
    # Configuration options
    print("\n📊 Current Configuration:")
    config = ScheduleConfig()
    print(f"   Monitor interval: {config.monitor_interval} minutes (price checks)")
    print(f"   Quick scan: {config.quick_scan_interval} minutes (~2K tokens)")
    print(f"   Medium analysis: {config.medium_analysis_interval} minutes (~8K tokens)")  
    print(f"   Full analysis: {config.full_analysis_interval} minutes (~25K tokens)")
    print(f"   Volatility threshold: {config.high_volatility_threshold:.1%}")
    print(f"   Volume surge threshold: {config.volume_surge_threshold:.1%}")
    
    # Token limit options
    print("\n💰 Token Usage Presets:")
    print("   1. Conservative: 50,000 tokens/day (~$5-10 estimated)")
    print("   2. Moderate: 100,000 tokens/day (~$10-20 estimated)")  
    print("   3. Aggressive: 200,000 tokens/day (~$20-40 estimated)")
    print("   4. Custom amount")
    
    try:
        choice = input("\nSelect token limit (1-4): ").strip()
        
        if choice == "1":
            max_tokens = 50000
        elif choice == "2":
            max_tokens = 100000
        elif choice == "3":
            max_tokens = 200000
        elif choice == "4":
            max_tokens = int(input("Enter daily token limit: "))
        else:
            max_tokens = 100000  # Default
            
        print(f"\n🎯 Daily token limit set to: {max_tokens:,}")
        
        # Confirm start
        input("\nPress Enter to start the Smart Scheduler (Ctrl+C to stop)...")
        
        # Start scheduler
        scheduler = SmartScheduler(config)
        scheduler.run_continuous(max_daily_tokens=max_tokens)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Smart Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())