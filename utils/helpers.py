"""
Funções utilitárias para o Smart Money Forex Analyzer Pro
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
import re
from dataclasses import dataclass
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

def format_currency_pair(pair: str, format_type: str = "display") -> str:
    """
    Formata par de moedas para diferentes contextos
    
    Args:
        pair: Par de moedas (ex: "EUR/USD")
        format_type: Tipo de formatação ("display", "api", "tradingview")
    
    Returns:
        Par formatado conforme o tipo
    """
    if format_type == "api":
        return pair.replace("/", "").upper()
    elif format_type == "tradingview":
        return f"FX:{pair.replace('/', '').upper()}"
    elif format_type == "display":
        return pair.upper()
    else:
        return pair

def calculate_pips(price1: float, price2: float, pair: str) -> float:
    """
    Calcula diferença em pips entre dois preços
    
    Args:
        price1: Primeiro preço
        price2: Segundo preço
        pair: Par de moedas
    
    Returns:
        Diferença em pips
    """
    # Pares com JPY têm valor de pip diferente
    if "JPY" in pair.upper():
        pip_value = 0.01
    else:
        pip_value = 0.0001
    
    return abs(price1 - price2) / pip_value

def format_number(number: Union[int, float], decimal_places: int = 2, 
                 use_thousands_separator: bool = True) -> str:
    """
    Formata número para exibição
    
    Args:
        number: Número para formatar
        decimal_places: Casas decimais
        use_thousands_separator: Usar separador de milhares
    
    Returns:
        Número formatado
    """
    if use_thousands_separator:
        return f"{number:,.{decimal_places}f}"
    else:
        return f"{number:.{decimal_places}f}"

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calcula Average True Range
    
    Args:
        df: DataFrame com dados OHLC
        period: Período para cálculo
    
    Returns:
        Série com valores ATR
    """
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift(1))
    low_close = abs(df['low'] - df['close'].shift(1))
    
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = true_range.rolling(window=period).mean()
    
    return atr

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """
    Calcula Relative Strength Index
    
    Args:
        df: DataFrame com dados de preço
        period: Período para cálculo
        column: Coluna para cálculo
    
    Returns:
        Série com valores RSI
    """
    delta = df[column].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, 
                            std_dev: float = 2.0, column: str = 'close') -> Dict[str, pd.Series]:
    """
    Calcula Bollinger Bands
    
    Args:
        df: DataFrame com dados de preço
        period: Período para média móvel
        std_dev: Multiplicador do desvio padrão
        column: Coluna para cálculo
    
    Returns:
        Dict com upper, middle, lower bands
    """
    sma = df[column].rolling(window=period).mean()
    std = df[column].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return {
        'upper': upper_band,
        'middle': sma,
        'lower': lower_band
    }

def identify_session(timestamp: datetime, pair: str) -> str:
    """
    Identifica sessão de mercado baseada no horário
    
    Args:
        timestamp: Timestamp para verificar
        pair: Par de moedas
    
    Returns:
        Nome da sessão (Asian, European, American)
    """
    hour = timestamp.hour
    
    # Horários aproximados em UTC
    if 22 <= hour or hour < 8:
        return "Asian"
    elif 8 <= hour < 16:
        return "European"
    else:
        return "American"

def get_session_overlap(timestamp: datetime) -> Optional[str]:
    """
    Identifica se horário está em overlap de sessões
    
    Args:
        timestamp: Timestamp para verificar
    
    Returns:
        Nome do overlap ou None
    """
    hour = timestamp.hour
    
    if 8 <= hour < 9:
        return "Tokyo-London"
    elif 13 <= hour < 16:
        return "London-New York"
    else:
        return None

def calculate_volatility(df: pd.DataFrame, period: int = 20, 
                        method: str = 'close') -> float:
    """
    Calcula volatilidade dos retornos
    
    Args:
        df: DataFrame com dados de preço
        period: Período para cálculo
        method: Método de cálculo ('close', 'hl', 'garman_klass')
    
    Returns:
        Volatilidade percentual
    """
    if method == 'close':
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(period) * 100
        
    elif method == 'hl':
        # High-Low volatility
        hl_ratio = np.log(df['high'] / df['low'])
        volatility = hl_ratio.rolling(window=period).std() * np.sqrt(period) * 100
        
    elif method == 'garman_klass':
        # Garman-Klass volatility estimator
        log_hl = (np.log(df['high']) - np.log(df['low'])) ** 2
        log_cc = (np.log(df['close']) - np.log(df['close'].shift(1))) ** 2
        
        rs = log_hl - (2 * np.log(2) - 1) * log_cc
        volatility = np.sqrt(rs.rolling(window=period).mean()) * np.sqrt(period) * 100
        
    else:
        raise ValueError("Método deve ser 'close', 'hl' ou 'garman_klass'")
    
    return volatility.iloc[-1] if not volatility.empty else 0.0

def find_support_resistance_levels(df: pd.DataFrame, method: str = 'pivot_points', 
                                  window: int = 5) -> Dict[str, List[float]]:
    """
    Identifica níveis de suporte e resistência
    
    Args:
        df: DataFrame com dados OHLC
        method: Método ('pivot_points', 'fractal', 'psychological')
        window: Janela para identificação
    
    Returns:
        Dict com listas de suporte e resistência
    """
    levels = {'support': [], 'resistance': []}
    
    if method == 'pivot_points':
        # Pivot Points clássicos
        for i in range(window, len(df) - window):
            high_window = df['high'].iloc[i-window:i+window+1]
            low_window = df['low'].iloc[i-window:i+window+1]
            
            # Resistência (pico)
            if df['high'].iloc[i] == high_window.max():
                levels['resistance'].append(df['high'].iloc[i])
            
            # Suporte (vale)
            if df['low'].iloc[i] == low_window.min():
                levels['support'].append(df['low'].iloc[i])
    
    elif method == 'psychological':
        # Níveis psicológicos (números redondos)
        current_price = df['close'].iloc[-1]
        
        # Determinar step baseado no par
        if any(curr in df.columns[0] if hasattr(df.columns, '__getitem__') else False 
               for curr in ['JPY']):
            step = 0.5  # Para pares JPY
        else:
            step = 0.005  # Para outros pares
        
        # Gerar níveis próximos ao preço atual
        base = round(current_price / step) * step
        
        for i in range(-10, 11):
            level = base + (i * step)
            if level > 0:
                if level > current_price:
                    levels['resistance'].append(level)
                else:
                    levels['support'].append(level)
    
    # Remover duplicatas e ordenar
    levels['support'] = sorted(list(set(levels['support'])))
    levels['resistance'] = sorted(list(set(levels['resistance'])))
    
    return levels

def calculate_fibonacci_levels(high_price: float, low_price: float, 
                             trend: str = 'uptrend') -> Dict[str, float]:
    """
    Calcula níveis de Fibonacci
    
    Args:
        high_price: Preço máximo do movimento
        low_price: Preço mínimo do movimento
        trend: Direção da tendência ('uptrend', 'downtrend')
    
    Returns:
        Dict com níveis de Fibonacci
    """
    diff = high_price - low_price
    
    fib_ratios = {
        '0.0': 0.0,
        '23.6': 0.236,
        '38.2': 0.382,
        '50.0': 0.5,
        '61.8': 0.618,
        '78.6': 0.786,
        '100.0': 1.0
    }
    
    levels = {}
    
    if trend == 'uptrend':
        # Retracement em uptrend
        for name, ratio in fib_ratios.items():
            levels[f'Fib_{name}'] = high_price - (diff * ratio)
    else:
        # Retracement em downtrend
        for name, ratio in fib_ratios.items():
            levels[f'Fib_{name}'] = low_price + (diff * ratio)
    
    return levels

def detect_chart_patterns(df: pd.DataFrame) -> List[Dict]:
    """
    Detecta padrões gráficos básicos
    
    Args:
        df: DataFrame com dados OHLC
    
    Returns:
        Lista de padrões detectados
    """
    patterns = []
    
    if len(df) < 20:
        return patterns
    
    # Double Top/Bottom
    patterns.extend(_detect_double_top_bottom(df))
    
    # Head and Shoulders
    patterns.extend(_detect_head_shoulders(df))
    
    # Triangles
    patterns.extend(_detect_triangles(df))
    
    return patterns

def _detect_double_top_bottom(df: pd.DataFrame) -> List[Dict]:
    """Detecta padrões Double Top/Bottom"""
    patterns = []
    window = 10
    
    # Encontrar picos e vales
    peaks = []
    valleys = []
    
    for i in range(window, len(df) - window):
        high_window = df['high'].iloc[i-window:i+window+1]
        low_window = df['low'].iloc[i-window:i+window+1]
        
        if df['high'].iloc[i] == high_window.max():
            peaks.append({'index': i, 'price': df['high'].iloc[i]})
        
        if df['low'].iloc[i] == low_window.min():
            valleys.append({'index': i, 'price': df['low'].iloc[i]})
    
    # Double Top
    for i in range(1, len(peaks)):
        peak1 = peaks[i-1]
        peak2 = peaks[i]
        
        price_diff = abs(peak1['price'] - peak2['price'])
        price_tolerance = peak1['price'] * 0.01  # 1% tolerance
        
        if price_diff < price_tolerance and peak2['index'] - peak1['index'] > 20:
            patterns.append({
                'type': 'Double Top',
                'direction': 'bearish',
                'start_index': peak1['index'],
                'end_index': peak2['index'],
                'level': (peak1['price'] + peak2['price']) / 2,
                'strength': 70
            })
    
    # Double Bottom
    for i in range(1, len(valleys)):
        valley1 = valleys[i-1]
        valley2 = valleys[i]
        
        price_diff = abs(valley1['price'] - valley2['price'])
        price_tolerance = valley1['price'] * 0.01
        
        if price_diff < price_tolerance and valley2['index'] - valley1['index'] > 20:
            patterns.append({
                'type': 'Double Bottom',
                'direction': 'bullish',
                'start_index': valley1['index'],
                'end_index': valley2['index'],
                'level': (valley1['price'] + valley2['price']) / 2,
                'strength': 70
            })
    
    return patterns

def _detect_head_shoulders(df: pd.DataFrame) -> List[Dict]:
    """Detecta padrões Head and Shoulders"""
    patterns = []
    # Implementação simplificada
    # TODO: Implementar detecção completa de H&S
    return patterns

def _detect_triangles(df: pd.DataFrame) -> List[Dict]:
    """Detecta padrões de triângulos"""
    patterns = []
    # Implementação simplificada
    # TODO: Implementar detecção de triângulos
    return patterns

def calculate_position_size(account_balance: float, risk_percentage: float,
                          entry_price: float, stop_loss: float, 
                          pair: str) -> Dict:
    """
    Calcula tamanho da posição baseado em gestão de risco
    
    Args:
        account_balance: Saldo da conta
        risk_percentage: Percentual de risco por trade (1-5%)
        entry_price: Preço de entrada
        stop_loss: Preço de stop loss
        pair: Par de moedas
    
    Returns:
        Dict com informações da posição
    """
    risk_amount = account_balance * (risk_percentage / 100)
    
    # Calcular risco em pips
    pip_risk = calculate_pips(entry_price, stop_loss, pair)
    
    if pip_risk == 0:
        return {
            'lots': 0,
            'units': 0,
            'risk_amount': risk_amount,
            'pip_risk': 0,
            'pip_value': 0,
            'error': 'Stop loss igual ao preço de entrada'
        }
    
    # Valor por pip (simplificado para conta USD)
    if pair.endswith('USD'):
        # Par direto (EUR/USD, GBP/USD, etc.)
        pip_value = 1.0
    elif pair.startswith('USD'):
        # Par indireto (USD/JPY, USD/CHF, etc.)
        pip_value = 1.0 / entry_price
    else:
        # Par cruzado - usar aproximação
        pip_value = 1.0
    
    # Calcular tamanho da posição
    # Fórmula: Lots = Risco em USD / (Risco em Pips × Valor por Pip × 10000)
    lots = risk_amount / (pip_risk * pip_value * 10000)
    
    # Arredondar para 2 casas decimais
    lots = round(lots, 2)
    
    # Calcular unidades (1 lote padrão = 100.000 unidades)
    units = int(lots * 100000)
    
    return {
        'lots': lots,
        'units': units,
        'risk_amount': risk_amount,
        'pip_risk': pip_risk,
        'pip_value': pip_value,
        'risk_per_pip': risk_amount / pip_risk if pip_risk > 0 else 0
    }

def calculate_risk_reward_ratio(entry_price: float, stop_loss: float,
                              take_profit: float, direction: str = 'long') -> float:
    """
    Calcula ratio Risco:Recompensa
    
    Args:
        entry_price: Preço de entrada
        stop_loss: Preço de stop loss
        take_profit: Preço de take profit
        direction: Direção da trade ('long', 'short')
    
    Returns:
        Ratio R:R (recompensa/risco)
    """
    if direction.lower() == 'long':
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
    else:  # short
        risk = abs(stop_loss - entry_price)
        reward = abs(entry_price - take_profit)
    
    if risk == 0:
        return float('inf')
    
    return reward / risk

def validate_market_hours(timestamp: datetime, pair: str) -> bool:
    """
    Valida se timestamp está em horário de mercado ativo
    
    Args:
        timestamp: Timestamp para validar
        pair: Par de moedas
    
    Returns:
        True se mercado está ativo
    """
    weekday = timestamp.weekday()
    hour = timestamp.hour
    
    # Forex é 24h durante a semana
    # Segunda a Quinta: sempre ativo
    if 0 <= weekday <= 3:
        return True
    
    # Sexta: ativo até 22:00 UTC (fechamento NY)
    elif weekday == 4:
        return hour < 22
    
    # Domingo: ativo após 22:00 UTC (abertura Sydney)
    elif weekday == 6:
        return hour >= 22
    
    # Sábado: geralmente inativo
    else:
        return False

def get_economic_calendar_impact(event_title: str, currency: str) -> str:
    """
    Determina impacto de evento econômico
    
    Args:
        event_title: Título do evento
        currency: Moeda afetada
    
    Returns:
        Nível de impacto ('High', 'Medium', 'Low')
    """
    title_lower = event_title.lower()
    
    # Eventos de alto impacto
    high_impact_keywords = [
        'interest rate', 'fomc', 'ecb', 'boe', 'boj', 'rba', 'boc',
        'nfp', 'non-farm payroll', 'employment change', 'unemployment rate',
        'gdp', 'inflation', 'cpi', 'core cpi', 'pce', 'retail sales',
        'trade balance', 'current account', 'monetary policy',
        'press conference', 'speech', 'testimony'
    ]
    
    # Eventos de médio impacto
    medium_impact_keywords = [
        'ppi', 'producer price', 'industrial production', 'manufacturing',
        'pmi', 'ism', 'consumer confidence', 'sentiment', 'housing',
        'building permits', 'existing home sales', 'new home sales',
        'durable goods', 'factory orders', 'business confidence'
    ]
    
    # Verificar alto impacto
    for keyword in high_impact_keywords:
        if keyword in title_lower:
            return 'High'
    
    # Verificar médio impacto
    for keyword in medium_impact_keywords:
        if keyword in title_lower:
            return 'Medium'
    
    return 'Low'

def format_signal_message(signal, pair: str, include_emoji: bool = True) -> str:
    """
    Formata mensagem de sinal para exibição
    
    Args:
        signal: Objeto de sinal
        pair: Par de moedas
        include_emoji: Incluir emojis na mensagem
    
    Returns:
        Mensagem formatada
    """
    if include_emoji:
        direction_emoji = "🟢" if signal.direction == 'bullish' else "🔴"
        strength_stars = "⭐" * min(5, int(signal.strength / 20))
        
        message = f"""
{direction_emoji} **{signal.signal_type.replace('_', ' ')}** - {pair}
📍 Preço: {signal.price:.5f}
💪 Força: {signal.strength:.1f}% {strength_stars}
⏰ Tempo: {signal.timestamp.strftime('%Y-%m-%d %H:%M')}
📝 {signal.description}
"""
    else:
        message = f"""
{signal.signal_type.replace('_', ' ')} - {pair}
Preço: {signal.price:.5f}
Força: {signal.strength:.1f}%
Tempo: {signal.timestamp.strftime('%Y-%m-%d %H:%M')}
Descrição: {signal.description}
"""
    
    return message.strip()

def calculate_currency_strength(pairs_data: Dict[str, pd.DataFrame], 
                              period: int = 20) -> Dict[str, float]:
    """
    Calcula força relativa das moedas
    
    Args:
        pairs_data: Dict com dados de múltiplos pares
        period: Período para cálculo
    
    Returns:
        Dict com força de cada moeda (-100 a +100)
    """
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
    strength = {curr: 0.0 for curr in currencies}
    pair_count = {curr: 0 for curr in currencies}
    
    for pair, df in pairs_data.items():
        if df.empty or len(df) < period:
            continue
        
        # Extrair moedas do par
        base_curr = pair[:3].upper()
        quote_curr = pair[3:].upper() if len(pair) == 6 else pair[4:7].upper()
        
        if base_curr not in currencies or quote_curr not in currencies:
            continue
        
        # Calcular mudança percentual no período
        if len(df) >= period:
            start_price = df['close'].iloc[-period]
            end_price = df['close'].iloc[-1]
            price_change = (end_price - start_price) / start_price
            
            # Adicionar à força das moedas
            strength[base_curr] += price_change
            strength[quote_curr] -= price_change
            
            pair_count[base_curr] += 1
            pair_count[quote_curr] += 1
    
    # Calcular média e normalizar
    for currency in currencies:
        if pair_count[currency] > 0:
            strength[currency] = strength[currency] / pair_count[currency]
    
    # Normalizar para escala -100 a +100
    if strength:
        max_abs_strength = max(abs(v) for v in strength.values())
        if max_abs_strength > 0:
            strength = {k: (v / max_abs_strength) * 100 for k, v in strength.items()}
    
    return strength

def detect_divergence(price_data: pd.Series, indicator_data: pd.Series,
                     lookback: int = 20) -> List[Dict]:
    """
    Detecta divergências entre preço e indicador
    
    Args:
        price_data: Série de preços
        indicator_data: Série do indicador
        lookback: Período de análise
    
    Returns:
        Lista de divergências encontradas
    """
    divergences = []
    
    if len(price_data) < lookback or len(indicator_data) < lookback:
        return divergences
    
    # Encontrar picos e vales
    price_peaks = _find_peaks(price_data, lookback // 4)
    price_valleys = _find_valleys(price_data, lookback // 4)
    
    indicator_peaks = _find_peaks(indicator_data, lookback // 4)
    indicator_valleys = _find_valleys(indicator_data, lookback // 4)
    
    # Divergência bearish (preço faz topo mais alto, indicador faz topo mais baixo)
    for i in range(1, len(price_peaks)):
        price_peak1 = price_peaks[i-1]
        price_peak2 = price_peaks[i]
        
        # Encontrar pico correspondente no indicador
        for ind_peak in indicator_peaks:
            if abs(ind_peak['index'] - price_peak2['index']) <= 5:
                if (price_peak2['value'] > price_peak1['value'] and
                    ind_peak['value'] < price_peak1['value']):
                    
                    divergences.append({
                        'type': 'bearish_divergence',
                        'price_peak1': price_peak1,
                        'price_peak2': price_peak2,
                        'indicator_peak': ind_peak,
                        'strength': _calculate_divergence_strength(price_peak1, price_peak2, ind_peak)
                    })
                break
    
    # Divergência bullish (preço faz fundo mais baixo, indicador faz fundo mais alto)
    for i in range(1, len(price_valleys)):
        price_valley1 = price_valleys[i-1]
        price_valley2 = price_valleys[i]
        
        # Encontrar vale correspondente no indicador
        for ind_valley in indicator_valleys:
            if abs(ind_valley['index'] - price_valley2['index']) <= 5:
                if (price_valley2['value'] < price_valley1['value'] and
                    ind_valley['value'] > price_valley1['value']):
                    
                    divergences.append({
                        'type': 'bullish_divergence',
                        'price_valley1': price_valley1,
                        'price_valley2': price_valley2,
                        'indicator_valley': ind_valley,
                        'strength': _calculate_divergence_strength(price_valley1, price_valley2, ind_valley)
                    })
                break
    
    return divergences

def _find_peaks(data: pd.Series, window: int = 5) -> List[Dict]:
    """Encontra picos na série de dados"""
    peaks = []
    
    for i in range(window, len(data) - window):
        if data.iloc[i] == data.iloc[i-window:i+window+1].max():
            peaks.append({
                'index': i,
                'value': data.iloc[i],
                'timestamp': data.index[i] if hasattr(data.index, 'to_pydatetime') else i
            })
    
    return peaks

def _find_valleys(data: pd.Series, window: int = 5) -> List[Dict]:
    """Encontra vales na série de dados"""
    valleys = []
    
    for i in range(window, len(data) - window):
        if data.iloc[i] == data.iloc[i-window:i+window+1].min():
            valleys.append({
                'index': i,
                'value': data.iloc[i],
                'timestamp': data.index[i] if hasattr(data.index, 'to_pydatetime') else i
            })
    
    return valleys

def _calculate_divergence_strength(point1: Dict, point2: Dict, indicator_point: Dict) -> float:
    """Calcula força da divergência (0-100)"""
    price_change = abs(point2['value'] - point1['value']) / point1['value']
    indicator_change = abs(indicator_point['value'] - point1['value']) / abs(point1['value'])
    
    # Quanto maior a diferença nos movimentos, maior a força
    strength = min(100, (price_change + indicator_change) * 1000)
    
    return strength

def generate_trade_plan(signals: List, current_price: float, atr: float,
                       risk_reward_ratio: float = 2.0) -> Optional[Dict]:
    """
    Gera plano de trade baseado nos sinais
    
    Args:
        signals: Lista de sinais
        current_price: Preço atual
        atr: Average True Range
        risk_reward_ratio: Ratio R:R desejado
    
    Returns:
        Plano de trade ou None
    """
    if not signals:
        return None
    
    # Filtrar sinais válidos e ordenar por força
    valid_signals = [s for s in signals if hasattr(s, 'strength') and s.strength > 50]
    valid_signals.sort(key=lambda x: x.strength, reverse=True)
    
    if not valid_signals:
        return None
    
    best_signal = valid_signals[0]
    
    # Determinar direção e preços
    if best_signal.direction == 'bullish':
        entry_price = best_signal.price
        stop_loss = entry_price - (atr * 1.5)
        take_profit = entry_price + ((entry_price - stop_loss) * risk_reward_ratio)
        direction = 'LONG'
    else:
        entry_price = best_signal.price
        stop_loss = entry_price + (atr * 1.5)
        take_profit = entry_price - ((stop_loss - entry_price) * risk_reward_ratio)
        direction = 'SHORT'
    
    # Calcular métricas
    risk_pips = abs(entry_price - stop_loss) / (0.01 if 'JPY' in str(best_signal) else 0.0001)
    reward_pips = abs(take_profit - entry_price) / (0.01 if 'JPY' in str(best_signal) else 0.0001)
    actual_rr = reward_pips / risk_pips if risk_pips > 0 else 0
    
    return {
        'signal': best_signal,
        'direction': direction,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk_pips': risk_pips,
        'reward_pips': reward_pips,
        'risk_reward_ratio': actual_rr,
        'confidence': best_signal.strength,
        'setup_quality': _assess_setup_quality(valid_signals, current_price),
        'notes': f"Trade baseado em {best_signal.signal_type} com força {best_signal.strength:.1f}%"
    }

def _assess_setup_quality(signals: List, current_price: float) -> str:
    """Avalia qualidade do setup baseado nos sinais"""
    
    if len(signals) >= 3:
        avg_strength = sum(s.strength for s in signals[:3]) / 3
        if avg_strength > 75:
            return "Excelente"
        elif avg_strength > 60:
            return "Boa"
        else:
            return "Regular"
    elif len(signals) == 2:
        avg_strength = sum(s.strength for s in signals) / 2
        if avg_strength > 70:
            return "Boa"
        else:
            return "Regular"
    else:
        if signals[0].strength > 80:
            return "Boa"
        else:
            return "Regular"

async def fetch_with_retry(session: aiohttp.ClientSession, url: str, 
                          max_retries: int = 3, **kwargs) -> Optional[Dict]:
    """
    Faz requisição HTTP com retry automático
    
    Args:
        session: Sessão aiohttp
        url: URL para requisição
        max_retries: Número máximo de tentativas
        **kwargs: Parâmetros adicionais
    
    Returns:
        Resposta JSON ou None
    """
    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=15, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"HTTP {response.status} para {url}")
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout na tentativa {attempt + 1} para {url}")
            
        except Exception as e:
            logger.error(f"Erro na tentativa {attempt + 1} para {url}: {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(1)  # Pausa entre tentativas
    
    return None

def clean_and_validate_ohlc_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e valida dados OHLC
    
    Args:
        df: DataFrame com dados OHLC
    
    Returns:
        DataFrame limpo e validado
    """
    if df.empty:
        return df
    
    required_columns = ['datetime', 'open', 'high', 'low', 'close']
    
    # Verificar colunas obrigatórias
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Colunas faltando: {missing_columns}")
        return pd.DataFrame()
    
    # Converter tipos
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    # Remover linhas com dados inválidos
    df = df.dropna(subset=required_columns)
    
    # Validar lógica OHLC
    invalid_rows = (
        (df['high'] < df['low']) |
        (df['high'] < df['open']) |
        (df['high'] < df['close']) |
        (df['low'] > df['open']) |
        (df['low'] > df['close'])
    )
    
    if invalid_rows.any():
        logger.warning(f"Removendo {invalid_rows.sum()} linhas com dados OHLC inválidos")
        df = df[~invalid_rows]
    
    # Ordenar por timestamp
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Adicionar volume se não existir
    if 'volume' not in df.columns:
        df['volume'] = np.random.randint(1000, 10000, len(df))
    
    return df

def format_timeframe_display(timeframe: str) -> str:
    """
    Formata timeframe para exibição amigável
    
    Args:
        timeframe: Timeframe (ex: "1m", "15m", "1h", "1d")
    
    Returns:
        Timeframe formatado
    """
    timeframe_map = {
        '1m': '1 Minuto',
        '5m': '5 Minutos',
        '15m': '15 Minutos',
        '30m': '30 Minutos',
        '1h': '1 Hora',
        '4h': '4 Horas',
        '1d': '1 Dia',
        '1w': '1 Semana',
        '1M': '1 Mês'
    }
    
    return timeframe_map.get(timeframe, timeframe)

def get_market_status(timestamp: datetime = None) -> Dict[str, str]:
    """
    Obtém status atual do mercado forex
    
    Args:
        timestamp: Timestamp para verificar (default: agora)
    
    Returns:
        Dict com informações do mercado
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    session = identify_session(timestamp, "EURUSD")
    overlap = get_session_overlap(timestamp)
    is_active = validate_market_hours(timestamp, "EURUSD")
    
    status = {
        'session': session,
        'overlap': overlap or "Nenhum",
        'is_active': "Ativo" if is_active else "Fechado",
        'next_session': _get_next_session(timestamp)
    }
    
    return status

def _get_next_session(timestamp: datetime) -> str:
    """Determina a próxima sessão de mercado"""
    hour = timestamp.hour
    
    if hour < 8:
        return "European (08:00 UTC)"
    elif hour < 13:
        return "American (13:00 UTC)"
    elif hour < 22:
        return "Asian (22:00 UTC)"
    else:
        return "European (08:00 UTC - próximo dia)"