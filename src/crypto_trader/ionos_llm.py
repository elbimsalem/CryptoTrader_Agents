"""
IONOS Cloud LLM Configuration for Autonomous Crypto Trading Crew
Optimized model selection based on available IONOS models and agent requirements
"""
import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class IonosLLMFactory:
    """
    Factory class for creating optimally configured IONOS Cloud LLM instances
    Based on actual available models from IONOS Cloud API
    """
    
    # Available IONOS models with their capabilities
    AVAILABLE_MODELS = {
        # Large reasoning models - best for complex analysis
        "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8": {
            "context": 128000,
            "strengths": ["complex reasoning", "analysis", "strategy"],
            "cost": "high",
            "speed": "slow"
        },
        # Balanced performance models - good for most tasks
        "meta-llama/Llama-3.3-70B-Instruct": {
            "context": 128000,
            "strengths": ["balanced", "reasoning", "code", "analysis"],
            "cost": "medium",
            "speed": "medium"
        },
        # Efficient models - fast execution
        "mistralai/Mistral-Small-24B-Instruct": {
            "context": 32000,
            "strengths": ["fast", "efficient", "multilingual"],
            "cost": "low",
            "speed": "fast"
        },
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {
            "context": 32000,
            "strengths": ["fast", "code", "reasoning"],
            "cost": "low",
            "speed": "fast"
        },
        "mistralai/Mistral-Nemo-Instruct-2407": {
            "context": 128000,
            "strengths": ["efficient", "multilingual", "reasoning"],
            "cost": "medium",
            "speed": "medium"
        },
        # Specialized models
        "meta-llama/CodeLlama-13b-Instruct-hf": {
            "context": 16000,
            "strengths": ["code", "technical", "programming"],
            "cost": "low",
            "speed": "fast"
        },
        "meta-llama/Meta-Llama-3.1-8B-Instruct": {
            "context": 128000,
            "strengths": ["efficient", "fast", "general"],
            "cost": "very_low",
            "speed": "very_fast"
        }
    }
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("IONOS_BASE_URL", "https://openai.inference.de-txl.ionos.com/v1")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for IONOS Cloud access")
    
    def create_llm(self, model: str, temperature: float = 0.1, max_tokens: int = 4000, **kwargs) -> ChatOpenAI:
        """
        Create a ChatOpenAI instance configured for IONOS Cloud
        """
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model} not available in IONOS Cloud")
        
        config = {
            "model": model,
            "openai_api_key": self.api_key,
            "openai_api_base": self.base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": kwargs.get("timeout", 120),
        }
        
        config.update(kwargs)
        return ChatOpenAI(**config)
    
    # Optimized model assignments for each agent type
    def get_market_scanner_llm(self) -> ChatOpenAI:
        """Fast, efficient model for market scanning tasks"""
        return self.create_llm(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.0,  # Deterministic for data processing
            max_tokens=2000
        )
    
    def get_asset_selector_llm(self) -> ChatOpenAI:
        """Balanced model for asset selection analysis"""
        return self.create_llm(
            model="meta-llama/Llama-3.3-70B-Instruct",
            temperature=0.1,  # Slight creativity for selection logic
            max_tokens=3000
        )
    
    def get_market_data_analyst_llm(self) -> ChatOpenAI:
        """Efficient model for data analysis tasks"""
        return self.create_llm(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            temperature=0.0,  # Deterministic for data analysis
            max_tokens=3000
        )
    
    def get_news_researcher_llm(self) -> ChatOpenAI:
        """Large model for complex sentiment analysis"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.1,  # Slight creativity for sentiment interpretation
            max_tokens=4000
        )
    
    def get_crypto_analyst_llm(self) -> ChatOpenAI:
        """Largest model for comprehensive analysis"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.1,  # Balanced for deep analysis
            max_tokens=6000
        )
    
    def get_risk_manager_llm(self) -> ChatOpenAI:
        """Precise model for risk calculations"""
        return self.create_llm(
            model="meta-llama/Llama-3.3-70B-Instruct",
            temperature=0.0,  # Very conservative for risk management
            max_tokens=3000
        )
    
    def get_portfolio_manager_llm(self) -> ChatOpenAI:
        """Large model for complex portfolio optimization"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.05,  # Very conservative for portfolio decisions
            max_tokens=4000
        )
    
    def get_trade_executor_llm(self) -> ChatOpenAI:
        """Code-specialized model for execution logic"""
        return self.create_llm(
            model="meta-llama/CodeLlama-13b-Instruct-hf",
            temperature=0.0,  # Deterministic for trade execution
            max_tokens=2000
        )
    
    def get_performance_monitor_llm(self) -> ChatOpenAI:
        """Efficient model for monitoring tasks"""
        return self.create_llm(
            model="mistralai/Mistral-Small-24B-Instruct",
            temperature=0.0,  # Factual reporting
            max_tokens=3000
        )
    
    def get_strategy_coordinator_llm(self) -> ChatOpenAI:
        """Largest model for strategic coordination"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.1,  # Balanced for strategic decisions
            max_tokens=5000
        )

# Global factory instance
_llm_factory = None

def get_llm_factory() -> IonosLLMFactory:
    """Get or create the global LLM factory instance"""
    global _llm_factory
    if _llm_factory is None:
        _llm_factory = IonosLLMFactory()
    return _llm_factory

# Convenience functions for each agent type
def get_market_scanner_llm() -> ChatOpenAI:
    return get_llm_factory().get_market_scanner_llm()

def get_asset_selector_llm() -> ChatOpenAI:
    return get_llm_factory().get_asset_selector_llm()

def get_market_data_analyst_llm() -> ChatOpenAI:
    return get_llm_factory().get_market_data_analyst_llm()

def get_news_researcher_llm() -> ChatOpenAI:
    return get_llm_factory().get_news_researcher_llm()

def get_crypto_analyst_llm() -> ChatOpenAI:
    return get_llm_factory().get_crypto_analyst_llm()

def get_risk_manager_llm() -> ChatOpenAI:
    return get_llm_factory().get_risk_manager_llm()

def get_portfolio_manager_llm() -> ChatOpenAI:
    return get_llm_factory().get_portfolio_manager_llm()

def get_trade_executor_llm() -> ChatOpenAI:
    return get_llm_factory().get_trade_executor_llm()

def get_performance_monitor_llm() -> ChatOpenAI:
    return get_llm_factory().get_performance_monitor_llm()

def get_strategy_coordinator_llm() -> ChatOpenAI:
    return get_llm_factory().get_strategy_coordinator_llm()

# Model assignment summary for documentation
MODEL_ASSIGNMENTS = {
    "Market Scanner": "mistralai/Mixtral-8x7B-Instruct-v0.1 (Fast data processing)",
    "Asset Selector": "meta-llama/Llama-3.3-70B-Instruct (Balanced reasoning)",
    "Market Data Analyst": "mistralai/Mistral-Nemo-Instruct-2407 (Efficient analysis)",
    "News & Sentiment Researcher": "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 (Complex NLP)",
    "Crypto Analyst": "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 (Deep analysis)",
    "Risk Manager": "meta-llama/Llama-3.3-70B-Instruct (Precise calculations)",
    "Portfolio Manager": "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 (Complex optimization)",
    "Trade Executor": "meta-llama/CodeLlama-13b-Instruct-hf (Code execution)",
    "Performance Monitor": "mistralai/Mistral-Small-24B-Instruct (Fast monitoring)",
    "Strategy Coordinator": "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 (Strategic decisions)"
}

def print_model_assignments():
    """Print the model assignments for documentation"""
    print("IONOS Cloud Model Assignments for Autonomous Trading Crew:")
    print("=" * 60)
    for agent, model_info in MODEL_ASSIGNMENTS.items():
        print(f"{agent:25} → {model_info}")
    print("=" * 60)