"""
IONOS Cloud LLM Configuration for Autonomous Crypto Trading Crew
Optimized model selection based on available IONOS models and agent requirements
"""
import os
import time
import logging
from typing import Optional, Dict, Any, Union
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("crypto_trader.ionos_llm")

class RetryableChatOpenAI(ChatOpenAI):
    """
    ChatOpenAI wrapper with intelligent retry logic for rate limiting and connection errors
    """
    
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 60.0, **kwargs):
        """
        Initialize with retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
        """
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def _should_retry(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry
        
        Args:
            error: The exception that occurred
            
        Returns:
            bool: True if should retry, False otherwise
        """
        error_str = str(error).lower()
        
        # Retry on rate limiting
        if any(phrase in error_str for phrase in [
            "rate limit", "rate_limit", "too many requests", "quota exceeded",
            "limit exceeded", "429", "throttled"
        ]):
            logger.warning(f"Rate limiting detected: {error}")
            return True
        
        # Retry on connection errors
        if any(phrase in error_str for phrase in [
            "connection error", "connection failed", "timeout", "network",
            "connection timed out", "read timeout", "connect timeout",
            "internal server error", "502", "503", "504"
        ]):
            logger.warning(f"Connection error detected: {error}")
            return True
        
        # Retry on temporary service errors
        if any(phrase in error_str for phrase in [
            "service unavailable", "temporary", "try again", "temporarily unavailable"
        ]):
            logger.warning(f"Temporary service error detected: {error}")
            return True
        
        # Don't retry on authentication, model not found, or validation errors
        if any(phrase in error_str for phrase in [
            "unauthorized", "invalid api key", "authentication failed",
            "model not found", "invalid model", "validation error",
            "bad request", "400", "401", "403", "404"
        ]):
            logger.error(f"Non-retryable error: {error}")
            return False
        
        # Default: don't retry unknown errors
        logger.error(f"Unknown error, not retrying: {error}")
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt using exponential backoff with jitter
        
        Args:
            attempt: The current retry attempt (0-indexed)
            
        Returns:
            float: Delay in seconds
        """
        # Exponential backoff: delay = base_delay * (2 ^ attempt)
        delay = self.base_delay * (2 ** attempt)
        
        # Add jitter (up to 25% of delay) to prevent thundering herd
        jitter = delay * 0.25 * (time.time() % 1)  # Use time as pseudo-random
        delay += jitter
        
        # Cap at max_delay
        return min(delay, self.max_delay)
    
    def _generate_content(self, messages, **kwargs):
        """
        Override the main method with retry logic
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Attempt the request
                return super()._generate(messages, **kwargs)
            
            except Exception as error:
                last_error = error
                
                # Check if this is the last attempt
                if attempt >= self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) exceeded for LLM request")
                    break
                
                # Check if we should retry this error
                if not self._should_retry(error):
                    break
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt)
                logger.info(f"Retrying LLM request in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(delay)
        
        # If we get here, all retries failed
        logger.error(f"LLM request failed after {self.max_retries} retries: {last_error}")
        raise last_error

class IonosLLMFactory:
    """
    Factory class for creating optimally configured IONOS Cloud LLM instances
    Based on actual available models from IONOS Cloud API
    """
    
    # Available IONOS models with their capabilities (updated from API response)
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
        # Small efficient models
        "meta-llama/Meta-Llama-3.1-8B-Instruct": {
            "context": 128000,
            "strengths": ["efficient", "fast", "general"],
            "cost": "very_low",
            "speed": "very_fast"
        },
        # Specialized models
        "meta-llama/CodeLlama-13b-Instruct-hf": {
            "context": 16000,
            "strengths": ["code", "technical", "programming"],
            "cost": "low",
            "speed": "fast"
        },
        "openGPT-X/Teuken-7B-instruct-commercial": {
            "context": 8192,
            "strengths": ["german", "multilingual", "commercial"],
            "cost": "low",
            "speed": "fast"
        },
        # Embedding models (for reference, not used for chat)
        "BAAI/bge-m3": {
            "context": 8192,
            "strengths": ["embeddings", "multilingual"],
            "cost": "very_low",
            "speed": "very_fast",
            "type": "embedding"
        },
        "BAAI/bge-large-en-v1.5": {
            "context": 512,
            "strengths": ["embeddings", "english"],
            "cost": "very_low", 
            "speed": "very_fast",
            "type": "embedding"
        },
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2": {
            "context": 512,
            "strengths": ["embeddings", "multilingual", "paraphrasing"],
            "cost": "very_low",
            "speed": "very_fast", 
            "type": "embedding"
        }
    }
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("IONOS_BASE_URL", "https://openai.inference.de-txl.ionos.com/v1")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for IONOS Cloud access")
    
    def create_llm(self, model: str, temperature: float = 0.1, max_tokens: int = 4000, **kwargs) -> RetryableChatOpenAI:
        """
        Create a RetryableChatOpenAI instance configured for IONOS Cloud with intelligent retry logic
        """
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model} not available in IONOS Cloud")
        
        # Check if model is suitable for chat (exclude embedding models)
        model_info = self.AVAILABLE_MODELS[model]
        if model_info.get("type") == "embedding":
            raise ValueError(f"Model {model} is an embedding model, not suitable for chat")
        
        # Configure retry behavior based on model tier
        retry_config = self._get_retry_config(model)
        
        config = {
            "model": f"openai/{model}",  # Use openai prefix as per working remote config
            "openai_api_key": self.api_key,
            "openai_api_base": self.base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": kwargs.get("timeout", 120),
            **retry_config  # Add retry configuration
        }
        
        config.update(kwargs)
        return RetryableChatOpenAI(**config)
    
    def _get_retry_config(self, model: str) -> Dict[str, Any]:
        """
        Get retry configuration based on model tier and expected usage
        
        Args:
            model: The model name
            
        Returns:
            Dict with retry configuration
        """
        model_info = self.AVAILABLE_MODELS[model]
        cost = model_info.get("cost", "medium")
        
        # More aggressive retries for expensive models (we want them to succeed)
        # Less aggressive retries for cheap models (fail fast, try again later)
        if cost == "high":
            return {
                "max_retries": 8,      # More retries for expensive models
                "base_delay": 2.0,     # Longer initial delay
                "max_delay": 120.0     # Up to 2 minutes max delay
            }
        elif cost == "medium":
            return {
                "max_retries": 5,      # Standard retries
                "base_delay": 1.5,     # Standard delay
                "max_delay": 60.0      # Up to 1 minute max delay
            }
        else:  # low or very_low cost
            return {
                "max_retries": 3,      # Fewer retries for cheap models
                "base_delay": 1.0,     # Shorter delay
                "max_delay": 30.0      # Up to 30 seconds max delay
            }
    
    # Optimized model assignments for each agent type
    def get_market_scanner_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Fast, efficient model for market scanning tasks"""
        return self.create_llm(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.0,  # Deterministic for data processing
            max_tokens=2000
        )
    
    def get_asset_selector_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Balanced model for asset selection analysis"""
        return self.create_llm(
            model="meta-llama/Llama-3.3-70B-Instruct",
            temperature=0.1,  # Slight creativity for selection logic
            max_tokens=3000
        )
    
    def get_market_data_analyst_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Efficient model for data analysis tasks"""
        return self.create_llm(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            temperature=0.0,  # Deterministic for data analysis
            max_tokens=3000
        )
    
    def get_news_researcher_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Large model for complex sentiment analysis"""
        return self.create_llm(
            model="meta-llama/Llama-3.1-405B-Instruct-FP8",
            temperature=0.1,  # Slight creativity for sentiment interpretation
            max_tokens=4000
        )
    
    def get_crypto_analyst_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Largest model for comprehensive analysis"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.1,  # Balanced for deep analysis
            max_tokens=6000
        )
    
    def get_risk_manager_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Precise model for risk calculations"""
        return self.create_llm(
            model="meta-llama/Llama-3.3-70B-Instruct",
            temperature=0.0,  # Very conservative for risk management
            max_tokens=3000
        )
    
    def get_portfolio_manager_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Large model for complex portfolio optimization"""
        return self.create_llm(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8",
            temperature=0.05,  # Very conservative for portfolio decisions
            max_tokens=4000
        )
    
    def get_trade_executor_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Code-specialized model for execution logic"""
        return self.create_llm(
            model="meta-llama/CodeLlama-13b-Instruct-hf",
            temperature=0.0,  # Deterministic for trade execution
            max_tokens=2000
        )
    
    def get_performance_monitor_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
        """Efficient model for monitoring tasks"""
        return self.create_llm(
            model="mistralai/Mistral-Small-24B-Instruct",
            temperature=0.0,  # Factual reporting
            max_tokens=3000
        )
    
    def get_strategy_coordinator_llm(self) -> Union[ChatOpenAI, RetryableChatOpenAI]:
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
def get_market_scanner_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_market_scanner_llm()

def get_asset_selector_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_asset_selector_llm()

def get_market_data_analyst_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_market_data_analyst_llm()

def get_news_researcher_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_news_researcher_llm()

def get_crypto_analyst_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_crypto_analyst_llm()

def get_risk_manager_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_risk_manager_llm()

def get_portfolio_manager_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_portfolio_manager_llm()

def get_trade_executor_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_trade_executor_llm()

def get_performance_monitor_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
    return get_llm_factory().get_performance_monitor_llm()

def get_strategy_coordinator_llm() -> Union[ChatOpenAI, RetryableChatOpenAI]:
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