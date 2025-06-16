"""
Análise Smart Money Concepts - Identificação de padrões institucionais
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SmartMoneySignal:
    """Estrutura padronizada para sinais Smart Money"""
    signal_type: str
    direction: str  # bullish/bearish
    price: float
    timestamp: datetime
    strength: float  # 0-100
    timeframe: str
    description: str
    additional_data: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Converte sinal para dicionário"""
        return {
            'type': self.signal_type,
            'direction': self.direction,
            'price': self.price,
            'timestamp': self.timestamp,
            'strength': self.strength,
            'timeframe': self.timeframe,
            'description': self.description,
            'additional_data': self.additional_data or {}
        }

class FairValueGapAnalyzer:
    """Analisador de Fair Value Gaps (FVGs)"""
    
    def __init__(self, min_gap_pips: float = 3.0, max_age_hours: int = 24):
        self.min_gap_pips = min_gap_pips
        self.max_age_hours = max_age_hours
    
    def identify_fvgs(self, df: pd.DataFrame, pair: str) -> List[SmartMoneySignal]:
        """Identifica Fair Value Gaps no dataset"""
        
        signals = []
        
        if len(df) < 3:
            return signals
        
        # Determinar valor do pip
        pip_value = 0.01 if 'JPY' in pair else 0.0001
        
        for i in range(2, len(df)):
            try:
                candle_1 = df.iloc[i-2]  # Candle mais antiga
                candle_2 = df.iloc[i-1]  # Candle do meio (impulso)
                candle_3 = df.iloc[i]    # Candle mais recente
                
                # FVG Bullish: Low da candle 1 > High da candle 3
                if candle_1['low'] > candle_3['high']:
                    gap_size = candle_1['low'] - candle_3['high']
                    gap_pips = gap_size / pip_value
                    
                    # Verificar se gap é significativo
                    if gap_pips >= self.min_gap_pips:
                        # Verificar se candle do meio é impulso bullish
                        if self._is_bullish_impulse(candle_2):
                            strength = self._calculate_fvg_strength(
                                gap_pips, candle_2, df.iloc[max(0, i-10):i+1]
                            )
                            
                            signal = SmartMoneySignal(
                                signal_type="FVG_Bullish",
                                direction="bullish",
                                price=(candle_1['low'] + candle_3['high']) / 2,
                                timestamp=candle_3['datetime'],
                                strength=strength,
                                timeframe="current",
                                description=f"FVG Bullish - Gap: {gap_pips:.1f} pips",
                                additional_data={
                                    'gap_high': candle_1['low'],
                                    'gap_low': candle_3['high'],
                                    'gap_size_pips': gap_pips,
                                    'impulse_candle': {
                                        'open': candle_2['open'],
                                        'close': candle_2['close'],
                                        'high': candle_2['high'],
                                        'low': candle_2['low']
                                    }
                                }
                            )
                            signals.append(signal)
                
                # FVG Bearish: High da candle 1 < Low da candle 3
                elif candle_1['high'] < candle_3['low']:
                    gap_size = candle_3['low'] - candle_1['high']
                    gap_pips = gap_size / pip_value
                    
                    # Verificar se gap é significativo
                    if gap_pips >= self.min_gap_pips:
                        # Verificar se candle do meio é impulso bearish
                        if self._is_bearish_impulse(candle_2):
                            strength = self._calculate_fvg_strength(
                                gap_pips, candle_2, df.iloc[max(0, i-10):i+1]
                            )
                            
                            signal = SmartMoneySignal(
                                signal_type="FVG_Bearish",
                                direction="bearish",
                                price=(candle_3['low'] + candle_1['high']) / 2,
                                timestamp=candle_3['datetime'],
                                strength=strength,
                                timeframe="current",
                                description=f"FVG Bearish - Gap: {gap_pips:.1f} pips",
                                additional_data={
                                    'gap_high': candle_3['low'],
                                    'gap_low': candle_1['high'],
                                    'gap_size_pips': gap_pips,
                                    'impulse_candle': {
                                        'open': candle_2['open'],
                                        'close': candle_2['close'],
                                        'high': candle_2['high'],
                                        'low': candle_2['low']
                                    }
                                }
                            )
                            signals.append(signal)
                            
            except Exception as e:
                logger.warning(f"Erro ao processar FVG no índice {i}: {e}")
                continue
        
        # Filtrar FVGs por idade
        current_time = df['datetime'].iloc[-1]
        active_signals = []
        
        for signal in signals:
            age_hours = (current_time - signal.timestamp).total_seconds() / 3600
            if age_hours <= self.max_age_hours:
                active_signals.append(signal)
        
        return active_signals
    
    def _is_bullish_impulse(self, candle: pd.Series) -> bool:
        """Verifica se candle é impulso bullish válido"""
        body_size = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        # Candle deve ser verde e ter corpo significativo
        is_green = candle['close'] > candle['open']
        has_significant_body = body_size > total_range * 0.6 if total_range > 0 else False
        
        return is_green and has_significant_body
    
    def _is_bearish_impulse(self, candle: pd.Series) -> bool:
        """Verifica se candle é impulso bearish válido"""
        body_size = abs(candle['open'] - candle['close'])
        total_range = candle['high'] - candle['low']
        
        # Candle deve ser vermelha e ter corpo significativo
        is_red = candle['close'] < candle['open']
        has_significant_body = body_size > total_range * 0.6 if total_range > 0 else False
        
        return is_red and has_significant_body
    
    def _calculate_fvg_strength(self, gap_pips: float, impulse_candle: pd.Series, 
                              context_data: pd.DataFrame) -> float:
        """Calcula força do FVG baseado em múltiplos fatores"""
        
        strength = 0.0
        
        # Fator 1: Tamanho do gap (25 pontos máximo)
        gap_strength = min(25, gap_pips * 2)
        strength += gap_strength
        
        # Fator 2: Força do impulso (25 pontos máximo)
        body_size = abs(impulse_candle['close'] - impulse_candle['open'])
        total_range = impulse_candle['high'] - impulse_candle['low']
        
        if total_range > 0:
            body_ratio = body_size / total_range
            impulse_strength = body_ratio * 25
            strength += impulse_strength
        
        # Fator 3: Volume relativo (25 pontos máximo)
        if 'volume' in impulse_candle and len(context_data) > 5:
            avg_volume = context_data['volume'].mean()
            if avg_volume > 0:
                volume_ratio = impulse_candle['volume'] / avg_volume
                volume_strength = min(25, volume_ratio * 10)
                strength += volume_strength
        else:
            strength += 15  # Valor médio se não tiver volume
        
        # Fator 4: Contexto de mercado (25 pontos máximo)
        if len(context_data) >= 10:
            # Verificar se está em tendência
            recent_closes = context_data['close'].tail(10)
            trend_strength = self._calculate_trend_strength(recent_closes)
            strength += trend_strength * 25
        else:
            strength += 12.5  # Valor médio
        
        return min(100, max(0, strength))
    
    def _calculate_trend_strength(self, closes: pd.Series) -> float:
        """Calcula força da tendência (0-1)"""
        if len(closes) < 2:
            return 0.5
        
        # Calcular slope da regressão linear
        x = np.arange(len(closes))
        coeffs = np.polyfit(x, closes, 1)
        slope = coeffs[0]
        
        # Normalizar slope baseado na volatilidade
        price_std = closes.std()
        if price_std > 0:
            normalized_slope = abs(slope) / price_std
            return min(1.0, normalized_slope / 2)
        
        return 0.5

class OrderBlockAnalyzer:
    """Analisador de Order Blocks (OBs)"""
    
    def __init__(self, min_size_pips: float = 5.0, confirmation_candles: int = 2):
        self.min_size_pips = min_size_pips
        self.confirmation_candles = confirmation_candles
    
    def identify_order_blocks(self, df: pd.DataFrame, pair: str) -> List[SmartMoneySignal]:
        """Identifica Order Blocks no dataset"""
        
        signals = []
        
        if len(df) < 10:
            return signals
        
        pip_value = 0.01 if 'JPY' in pair else 0.0001
        window = 5  # Janela para verificar quebra de estrutura
        
        for i in range(window, len(df) - self.confirmation_candles):
            try:
                current_candle = df.iloc[i]
                
                # Verificar se houve movimento significativo após esta vela
                future_candles = df.iloc[i+1:i+1+self.confirmation_candles]
                
                # Order Block Bullish
                if self._is_potential_bullish_ob(current_candle, future_candles, pip_value):
                    strength = self._calculate_ob_strength(
                        current_candle, future_candles, df.iloc[max(0, i-10):i+10], 'bullish'
                    )
                    
                    signal = SmartMoneySignal(
                        signal_type="OB_Bullish",
                        direction="bullish",
                        price=current_candle['low'],
                        timestamp=current_candle['datetime'],
                        strength=strength,
                        timeframe="current",
                        description=f"Order Block Bullish - Zona: {current_candle['low']:.5f}",
                        additional_data={
                            'ob_high': current_candle['high'],
                            'ob_low': current_candle['low'],
                            'ob_open': current_candle['open'],
                            'ob_close': current_candle['close'],
                            'confirmation_move': self._calculate_confirmation_move(future_candles, 'bullish'),
                            'zone_type': 'demand'
                        }
                    )
                    signals.append(signal)
                
                # Order Block Bearish
                elif self._is_potential_bearish_ob(current_candle, future_candles, pip_value):
                    strength = self._calculate_ob_strength(
                        current_candle, future_candles, df.iloc[max(0, i-10):i+10], 'bearish'
                    )
                    
                    signal = SmartMoneySignal(
                        signal_type="OB_Bearish",
                        direction="bearish",
                        price=current_candle['high'],
                        timestamp=current_candle['datetime'],
                        strength=strength,
                        timeframe="current",
                        description=f"Order Block Bearish - Zona: {current_candle['high']:.5f}",
                        additional_data={
                            'ob_high': current_candle['high'],
                            'ob_low': current_candle['low'],
                            'ob_open': current_candle['open'],
                            'ob_close': current_candle['close'],
                            'confirmation_move': self._calculate_confirmation_move(future_candles, 'bearish'),
                            'zone_type': 'supply'
                        }
                    )
                    signals.append(signal)
                    
            except Exception as e:
                logger.warning(f"Erro ao processar OB no índice {i}: {e}")
                continue
        
        return signals
    
    def _is_potential_bullish_ob(self, candle: pd.Series, future_candles: pd.DataFrame, 
                               pip_value: float) -> bool:
        """Verifica se vela pode ser Order Block bullish"""
        
        # Candle deve ser bearish (institucional antes do movimento)
        is_bearish = candle['close'] < candle['open']
        
        # Deve haver movimento bullish significativo após
        if len(future_candles) == 0:
            return False
        
        highest_after = future_candles['high'].max()
        move_pips = (highest_after - candle['high']) / pip_value
        
        return is_bearish and move_pips >= self.min_size_pips
    
    def _is_potential_bearish_ob(self, candle: pd.Series, future_candles: pd.DataFrame,
                               pip_value: float) -> bool:
        """Verifica se vela pode ser Order Block bearish"""
        
        # Candle deve ser bullish (institucional antes do movimento)
        is_bullish = candle['close'] > candle['open']
        
        # Deve haver movimento bearish significativo após
        if len(future_candles) == 0:
            return False
        
        lowest_after = future_candles['low'].min()
        move_pips = (candle['low'] - lowest_after) / pip_value
        
        return is_bullish and move_pips >= self.min_size_pips
    
    def _calculate_confirmation_move(self, future_candles: pd.DataFrame, direction: str) -> float:
        """Calcula o movimento de confirmação em pips"""
        if len(future_candles) == 0:
            return 0.0
        
        if direction == 'bullish':
            start_price = future_candles['close'].iloc[0]
            max_price = future_candles['high'].max()
            return max_price - start_price
        else:
            start_price = future_candles['close'].iloc[0]
            min_price = future_candles['low'].min()
            return start_price - min_price
    
    def _calculate_ob_strength(self, ob_candle: pd.Series, future_candles: pd.DataFrame,
                             context: pd.DataFrame, direction: str) -> float:
        """Calcula força do Order Block"""
        
        strength = 0.0
        
        # Fator 1: Tamanho do movimento de confirmação (30 pontos)
        confirmation_move = self._calculate_confirmation_move(future_candles, direction)
        if confirmation_move > 0:
            move_strength = min(30, confirmation_move * 10000)  # Assumindo 4 casas decimais
            strength += move_strength
        
        # Fator 2: Velocidade do movimento (25 pontos)
        if len(future_candles) > 0:
            speed = confirmation_move / len(future_candles)
            speed_strength = min(25, speed * 50000)
            strength += speed_strength
        
        # Fator 3: Volume da vela OB (25 pontos)
        if 'volume' in ob_candle and len(context) > 5:
            avg_volume = context['volume'].mean()
            if avg_volume > 0:
                volume_ratio = ob_candle['volume'] / avg_volume
                volume_strength = min(25, volume_ratio * 10)
                strength += volume_strength
        else:
            strength += 15
        
        # Fator 4: Qualidade da vela OB (20 pontos)
        body_size = abs(ob_candle['close'] - ob_candle['open'])
        total_range = ob_candle['high'] - ob_candle['low']
        
        if total_range > 0:
            body_ratio = body_size / total_range
            quality_strength = body_ratio * 20
            strength += quality_strength
        else:
            strength += 10
        
        return min(100, max(0, strength))

class MarketStructureAnalyzer:
    """Analisador de Market Structure Shifts (MSS) e Change of Character (ChoCh)"""
    
    def __init__(self, lookback_period: int = 20, min_break_pips: float = 2.0):
        self.lookback_period = lookback_period
        self.min_break_pips = min_break_pips
    
    def identify_structure_shifts(self, df: pd.DataFrame, pair: str) -> List[SmartMoneySignal]:
        """Identifica mudanças na estrutura de mercado"""
        
        signals = []
        
        if len(df) < self.lookback_period * 2:
            return signals
        
        # Identificar swing points
        swing_points = self._identify_swing_points(df)
        
        if len(swing_points) < 4:
            return signals
        
        pip_value = 0.01 if 'JPY' in pair else 0.0001
        
        # Analisar para MSS e ChoCh
        for i in range(2, len(swing_points)):
            try:
                current_swing = swing_points[i]
                previous_swing = swing_points[i-1]
                prev_prev_swing = swing_points[i-2]
                
                # MSS Bullish: Novo Higher High
                if (current_swing['type'] == 'high' and 
                    prev_prev_swing['type'] == 'high' and
                    current_swing['price'] > prev_prev_swing['price']):
                    
                    break_size = (current_swing['price'] - prev_prev_swing['price']) / pip_value
                    
                    if break_size >= self.min_break_pips:
                        strength = self._calculate_structure_strength(
                            swing_points[max(0, i-3):i+1], 'bullish_mss'
                        )
                        
                        signal = SmartMoneySignal(
                            signal_type="MSS_Bullish",
                            direction="bullish",
                            price=current_swing['price'],
                            timestamp=current_swing['timestamp'],
                            strength=strength,
                            timeframe="current",
                            description=f"Market Structure Shift Bullish - Break: {break_size:.1f} pips",
                            additional_data={
                                'previous_high': prev_prev_swing['price'],
                                'new_high': current_swing['price'],
                                'break_size_pips': break_size,
                                'structure_type': 'higher_high'
                            }
                        )
                        signals.append(signal)
                
                # MSS Bearish: Novo Lower Low
                elif (current_swing['type'] == 'low' and 
                      prev_prev_swing['type'] == 'low' and
                      current_swing['price'] < prev_prev_swing['price']):
                    
                    break_size = (prev_prev_swing['price'] - current_swing['price']) / pip_value
                    
                    if break_size >= self.min_break_pips:
                        strength = self._calculate_structure_strength(
                            swing_points[max(0, i-3):i+1], 'bearish_mss'
                        )
                        
                        signal = SmartMoneySignal(
                            signal_type="MSS_Bearish",
                            direction="bearish",
                            price=current_swing['price'],
                            timestamp=current_swing['timestamp'],
                            strength=strength,
                            timeframe="current",
                            description=f"Market Structure Shift Bearish - Break: {break_size:.1f} pips",
                            additional_data={
                                'previous_low': prev_prev_swing['price'],
                                'new_low': current_swing['price'],
                                'break_size_pips': break_size,
                                'structure_type': 'lower_low'
                            }
                        )
                        signals.append(signal)
                
                # ChoCh: Mudança de caráter
                choch_signal = self._identify_change_of_character(
                    swing_points[max(0, i-4):i+1], pip_value
                )
                
                if choch_signal:
                    signals.append(choch_signal)
                    
            except Exception as e:
                logger.warning(f"Erro ao processar estrutura no swing {i}: {e}")
                continue
        
        return signals
    
    def _identify_swing_points(self, df: pd.DataFrame, window: int = 5) -> List[Dict]:
        """Identifica pontos de swing (topos e fundos)"""
        
        swing_points = []
        
        for i in range(window, len(df) - window):
            try:
                high_window = df['high'].iloc[i-window:i+window+1]
                low_window = df['low'].iloc[i-window:i+window+1]
                
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                # Verificar se é topo
                if current_high == high_window.max():
                    swing_points.append({
                        'type': 'high',
                        'price': current_high,
                        'timestamp': df['datetime'].iloc[i],
                        'index': i
                    })
                
                # Verificar se é fundo
                elif current_low == low_window.min():
                    swing_points.append({
                        'type': 'low',
                        'price': current_low,
                        'timestamp': df['datetime'].iloc[i],
                        'index': i
                    })
                    
            except Exception as e:
                logger.warning(f"Erro ao identificar swing no índice {i}: {e}")
                continue
        
        return swing_points
    
    def _identify_change_of_character(self, recent_swings: List[Dict], 
                                    pip_value: float) -> Optional[SmartMoneySignal]:
        """Identifica Change of Character (ChoCh)"""
        
        if len(recent_swings) < 4:
            return None
        
        try:
            # Verificar padrão para ChoCh Bullish
            # Precisa de: Low, High, Lower Low, quebra do High anterior
            
            # ChoCh Bullish: mercado bearish que quebra estrutura de alta
            lows = [s for s in recent_swings if s['type'] == 'low']
            highs = [s for s in recent_swings if s['type'] == 'high']
            
            if len(lows) >= 2 and len(highs) >= 1:
                last_low = lows[-1]
                prev_low = lows[-2]
                last_high = highs[-1] if highs else None
                
                # ChoCh Bullish: Lower Low seguido de quebra de High anterior
                if (last_high and 
                    last_low['price'] < prev_low['price'] and
                    last_low['index'] > last_high['index']):
                    
                    # Verificar se há quebra subsequente
                    break_size = (last_high['price'] - prev_low['price']) / pip_value
                    
                    if break_size >= self.min_break_pips:
                        return SmartMoneySignal(
                            signal_type="ChoCh_Bullish",
                            direction="bullish",
                            price=last_high['price'],
                            timestamp=last_low['timestamp'],
                            strength=70.0,  # ChoCh geralmente é forte
                            timeframe="current",
                            description=f"Change of Character Bullish - {break_size:.1f} pips",
                            additional_data={
                                'lower_low': last_low['price'],
                                'broken_high': last_high['price'],
                                'break_size_pips': break_size
                            }
                        )
            
            # ChoCh Bearish: mercado bullish que quebra estrutura de baixa
            if len(highs) >= 2 and len(lows) >= 1:
                last_high = highs[-1]
                prev_high = highs[-2]
                last_low = lows[-1] if lows else None
                
                # ChoCh Bearish: Higher High seguido de quebra de Low anterior
                if (last_low and 
                    last_high['price'] > prev_high['price'] and
                    last_high['index'] > last_low['index']):
                    
                    break_size = (prev_high['price'] - last_low['price']) / pip_value
                    
                    if break_size >= self.min_break_pips:
                        return SmartMoneySignal(
                            signal_type="ChoCh_Bearish",
                            direction="bearish",
                            price=last_low['price'],
                            timestamp=last_high['timestamp'],
                            strength=70.0,
                            timeframe="current",
                            description=f"Change of Character Bearish - {break_size:.1f} pips",
                            additional_data={
                                'higher_high': last_high['price'],
                                'broken_low': last_low['price'],
                                'break_size_pips': break_size
                            }
                        )
                        
        except Exception as e:
            logger.warning(f"Erro ao identificar ChoCh: {e}")
        
        return None
    
    def _calculate_structure_strength(self, swing_context: List[Dict], 
                                    structure_type: str) -> float:
        """Calcula força da mudança estrutural"""
        
        if len(swing_context) < 2:
            return 50.0
        
        strength = 0.0
        
        # Fator 1: Consistência da tendência anterior (40 pontos)
        if structure_type == 'bullish_mss':
            # Verificar se havia tendência bearish consistente
            lows = [s['price'] for s in swing_context if s['type'] == 'low']
            if len(lows) >= 2:
                is_consistent = all(lows[i] <= lows[i+1] for i in range(len(lows)-1))
                strength += 40 if is_consistent else 20
        elif structure_type == 'bearish_mss':
            # Verificar se havia tendência bullish consistente
            highs = [s['price'] for s in swing_context if s['type'] == 'high']
            if len(highs) >= 2:
                is_consistent = all(highs[i] <= highs[i+1] for i in range(len(highs)-1))
                strength += 40 if is_consistent else 20
        
        # Fator 2: Magnitude da quebra (30 pontos)
        if len(swing_context) >= 2:
            latest = swing_context[-1]
            previous = swing_context[-2]
            
            price_diff = abs(latest['price'] - previous['price'])
            avg_price = (latest['price'] + previous['price']) / 2
            
            if avg_price > 0:
                percentage_break = (price_diff / avg_price) * 100
                magnitude_strength = min(30, percentage_break * 1000)
                strength += magnitude_strength
        
        # Fator 3: Contexto temporal (30 pontos)
        if len(swing_context) >= 3:
            time_consistency = 30  # Simplificado
            strength += time_consistency
        
        return min(100, max(0, strength))

class LiquidityAnalyzer:
    """Analisador de zonas de liquidez"""
    
    def __init__(self, equal_level_tolerance: float = 0.0002):
        self.equal_level_tolerance = equal_level_tolerance
    
    def identify_liquidity_zones(self, df: pd.DataFrame, pair: str) -> List[SmartMoneySignal]:
        """Identifica zonas de liquidez (Equal Highs/Lows)"""
        
        signals = []
        
        if len(df) < 20:
            return signals
        
        # Identificar swing points
        swing_analyzer = MarketStructureAnalyzer()
        swing_points = swing_analyzer._identify_swing_points(df)
        
        # Agrupar por tipo
        highs = [s for s in swing_points if s['type'] == 'high']
        lows = [s for s in swing_points if s['type'] == 'low']
        
        # Identificar Equal Highs
        equal_highs = self._find_equal_levels(highs, 'high')
        for level_group in equal_highs:
            if len(level_group) >= 2:  # Pelo menos 2 topos iguais
                signal = SmartMoneySignal(
                    signal_type="Liquidity_EqualHighs",
                    direction="bearish",  # Equal highs são bearish (sell stops acima)
                    price=level_group[0]['price'],
                    timestamp=level_group[-1]['timestamp'],
                    strength=min(100, len(level_group) * 25),
                    timeframe="current",
                    description=f"Equal Highs - {len(level_group)} toques em {level_group[0]['price']:.5f}",
                    additional_data={
                        'level_type': 'equal_highs',
                        'touch_count': len(level_group),
                        'touch_points': level_group
                    }
                )
                signals.append(signal)
        
        # Identificar Equal Lows
        equal_lows = self._find_equal_levels(lows, 'low')
        for level_group in equal_lows:
            if len(level_group) >= 2:  # Pelo menos 2 fundos iguais
                signal = SmartMoneySignal(
                    signal_type="Liquidity_EqualLows",
                    direction="bullish",  # Equal lows são bullish (buy stops abaixo)
                    price=level_group[0]['price'],
                    timestamp=level_group[-1]['timestamp'],
                    strength=min(100, len(level_group) * 25),
                    timeframe="current",
                    description=f"Equal Lows - {len(level_group)} toques em {level_group[0]['price']:.5f}",
                    additional_data={
                        'level_type': 'equal_lows',
                        'touch_count': len(level_group),
                        'touch_points': level_group
                    }
                )
                signals.append(signal)
        
        return signals
    
    def _find_equal_levels(self, swing_points: List[Dict], level_type: str) -> List[List[Dict]]:
        """Encontra níveis iguais (dentro da tolerância)"""
        
        if len(swing_points) < 2:
            return []
        
        equal_groups = []
        used_points = set()
        
        for i, point in enumerate(swing_points):
            if i in used_points:
                continue
            
            # Encontrar pontos próximos a este nível
            level_group = [point]
            used_points.add(i)
            
            for j, other_point in enumerate(swing_points[i+1:], i+1):
                if j in used_points:
                    continue
                
                price_diff = abs(point['price'] - other_point['price'])
                tolerance = point['price'] * self.equal_level_tolerance
                
                if price_diff <= tolerance:
                    level_group.append(other_point)
                    used_points.add(j)
            
            if len(level_group) >= 2:
                # Ordenar por timestamp
                level_group.sort(key=lambda x: x['timestamp'])
                equal_groups.append(level_group)
        
        return equal_groups

class SmartMoneyAnalyzer:
    """Analisador principal que combina todos os conceitos Smart Money"""
    
    def __init__(self):
        self.fvg_analyzer = FairValueGapAnalyzer()
        self.ob_analyzer = OrderBlockAnalyzer()
        self.structure_analyzer = MarketStructureAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()
    
    def analyze(self, df: pd.DataFrame, pair: str, timeframe: str = "15m") -> Dict[str, List[SmartMoneySignal]]:
        """Executa análise completa Smart Money"""
        
        results = {
            'fair_value_gaps': [],
            'order_blocks': [],
            'market_structure': [],
            'liquidity_zones': [],
            'all_signals': []
        }
        
        try:
            # Analisar Fair Value Gaps
            logger.info("Analisando Fair Value Gaps...")
            results['fair_value_gaps'] = self.fvg_analyzer.identify_fvgs(df, pair)
            
            # Analisar Order Blocks
            logger.info("Analisando Order Blocks...")
            results['order_blocks'] = self.ob_analyzer.identify_order_blocks(df, pair)
            
            # Analisar Market Structure
            logger.info("Analisando Market Structure...")
            results['market_structure'] = self.structure_analyzer.identify_structure_shifts(df, pair)
            
            # Analisar Liquidez
            logger.info("Analisando Liquidez...")
            results['liquidity_zones'] = self.liquidity_analyzer.identify_liquidity_zones(df, pair)
            
            # Combinar todos os sinais
            all_signals = (results['fair_value_gaps'] + 
                          results['order_blocks'] + 
                          results['market_structure'] + 
                          results['liquidity_zones'])
            
            # Ordenar por timestamp
            all_signals.sort(key=lambda x: x.timestamp, reverse=True)
            results['all_signals'] = all_signals
            
            logger.info(f"Análise completa: {len(all_signals)} sinais identificados")
            
        except Exception as e:
            logger.error(f"Erro na análise Smart Money: {e}")
        
        return results
    
    def get_market_bias(self, signals: List[SmartMoneySignal]) -> Dict:
        """Determina bias do mercado baseado nos sinais"""
        
        if not signals:
            return {
                'bias': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Nenhum sinal disponível'
            }
        
        # Calcular pontuação por direção
        bullish_score = 0
        bearish_score = 0
        
        for signal in signals:
            weight = signal.strength / 100.0
            
            if signal.direction == 'bullish':
                bullish_score += weight
            elif signal.direction == 'bearish':
                bearish_score += weight
        
        total_score = bullish_score + bearish_score
        
        if total_score == 0:
            return {
                'bias': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Sinais equilibrados'
            }
        
        # Determinar bias
        bullish_percentage = (bullish_score / total_score) * 100
        bearish_percentage = (bearish_score / total_score) * 100
        
        if bullish_percentage > 60:
            bias = 'BULLISH'
            confidence = bullish_percentage
        elif bearish_percentage > 60:
            bias = 'BEARISH'
            confidence = bearish_percentage
        else:
            bias = 'NEUTRAL'
            confidence = 50
        
        # Gerar reasoning
        strong_signals = [s for s in signals if s.strength > 70]
        reasoning = f"{len(strong_signals)} sinais fortes de {len(signals)} total. "
        reasoning += f"Bullish: {bullish_percentage:.1f}%, Bearish: {bearish_percentage:.1f}%"
        
        return {
            'bias': bias,
            'confidence': round(confidence, 1),
            'reasoning': reasoning
        }
    
    def filter_signals_by_strength(self, signals: List[SmartMoneySignal], 
                                 min_strength: float = 50.0) -> List[SmartMoneySignal]:
        """Filtra sinais por força mínima"""
        return [s for s in signals if s.strength >= min_strength]
    
    def get_confluence_signals(self, signals: List[SmartMoneySignal], 
                             price_tolerance: float = 0.001) -> List[Dict]:
        """Identifica sinais em confluência (próximos no preço)"""
        
        confluences = []
        used_signals = set()
        
        for i, signal in enumerate(signals):
            if i in used_signals:
                continue
            
            # Encontrar sinais próximos
            confluent_signals = [signal]
            used_signals.add(i)
            
            for j, other_signal in enumerate(signals[i+1:], i+1):
                if j in used_signals:
                    continue
                
                price_diff = abs(signal.price - other_signal.price)
                tolerance = signal.price * price_tolerance
                
                if price_diff <= tolerance:
                    confluent_signals.append(other_signal)
                    used_signals.add(j)
            
            if len(confluent_signals) >= 2:  # Pelo menos 2 sinais em confluência
                # Calcular força combinada
                combined_strength = sum(s.strength for s in confluent_signals) / len(confluent_signals)
                combined_strength = min(100, combined_strength * 1.2)  # Bonus por confluência
                
                # Determinar direção dominante
                bullish_count = sum(1 for s in confluent_signals if s.direction == 'bullish')
                bearish_count = sum(1 for s in confluent_signals if s.direction == 'bearish')
                
                dominant_direction = 'bullish' if bullish_count > bearish_count else 'bearish'
                
                confluences.append({
                    'signals': confluent_signals,
                    'avg_price': sum(s.price for s in confluent_signals) / len(confluent_signals),
                    'combined_strength': combined_strength,
                    'dominant_direction': dominant_direction,
                    'signal_count': len(confluent_signals),
                    'signal_types': list(set(s.signal_type for s in confluent_signals))
                })
        
        # Ordenar por força combinada
        confluences.sort(key=lambda x: x['combined_strength'], reverse=True)
        
        return confluences