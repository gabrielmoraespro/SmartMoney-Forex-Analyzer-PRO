"""
Configurações centralizadas para o Smart Money Forex Analyzer Pro
"""

import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class APIEndpoints:
    """URLs de APIs gratuitas para forex e análise financeira"""
    
    # APIs de Forex GRATUITAS
    FIXER_IO = "http://data.fixer.io/api"  # 100 req/mês grátis
    EXCHANGERATE_API = "https://api.exchangerate-api.com/v4/latest"  # Ilimitado grátis
    FREEFOREXAPI = "https://freeforexapi.com/api/live"  # Grátis
    EXCHANGERATES_API = "https://api.exchangeratesapi.io/v1"  # 1000 req/mês grátis
    FRANKFURTER = "https://api.frankfurter.app"  # Grátis, sem key
    
    # APIs de Notícias Econômicas GRATUITAS
    NEWSAPI = "https://newsapi.org/v2"  # 100 req/dia grátis
    MARKETAUX = "https://api.marketaux.com/v1"  # 100 req/dia grátis
    CURRENTS_API = "https://api.currentsapi.services/v1"  # 600 req/mês grátis
    
    # APIs de Criptomoedas GRATUITAS (para correlação)
    COINGECKO = "https://api.coingecko.com/api/v3"  # Grátis
    COINLORE = "https://api.coinlore.com/api"  # Grátis
    BLOCKCHAIN_INFO = "https://blockchain.info/ticker"  # Grátis
    
    # APIs de Commodities GRATUITAS
    METALS_API = "https://metals-api.com/api"  # 50 req/mês grátis
    
    # APIs de Dados Macroeconômicos GRATUITAS
    FRED_API = "https://api.stlouisfed.org/fred/series"  # Grátis com key
    WORLD_BANK = "https://api.worldbank.org/v2"  # Grátis
    
    # APIs de Análise Técnica GRATUITAS
    ALPHA_VANTAGE = "https://www.alphavantage.co/query"  # 5 req/min grátis
    POLYGON = "https://api.polygon.io"  # Plano grátis limitado

@dataclass
class ForexPairs:
    """Configuração de pares de forex"""
    
    MAJOR_PAIRS = [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
        "USD/CAD", "USD/CHF", "NZD/USD"
    ]
    
    MINOR_PAIRS = [
        "EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/AUD",
        "GBP/AUD", "AUD/JPY", "CAD/JPY", "CHF/JPY",
        "EUR/CAD", "EUR/CHF", "GBP/CAD", "GBP/CHF"
    ]
    
    EXOTIC_PAIRS = [
        "USD/TRY", "USD/ZAR", "USD/MXN", "USD/BRL",
        "EUR/TRY", "GBP/ZAR", "AUD/MXN", "CAD/MXN"
    ]
    
    ALL_PAIRS = MAJOR_PAIRS + MINOR_PAIRS + EXOTIC_PAIRS
    
    @classmethod
    def get_pairs_by_currency(cls, currency: str) -> List[str]:
        """Retorna pares que contêm a moeda especificada"""
        return [pair for pair in cls.ALL_PAIRS if currency in pair]

@dataclass
class TechnicalAnalysis:
    """Configurações de análise técnica"""
    
    TIMEFRAMES = {
        "1m": {"name": "1 Minuto", "minutes": 1},
        "5m": {"name": "5 Minutos", "minutes": 5},
        "15m": {"name": "15 Minutos", "minutes": 15},
        "30m": {"name": "30 Minutos", "minutes": 30},
        "1h": {"name": "1 Hora", "minutes": 60},
        "4h": {"name": "4 Horas", "minutes": 240},
        "1d": {"name": "1 Dia", "minutes": 1440},
        "1w": {"name": "1 Semana", "minutes": 10080}
    }
    
    # Configurações Smart Money
    FVG_MIN_SIZE_PIPS = 3
    FVG_MAX_AGE_HOURS = 24
    
    ORDER_BLOCK_MIN_SIZE = 5
    ORDER_BLOCK_CONFIRMATION_CANDLES = 2
    ORDER_BLOCK_MAX_AGE_HOURS = 48
    
    MSS_LOOKBACK_PERIOD = 20
    MSS_MIN_BREAK_PIPS = 2
    
    CHOCH_LOOKBACK_PERIOD = 15
    CHOCH_MIN_BREAK_PIPS = 1
    
    # Configurações Wyckoff
    ACCUMULATION_PHASES = ["PS", "SC", "AR", "ST", "SOS", "LPS", "BU"]
    DISTRIBUTION_PHASES = ["PSY", "BC", "AD", "ST", "SOW", "LPSY", "UTAD"]
    
    # Configurações de força de sinal
    SIGNAL_STRENGTH = {
        "VERY_WEAK": (0, 20),
        "WEAK": (20, 40),
        "MODERATE": (40, 60),
        "STRONG": (60, 80),
        "VERY_STRONG": (80, 100)
    }

@dataclass
class UIConfiguration:
    """Configurações da interface do usuário"""
    
    # Cores dos sinais
    SIGNAL_COLORS = {
        'FVG_Bullish': '#00ff88',
        'FVG_Bearish': '#ff4444',
        'OB_Bullish': '#4488ff',
        'OB_Bearish': '#ff8844',
        'MSS_Bullish': '#88ff44',
        'MSS_Bearish': '#ff4488',
        'ChoCh_Bullish': '#44ff88',
        'ChoCh_Bearish': '#ff4888',
        'Liquidity_Bullish': '#ffff44',
        'Liquidity_Bearish': '#ff44ff'
    }
    
    # Configurações do gráfico
    CHART_CONFIG = {
        'height': 700,
        'theme': 'plotly_dark',
        'template': 'plotly_dark',
        'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
    }
    
    # Cores para notícias
    NEWS_COLORS = {
        'High': {'color': '#ff4444', 'emoji': '🔴'},
        'Medium': {'color': '#ffaa00', 'emoji': '🟡'},
        'Low': {'color': '#00ff88', 'emoji': '🟢'}
    }
    
    # Configurações de métricas
    METRIC_COLORS = {
        'positive': '#00ff88',
        'negative': '#ff4444',
        'neutral': '#666666'
    }

@dataclass
class RiskManagement:
    """Configurações de gestão de risco"""
    
    DEFAULT_RISK_PERCENT = 1.0  # 1% do capital por trade
    MAX_RISK_PERCENT = 5.0      # Máximo 5% do capital por trade
    
    RISK_REWARD_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    DEFAULT_RR_RATIO = 2.0
    
    POSITION_SIZING_METHODS = [
        "Fixed Percentage",
        "Kelly Criterion", 
        "Optimal f",
        "Fixed Dollar Amount"
    ]
    
    STOP_LOSS_METHODS = [
        "ATR Based",
        "Support/Resistance",
        "Percentage Based",
        "Fixed Pips"
    ]

class MarketSessions:
    """Configurações de sessões de mercado"""
    
    SESSIONS = {
        "ASIAN": {
            "name": "Sessão Asiática",
            "start": "22:00",
            "end": "08:00",
            "timezone": "UTC",
            "major_pairs": ["USD/JPY", "AUD/USD", "NZD/USD"],
            "characteristics": ["Baixa volatilidade", "Movimentos laterais"]
        },
        "EUROPEAN": {
            "name": "Sessão Europeia", 
            "start": "08:00",
            "end": "16:00",
            "timezone": "UTC",
            "major_pairs": ["EUR/USD", "GBP/USD", "USD/CHF"],
            "characteristics": ["Média volatilidade", "Tendências definidas"]
        },
        "AMERICAN": {
            "name": "Sessão Americana",
            "start": "13:00", 
            "end": "22:00",
            "timezone": "UTC",
            "major_pairs": ["EUR/USD", "GBP/USD", "USD/CAD"],
            "characteristics": ["Alta volatilidade", "Grandes movimentos"]
        }
    }
    
    OVERLAP_SESSIONS = {
        "LONDON_NEW_YORK": {
            "start": "13:00",
            "end": "16:00", 
            "description": "Maior volume e volatilidade"
        },
        "TOKYO_LONDON": {
            "start": "08:00",
            "end": "09:00",
            "description": "Transição Asia-Europa"
        }
    }

class EconomicIndicators:
    """Indicadores econômicos importantes"""
    
    HIGH_IMPACT = [
        "Non-Farm Payrolls", "FOMC Meeting", "ECB Meeting",
        "CPI", "GDP", "Unemployment Rate", "Retail Sales"
    ]
    
    MEDIUM_IMPACT = [
        "PPI", "Industrial Production", "Consumer Confidence",
        "Housing Data", "Trade Balance"
    ]
    
    LOW_IMPACT = [
        "Building Permits", "Existing Home Sales",
        "Initial Jobless Claims"
    ]
    
    CURRENCY_IMPACT = {
        "USD": HIGH_IMPACT + ["FOMC", "NFP", "CPI", "PPI"],
        "EUR": ["ECB", "German CPI", "EU CPI", "German GDP"],
        "GBP": ["BOE", "UK CPI", "UK GDP", "UK Employment"],
        "JPY": ["BOJ", "Japan CPI", "Japan GDP", "Tankan Survey"],
        "AUD": ["RBA", "Australia CPI", "Employment Change"],
        "CAD": ["BOC", "Canada CPI", "Employment Change"],
        "CHF": ["SNB", "Swiss CPI", "Swiss GDP"],
        "NZD": ["RBNZ", "New Zealand CPI", "Employment Change"]
    }

class AppConfig:
    """Configuração principal da aplicação"""
    
    # Informações da aplicação
    APP_NAME = "Smart Money Forex Analyzer Pro"
    VERSION = "2.0.0"
    AUTHOR = "Smart Money Team"
    
    # Configurações de desenvolvimento
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limits para APIs
    RATE_LIMITS = {
        "FIXER_IO": {"requests_per_minute": 10, "requests_per_month": 100},
        "NEWSAPI": {"requests_per_day": 100},
        "ALPHA_VANTAGE": {"requests_per_minute": 5},
        "COINGECKO": {"requests_per_minute": 10},
        "MARKETAUX": {"requests_per_day": 100}
    }
    
    # Configurações de cache
    CACHE_CONFIG = {
        "forex_data_ttl": 300,  # 5 minutos
        "news_data_ttl": 1800,  # 30 minutos
        "economic_data_ttl": 3600,  # 1 hora
        "technical_analysis_ttl": 60  # 1 minuto
    }
    
    # Configurações de timeout
    TIMEOUT_CONFIG = {
        "api_request": 30,
        "websocket": 10,
        "data_processing": 60
    }
    
    # APIs ativas (configurar aqui quais usar)
    ACTIVE_APIS = {
        "forex": ["FRANKFURTER", "EXCHANGERATE_API", "FREEFOREXAPI"],
        "news": ["NEWSAPI", "MARKETAUX"],
        "crypto": ["COINGECKO", "COINLORE"],
        "technical": ["ALPHA_VANTAGE"]
    }
    
    # Configurações de dados de demonstração
    DEMO_CONFIG = {
        "enabled": True,
        "data_points": 500,
        "volatility": 0.001,
        "trend_strength": 0.0005
    }

# Configurações específicas para análise Smart Money
class SmartMoneyConfig:
    """Configurações específicas para análise Smart Money"""
    
    INSTITUTIONAL_LEVELS = {
        "DAILY_HIGHS_LOWS": {"importance": "High", "timeframe": "1d"},
        "WEEKLY_HIGHS_LOWS": {"importance": "Very High", "timeframe": "1w"},
        "MONTHLY_HIGHS_LOWS": {"importance": "Extreme", "timeframe": "1M"},
        "PREVIOUS_DAY_HIGH_LOW": {"importance": "Medium", "timeframe": "1d"},
        "ASIAN_SESSION_RANGE": {"importance": "Medium", "timeframe": "4h"}
    }
    
    LIQUIDITY_CONCEPTS = {
        "EQUAL_HIGHS": "Accumulation of buy stops",
        "EQUAL_LOWS": "Accumulation of sell stops", 
        "TRENDLINE_LIQUIDITY": "Stops behind trendlines",
        "PSYCHOLOGICAL_LEVELS": "Round numbers (00, 50)",
        "PREVIOUS_STRUCTURE": "Old support becomes resistance"
    }
    
    ORDER_FLOW_CONCEPTS = {
        "INDUCEMENT": "Fake breakout to grab liquidity",
        "FAIR_VALUE_GAP": "Imbalance to be filled",
        "ORDER_BLOCK": "Last supply/demand before move",
        "BREAKER_BLOCK": "Failed order block becomes opposite",
        "MITIGATION_BLOCK": "Partial fill of order block"
    }

# Constantes globais
SUPPORTED_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", 
    "CHF", "NZD", "CNY", "SEK", "NOK", "DKK"
]

COMMODITY_SYMBOLS = {
    "GOLD": "XAU/USD",
    "SILVER": "XAG/USD", 
    "OIL": "WTI/USD",
    "COPPER": "XCU/USD"
}

CRYPTO_PAIRS = [
    "BTC/USD", "ETH/USD", "XRP/USD", "LTC/USD",
    "ADA/USD", "DOT/USD", "LINK/USD", "BCH/USD"
]

# Mensagens e textos da aplicação
APP_MESSAGES = {
    "welcome": """
    🚀 **Bem-vindo ao Smart Money Forex Analyzer Pro!**
    
    Esta aplicação oferece análise institucional avançada usando apenas APIs gratuitas:
    
    **🎯 Recursos Principais:**
    - 📊 Análise Smart Money Concepts
    - 📈 Metodologia Wyckoff 
    - 📰 Calendário econômico em tempo real
    - 🔍 Identificação de Order Blocks e FVGs
    - ⚡ Market Structure Shifts
    - 💰 Gestão de risco avançada
    
    **🆓 APIs Gratuitas Integradas:**
    - Dados de Forex em tempo real
    - Notícias econômicas
    - Análise técnica
    - Correlações de mercado
    """,
    
    "api_info": """
    ### 🔑 APIs Gratuitas Disponíveis:
    
    **📊 Dados de Forex:**
    - Frankfurter (Sem API key necessária)
    - ExchangeRate-API (Ilimitado)
    - FreeForexAPI (Gratuito)
    
    **📰 Notícias Econômicas:**
    - NewsAPI (100 req/dia)
    - MarketAux (100 req/dia)
    
    **📈 Análise Técnica:**
    - Alpha Vantage (5 req/min)
    - CoinGecko (Crypto correlation)
    
    **💡 Dica:** Configure pelo menos uma API key para dados mais precisos!
    """,
    
    "disclaimer": """
    ⚠️ **AVISO IMPORTANTE:**
    
    Esta ferramenta é apenas para fins educacionais e informativos. 
    O trading de forex envolve riscos significativos e você pode perder 
    todo o seu capital investido.
    
    - Sempre use gestão de risco adequada
    - Nunca arrisque mais do que pode perder
    - Pratique em conta demo antes de operar com dinheiro real
    - Busque orientação profissional quando necessário
    """
}

# Configurações de localização
LOCALE_CONFIG = {
    "default_language": "pt_BR",
    "date_format": "%d/%m/%Y %H:%M",
    "number_format": "pt_BR",
    "timezone": "America/Sao_Paulo"
}