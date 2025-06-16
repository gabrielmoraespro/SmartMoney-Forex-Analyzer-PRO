"""
Configurações básicas para Smart Money Forex Analyzer Pro
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ForexPairs:
    MAJOR_PAIRS = [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
        "USD/CAD", "USD/CHF", "NZD/USD"
    ]
    
    ALL_PAIRS = MAJOR_PAIRS

@dataclass
class AppConfig:
    APP_NAME = "Smart Money Forex Analyzer Pro"
    VERSION = "2.0.0"
    
    RATE_LIMITS = {
        "NEWSAPI": {"requests_per_day": 100},
        "ALPHA_VANTAGE": {"requests_per_minute": 5}
    }

APP_MESSAGES = {
    'welcome': """
    🚀 **Bem-vindo ao Smart Money Analyzer Pro!**
    
    Esta aplicação oferece análise institucional avançada.
    """
}
