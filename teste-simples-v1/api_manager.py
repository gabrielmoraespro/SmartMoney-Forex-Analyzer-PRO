"""
Gerenciador centralizado de APIs gratuitas para forex e análise financeira
"""

import asyncio
import aiohttp
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
import time
import json
from dataclasses import dataclass
import hashlib

from config.settings import APIEndpoints, AppConfig

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Padronização de resposta das APIs"""
    success: bool
    data: Any
    error_message: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    rate_limit_remaining: Optional[int] = None

class RateLimiter:
    """Controle de rate limiting para APIs"""
    
    def __init__(self):
        self.request_history = {}
        
    def can_make_request(self, api_name: str, limit_per_minute: int = 60) -> bool:
        """Verifica se pode fazer requisição baseado no rate limit"""
        now = time.time()
        
        if api_name not in self.request_history:
            self.request_history[api_name] = []
            
        # Remove requisições antigas (mais de 1 minuto)
        self.request_history[api_name] = [
            req_time for req_time in self.request_history[api_name]
            if now - req_time < 60
        ]
        
        return len(self.request_history[api_name]) < limit_per_minute
    
    def record_request(self, api_name: str):
        """Registra uma requisição"""
        if api_name not in self.request_history:
            self.request_history[api_name] = []
        
        self.request_history[api_name].append(time.time())

class CacheManager:
    """Gerenciador de cache para otimizar requisições"""
    
    def __init__(self):
        self.cache = {}
        
    def _generate_key(self, url: str, params: Dict) -> str:
        """Gera chave única para cache"""
        key_string = f"{url}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url: str, params: Dict, ttl: int = 300) -> Optional[Any]:
        """Busca dados do cache"""
        key = self._generate_key(url, params)
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < ttl:
                return data
            else:
                del self.cache[key]
        
        return None
    
    def set(self, url: str, params: Dict, data: Any):
        """Armazena dados no cache"""
        key = self._generate_key(url, params)
        self.cache[key] = (data, time.time())

class ForexDataAPI:
    """Gerenciador de APIs de dados forex gratuitas"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.cache = CacheManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Smart-Money-Forex-Analyzer/2.0'
        })
    
    async def get_current_rates(self, base_currency: str = "USD") -> APIResponse:
        """Obtém taxas atuais de múltiplas APIs gratuitas"""
        
        # Tentar Frankfurter primeiro (sem API key)
        try:
            response = await self._get_frankfurter_rates(base_currency)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"Frankfurter API falhou: {e}")
        
        # Tentar ExchangeRate-API
        try:
            response = await self._get_exchangerate_api_rates(base_currency)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"ExchangeRate-API falhou: {e}")
        
        # Tentar FreeForexAPI
        try:
            response = await self._get_freeforex_rates(base_currency)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"FreeForexAPI falhou: {e}")
        
        # Se todas falharam, retornar dados demo
        return self._generate_demo_forex_data(base_currency)
    
    async def _get_freeforex_rates(self, base: str) -> APIResponse:
        """FreeForexAPI - Gratuita"""
        url = f"{APIEndpoints.FREEFOREXAPI}"
        params = {"pairs": f"{base}USD,{base}EUR,{base}GBP,{base}JPY"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Converter formato
                        rates = {}
                        for pair_data in data.get('rates', {}).values():
                            if 'rate' in pair_data:
                                pair = pair_data.get('pairs', '')
                                if pair:
                                    target_currency = pair.replace(base, '')
                                    rates[target_currency] = pair_data['rate']
                        
                        formatted_data = {
                            'base': base,
                            'rates': rates,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        return APIResponse(
                            success=True,
                            data=formatted_data,
                            source="FreeForexAPI",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro FreeForexAPI: {e}")
        
        return APIResponse(success=False, error_message="FreeForexAPI falhou")
    
    def _generate_demo_forex_data(self, base: str) -> APIResponse:
        """Gera dados demo quando APIs falham"""
        
        # Taxas base simuladas
        demo_rates = {
            'EUR': 0.85 + np.random.normal(0, 0.01),
            'GBP': 0.75 + np.random.normal(0, 0.01),
            'JPY': 150.0 + np.random.normal(0, 2.0),
            'AUD': 0.65 + np.random.normal(0, 0.01),
            'CAD': 1.35 + np.random.normal(0, 0.02),
            'CHF': 0.88 + np.random.normal(0, 0.01),
            'NZD': 0.60 + np.random.normal(0, 0.01)
        }
        
        # Ajustar se base não for USD
        if base != 'USD':
            if base in demo_rates:
                base_rate = demo_rates[base]
                demo_rates = {k: v/base_rate for k, v in demo_rates.items()}
                demo_rates['USD'] = 1.0/base_rate
                del demo_rates[base]
        
        formatted_data = {
            'base': base,
            'rates': demo_rates,
            'timestamp': datetime.now().isoformat(),
            'demo': True
        }
        
        return APIResponse(
            success=True,
            data=formatted_data,
            source="Demo Data",
            timestamp=datetime.now()
        )

class HistoricalDataAPI:
    """API para dados históricos forex"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    async def get_historical_data(self, pair: str, timeframe: str = "1h", 
                                 limit: int = 500) -> APIResponse:
        """Obtém dados históricos OHLC"""
        
        # Tentar Alpha Vantage (requer API key gratuita)
        try:
            response = await self._get_alpha_vantage_data(pair, timeframe, limit)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"Alpha Vantage falhou: {e}")
        
        # Fallback para dados demo
        return self._generate_demo_historical_data(pair, timeframe, limit)
    
    async def _get_alpha_vantage_data(self, pair: str, timeframe: str, 
                                    limit: int) -> APIResponse:
        """Alpha Vantage API - 5 req/min gratuitas"""
        
        # Converter par para formato Alpha Vantage
        from_symbol = pair[:3]
        to_symbol = pair[3:]
        
        url = APIEndpoints.ALPHA_VANTAGE
        params = {
            'function': 'FX_INTRADAY',
            'from_symbol': from_symbol,
            'to_symbol': to_symbol,
            'interval': self._convert_timeframe_av(timeframe),
            'apikey': 'demo'  # Usar 'demo' para teste
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Processar dados Alpha Vantage
                        time_series_key = f"Time Series ({params['interval']})"
                        if time_series_key in data:
                            ohlc_data = []
                            
                            for timestamp, values in list(data[time_series_key].items())[:limit]:
                                ohlc_data.append({
                                    'datetime': pd.to_datetime(timestamp),
                                    'open': float(values['1. open']),
                                    'high': float(values['2. high']),
                                    'low': float(values['3. low']),
                                    'close': float(values['4. close']),
                                    'volume': np.random.randint(1000, 10000)  # Volume simulado
                                })
                            
                            df = pd.DataFrame(ohlc_data)
                            df = df.sort_values('datetime').reset_index(drop=True)
                            
                            return APIResponse(
                                success=True,
                                data=df,
                                source="Alpha Vantage",
                                timestamp=datetime.now()
                            )
                    
        except Exception as e:
            logger.error(f"Erro Alpha Vantage: {e}")
        
        return APIResponse(success=False, error_message="Alpha Vantage falhou")
    
    def _convert_timeframe_av(self, timeframe: str) -> str:
        """Converte timeframe para formato Alpha Vantage"""
        mapping = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '60min'
        }
        return mapping.get(timeframe, '15min')
    
    def _generate_demo_historical_data(self, pair: str, timeframe: str, 
                                     limit: int) -> APIResponse:
        """Gera dados históricos demo"""
        
        # Preços base para pares principais
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
            'AUDUSD': 0.6550, 'USDCAD': 1.3650, 'USDCHF': 0.8750,
            'NZDUSD': 0.6150, 'EURGBP': 0.8580, 'EURJPY': 162.30,
            'GBPJPY': 189.20, 'XAUUSD': 2050.00, 'BTCUSD': 42000.00
        }
        
        base_price = base_prices.get(pair, 1.0000)
        
        # Calcular intervalo de tempo
        timeframe_map = {
            '1m': timedelta(minutes=1), '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15), '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1), '4h': timedelta(hours=4),
            '1d': timedelta(days=1)
        }
        
        time_delta = timeframe_map.get(timeframe, timedelta(minutes=15))
        end_time = datetime.now()
        
        # Gerar dados OHLC realistas
        data = []
        current_price = base_price
        
        for i in range(limit):
            timestamp = end_time - (time_delta * (limit - i - 1))
            
            # Simular volatilidade e tendência
            volatility = 0.001 if 'JPY' not in pair else 0.01
            trend = np.sin(i / 50) * 0.0005
            noise = np.random.normal(0, volatility)
            
            # Aplicar mudança de preço
            price_change = trend + noise
            current_price = current_price * (1 + price_change)
            
            # Gerar OHLC
            range_size = current_price * np.random.uniform(0.0005, 0.002)
            
            open_price = current_price + np.random.uniform(-range_size/3, range_size/3)
            close_price = current_price + np.random.uniform(-range_size/3, range_size/3)
            high_price = max(open_price, close_price) + np.random.uniform(0, range_size/2)
            low_price = min(open_price, close_price) - np.random.uniform(0, range_size/2)
            
            # Volume simulado
            volume = np.random.randint(1000, 15000)
            
            data.append({
                'datetime': timestamp,
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('datetime').reset_index(drop=True)
        
        return APIResponse(
            success=True,
            data=df,
            source="Demo Data",
            timestamp=datetime.now()
        )

class NewsAPI:
    """Gerenciador de APIs de notícias econômicas gratuitas"""
    
    def __init__(self):
        self.cache = CacheManager()
        
    async def get_economic_news(self, symbols: List[str] = None) -> APIResponse:
        """Obtém notícias econômicas de múltiplas fontes"""
        
        # Tentar NewsAPI
        try:
            response = await self._get_newsapi_data(symbols)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"NewsAPI falhou: {e}")
        
        # Tentar MarketAux
        try:
            response = await self._get_marketaux_data(symbols)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"MarketAux falhou: {e}")
        
        # Fallback para dados demo
        return self._generate_demo_news()
    
    async def _get_newsapi_data(self, symbols: List[str]) -> APIResponse:
        """NewsAPI - 100 requests/day gratuitas"""
        
        url = f"{APIEndpoints.NEWSAPI}/everything"
        params = {
            'q': 'forex OR currency OR "central bank" OR inflation OR GDP',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 20,
            'apiKey': 'demo'  # Substituir por API key real
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        news_events = []
                        for article in data.get('articles', []):
                            news_events.append({
                                'timestamp': pd.to_datetime(article.get('publishedAt')),
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'url': article.get('url', ''),
                                'importance': self._classify_news_importance(article.get('title', '')),
                                'currency': self._extract_currency_from_news(article.get('title', ''))
                            })
                        
                        return APIResponse(
                            success=True,
                            data=news_events,
                            source="NewsAPI",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro NewsAPI: {e}")
        
        return APIResponse(success=False, error_message="NewsAPI falhou")
    
    async def _get_marketaux_data(self, symbols: List[str]) -> APIResponse:
        """MarketAux - 100 requests/day gratuitas"""
        
        url = f"{APIEndpoints.MARKETAUX}/news"
        params = {
            'filter_entities': True,
            'language': 'en',
            'limit': 20,
            'api_token': 'demo'  # Substituir por API key real
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        news_events = []
                        for article in data.get('data', []):
                            news_events.append({
                                'timestamp': pd.to_datetime(article.get('published_at')),
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'source': article.get('source', ''),
                                'url': article.get('url', ''),
                                'importance': self._classify_news_importance(article.get('title', '')),
                                'currency': self._extract_currency_from_news(article.get('title', ''))
                            })
                        
                        return APIResponse(
                            success=True,
                            data=news_events,
                            source="MarketAux",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro MarketAux: {e}")
        
        return APIResponse(success=False, error_message="MarketAux falhou")
    
    def _classify_news_importance(self, title: str) -> str:
        """Classifica importância da notícia"""
        title_lower = title.lower()
        
        high_impact_keywords = [
            'fed', 'federal reserve', 'ecb', 'boe', 'boj', 'rba', 'boc',
            'interest rate', 'gdp', 'inflation', 'nfp', 'employment',
            'fomc', 'monetary policy', 'recession'
        ]
        
        medium_impact_keywords = [
            'trade', 'export', 'import', 'retail sales', 'consumer',
            'housing', 'manufacturing', 'pmi', 'cpi', 'ppi'
        ]
        
        for keyword in high_impact_keywords:
            if keyword in title_lower:
                return 'High'
        
        for keyword in medium_impact_keywords:
            if keyword in title_lower:
                return 'Medium'
        
        return 'Low'
    
    def _extract_currency_from_news(self, title: str) -> str:
        """Extrai moeda relevante da notícia"""
        title_lower = title.lower()
        
        currency_keywords = {
            'USD': ['dollar', 'fed', 'federal reserve', 'us ', 'usa', 'america'],
            'EUR': ['euro', 'ecb', 'europe', 'eurozone', 'eu '],
            'GBP': ['pound', 'sterling', 'boe', 'uk ', 'britain', 'england'],
            'JPY': ['yen', 'boj', 'japan', 'japanese'],
            'AUD': ['aussie', 'rba', 'australia', 'australian'],
            'CAD': ['cad', 'boc', 'canada', 'canadian'],
            'CHF': ['franc', 'snb', 'swiss', 'switzerland'],
            'NZD': ['kiwi', 'rbnz', 'zealand', 'new zealand']
        }
        
        for currency, keywords in currency_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return currency
        
        return 'USD'  # Default
    
    def _generate_demo_news(self) -> APIResponse:
        """Gera notícias demo"""
        
        now = datetime.now()
        demo_news = [
            {
                'timestamp': now + timedelta(hours=2),
                'title': 'Fed Chair Powell Speaks on Monetary Policy',
                'description': 'Federal Reserve Chairman discusses current economic outlook and interest rate policy.',
                'source': 'Reuters',
                'importance': 'High',
                'currency': 'USD'
            },
            {
                'timestamp': now + timedelta(hours=4),
                'title': 'ECB Releases Economic Bulletin',
                'description': 'European Central Bank publishes latest economic assessment for the Eurozone.',
                'source': 'Bloomberg',
                'importance': 'Medium',
                'currency': 'EUR'
            },
            {
                'timestamp': now + timedelta(days=1, hours=2),
                'title': 'UK GDP Data Shows Economic Growth',
                'description': 'British economy shows signs of recovery with positive GDP figures.',
                'source': 'Financial Times',
                'importance': 'High',
                'currency': 'GBP'
            },
            {
                'timestamp': now + timedelta(days=1, hours=6),
                'title': 'US Initial Jobless Claims Released',
                'description': 'Weekly unemployment claims data provides insight into labor market health.',
                'source': 'MarketWatch',
                'importance': 'Medium',
                'currency': 'USD'
            }
        ]
        
        return APIResponse(
            success=True,
            data=demo_news,
            source="Demo Data",
            timestamp=datetime.now()
        )

class CryptoAPI:
    """API para dados de criptomoedas (correlação)"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    async def get_crypto_data(self, symbols: List[str] = None) -> APIResponse:
        """Obtém dados de criptomoedas para análise de correlação"""
        
        if not symbols:
            symbols = ['bitcoin', 'ethereum', 'ripple']
        
        try:
            response = await self._get_coingecko_data(symbols)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"CoinGecko falhou: {e}")
        
        return self._generate_demo_crypto_data(symbols)
    
    async def _get_coingecko_data(self, symbols: List[str]) -> APIResponse:
        """CoinGecko API - Gratuita"""
        
        url = f"{APIEndpoints.COINGECKO}/simple/price"
        params = {
            'ids': ','.join(symbols),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        crypto_data = {}
                        for symbol, info in data.items():
                            crypto_data[symbol.upper()] = {
                                'price': info.get('usd', 0),
                                'change_24h': info.get('usd_24h_change', 0),
                                'market_cap': info.get('usd_market_cap', 0)
                            }
                        
                        return APIResponse(
                            success=True,
                            data=crypto_data,
                            source="CoinGecko",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro CoinGecko: {e}")
        
        return APIResponse(success=False, error_message="CoinGecko falhou")
    
    def _generate_demo_crypto_data(self, symbols: List[str]) -> APIResponse:
        """Gera dados crypto demo"""
        
        demo_prices = {
            'BITCOIN': 42000 + np.random.normal(0, 1000),
            'ETHEREUM': 2500 + np.random.normal(0, 100),
            'RIPPLE': 0.60 + np.random.normal(0, 0.05)
        }
        
        crypto_data = {}
        for symbol in symbols:
            key = symbol.upper()
            if key in demo_prices:
                crypto_data[key] = {
                    'price': demo_prices[key],
                    'change_24h': np.random.normal(0, 5),
                    'market_cap': demo_prices[key] * np.random.randint(18000000, 20000000)
                }
        
        return APIResponse(
            success=True,
            data=crypto_data,
            source="Demo Data",
            timestamp=datetime.now()
        )

class APIManager:
    """Gerenciador principal de todas as APIs"""
    
    def __init__(self):
        self.forex_api = ForexDataAPI()
        self.historical_api = HistoricalDataAPI()
        self.news_api = NewsAPI()
        self.crypto_api = CryptoAPI()
        self.rate_limiter = RateLimiter()
    
    async def get_market_overview(self, base_currency: str = "USD") -> Dict[str, APIResponse]:
        """Obtém overview completo do mercado"""
        
        tasks = {
            'forex': self.forex_api.get_current_rates(base_currency),
            'news': self.news_api.get_economic_news(),
            'crypto': self.crypto_api.get_crypto_data()
        }
        
        results = {}
        
        # Executar requests concorrentemente
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Erro em {name}: {e}")
                results[name] = APIResponse(
                    success=False, 
                    error_message=f"Erro em {name}: {str(e)}"
                )
        
        return results
    
    def get_api_status(self) -> Dict[str, bool]:
        """Verifica status de todas as APIs"""
        
        status = {}
        
        # Verificar rate limits
        for api_name, config in AppConfig.RATE_LIMITS.items():
            if 'requests_per_minute' in config:
                status[api_name] = self.rate_limiter.can_make_request(
                    api_name, 
                    config['requests_per_minute']
                )
            else:
                status[api_name] = True
        
        return status
    
    async def test_all_apis(self) -> Dict[str, bool]:
        """Testa conectividade de todas as APIs"""
        
        test_results = {}
        
        # Testar Forex APIs
        try:
            forex_response = await self.forex_api.get_current_rates("USD")
            test_results['forex'] = forex_response.success
        except Exception:
            test_results['forex'] = False
        
        # Testar News APIs
        try:
            news_response = await self.news_api.get_economic_news()
            test_results['news'] = news_response.success
        except Exception:
            test_results['news'] = False
        
        # Testar Crypto APIs
        try:
            crypto_response = await self.crypto_api.get_crypto_data()
            test_results['crypto'] = crypto_response.success
        except Exception:
            test_results['crypto'] = False
        
        return test_results_frankfurter_rates(self, base: str) -> APIResponse:
        """API Frankfurter - Gratuita sem API key"""
        url = f"{APIEndpoints.FRANKFURTER}/latest"
        params = {"from": base}
        
        # Verificar cache primeiro
        cached = self.cache.get(url, params, ttl=300)
        if cached:
            return APIResponse(
                success=True,
                data=cached,
                source="Frankfurter (cached)",
                timestamp=datetime.now()
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Converter para formato padronizado
                        formatted_data = {
                            'base': data.get('base', base),
                            'date': data.get('date'),
                            'rates': data.get('rates', {}),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.cache.set(url, params, formatted_data)
                        
                        return APIResponse(
                            success=True,
                            data=formatted_data,
                            source="Frankfurter",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro Frankfurter API: {e}")
        
        return APIResponse(success=False, error_message="Frankfurter API falhou")
    
    async def _get_exchangerate_api_rates(self, base: str) -> APIResponse:
        """ExchangeRate-API - Gratuita"""
        url = f"{APIEndpoints.EXCHANGERATE_API}/{base}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        formatted_data = {
                            'base': data.get('base', base),
                            'date': data.get('date'),
                            'rates': data.get('rates', {}),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        return APIResponse(
                            success=True,
                            data=formatted_data,
                            source="ExchangeRate-API",
                            timestamp=datetime.now()
                        )
                    
        except Exception as e:
            logger.error(f"Erro ExchangeRate-API: {e}")
        
        return APIResponse(success=False, error_message="ExchangeRate-API falhou")
    
    async def _get