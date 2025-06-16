"""
Dashboard principal da aplicação Smart Money Forex Analyzer Pro
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Imports locais
from api.manager import APIManager
from analysis.smart_money import SmartMoneyAnalyzer
from config.settings import AppConfig, ForexPairs, UIConfiguration, APP_MESSAGES
from utils.helpers import format_currency_pair, calculate_pips, format_number

logger = logging.getLogger(__name__)

class ForexDashboard:
    """Dashboard principal da aplicação"""
    
    def __init__(self):
        self.api_manager = APIManager()
        self.smart_money_analyzer = SmartMoneyAnalyzer()
        self.setup_session_state()
    
    def setup_session_state(self):
        """Inicializa variáveis de sessão"""
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {}
        
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = True
        
        if 'first_run' not in st.session_state:
            st.session_state.first_run = True
    
    def run(self):
        """Executa o dashboard principal"""
        
        # Mostrar mensagem de boas-vindas na primeira execução
        if st.session_state.first_run:
            self.show_welcome_message()
            return
        
        # Layout principal
        self.render_sidebar()
        self.render_main_content()
    
    def show_welcome_message(self):
        """Mostra mensagem de boas-vindas"""
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(APP_MESSAGES['welcome'])
            
            if st.button("🚀 Começar Análise", type="primary", use_container_width=True):
                st.session_state.first_run = False
                st.rerun()
            
            with st.expander("📖 Sobre a Aplicação"):
                st.markdown(APP_MESSAGES['api_info'])
            
            with st.expander("⚠️ Disclaimer"):
                st.markdown(APP_MESSAGES['disclaimer'])
    
    def render_sidebar(self):
        """Renderiza barra lateral com configurações"""
        
        st.sidebar.title("🎯 Smart Money Pro")
        st.sidebar.markdown("---")
        
        # Status das APIs
        self.render_api_status()
        
        # Configurações de APIs
        self.render_api_configuration()
        
        # Parâmetros de análise
        analysis_params = self.render_analysis_parameters()
        
        # Botão de análise
        self.render_analysis_button(analysis_params)
        
        # Links úteis
        self.render_useful_links()
        
        return analysis_params
    
    def render_api_status(self):
        """Renderiza status das APIs"""
        
        st.sidebar.subheader("📊 Status APIs")
        
        # Verificar status das APIs
        api_status = self.api_manager.get_api_status()
        
        status_items = [
            ("Frankfurter", True, "Forex gratuito"),
            ("ExchangeRate-API", True, "Forex backup"),
            ("NewsAPI", 'NEWSAPI' in st.session_state.api_keys, "Notícias econômicas"),
            ("Alpha Vantage", 'ALPHA_VANTAGE' in st.session_state.api_keys, "Dados históricos"),
            ("CoinGecko", True, "Crypto correlação")
        ]
        
        for name, active, description in status_items:
            status_icon = "✅" if active else "⚠️"
            color = "api-status-active" if active else "api-status-inactive"
            
            st.sidebar.markdown(f"""
            <div class="{color}">
                {status_icon} <strong>{name}</strong><br>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)
            st.sidebar.markdown("")
    
    def render_api_configuration(self):
        """Renderiza configuração de API keys"""
        
        with st.sidebar.expander("🔑 Configurar APIs"):
            st.markdown("**APIs Opcionais (para dados premium):**")
            
            # NewsAPI
            newsapi_key = st.text_input(
                "NewsAPI Key",
                value=st.session_state.api_keys.get('NEWSAPI', ''),
                type="password",
                help="100 requests/dia grátis - newsapi.org"
            )
            
            # Alpha Vantage
            alphav_key = st.text_input(
                "Alpha Vantage Key",
                value=st.session_state.api_keys.get('ALPHA_VANTAGE', ''),
                type="password",
                help="5 requests/min grátis - alphavantage.co"
            )
            
            # MarketAux
            marketaux_key = st.text_input(
                "MarketAux Key",
                value=st.session_state.api_keys.get('MARKETAUX', ''),
                type="password",
                help="100 requests/dia grátis - marketaux.com"
            )
            
            if st.button("💾 Salvar APIs"):
                st.session_state.api_keys.update({
                    'NEWSAPI': newsapi_key,
                    'ALPHA_VANTAGE': alphav_key,
                    'MARKETAUX': marketaux_key
                })
                st.success("✅ APIs salvas!")
                st.rerun()
            
            st.markdown("---")
            st.markdown("**💡 Dica:** A aplicação funciona sem API keys usando dados demo!")
    
    def render_analysis_parameters(self) -> Dict:
        """Renderiza parâmetros de análise"""
        
        st.sidebar.subheader("⚙️ Parâmetros")
        
        # Seleção de par
        selected_pair = st.sidebar.selectbox(
            "Par de Moedas",
            ForexPairs.ALL_PAIRS,
            index=0,
            help="Selecione o par forex para análise"
        )
        
        # Timeframe
        timeframes = {
            "1m": "1 Minuto",
            "5m": "5 Minutos", 
            "15m": "15 Minutos",
            "30m": "30 Minutos",
            "1h": "1 Hora",
            "4h": "4 Horas",
            "1d": "1 Dia"
        }
        
        selected_timeframe = st.sidebar.selectbox(
            "Timeframe",
            list(timeframes.keys()),
            index=2,
            format_func=lambda x: timeframes[x]
        )
        
        # Número de dados
        data_points = st.sidebar.slider(
            "Dados Históricos",
            min_value=100,
            max_value=1000,
            value=500,
            step=50,
            help="Quantidade de velas para análise"
        )
        
        # Configurações avançadas
        with st.sidebar.expander("🔧 Configurações Avançadas"):
            min_signal_strength = st.slider(
                "Força Mínima do Sinal (%)",
                min_value=0,
                max_value=100,
                value=40,
                help="Filtrar sinais abaixo desta força"
            )
            
            enable_confluence = st.checkbox(
                "Análise de Confluência",
                value=True,
                help="Identificar sinais em confluência"
            )
            
            enable_liquidity = st.checkbox(
                "Análise de Liquidez",
                value=True,
                help="Identificar zonas de liquidez"
            )
            
            demo_mode = st.checkbox(
                "Modo Demo",
                value=st.session_state.demo_mode,
                help="Usar dados simulados para demonstração"
            )
            
            st.session_state.demo_mode = demo_mode
        
        return {
            'pair': selected_pair,
            'timeframe': selected_timeframe,
            'data_points': data_points,
            'min_signal_strength': min_signal_strength,
            'enable_confluence': enable_confluence,
            'enable_liquidity': enable_liquidity,
            'demo_mode': demo_mode
        }
    
    def render_analysis_button(self, params: Dict):
        """Renderiza botão de análise"""
        
        st.sidebar.markdown("---")
        
        button_text = "🧪 Executar Análise DEMO" if params['demo_mode'] else "🚀 Executar Análise"
        
        if st.sidebar.button(button_text, type="primary", use_container_width=True):
            with st.spinner("🔄 Executando análise..."):
                self.execute_analysis(params)
    
    def render_useful_links(self):
        """Renderiza links úteis"""
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 Links Úteis")
        
        links = [
            ("📚 NewsAPI", "https://newsapi.org/"),
            ("📈 Alpha Vantage", "https://www.alphavantage.co/"),
            ("💰 MarketAux", "https://www.marketaux.com/"),
            ("🪙 CoinGecko", "https://www.coingecko.com/"),
            ("📊 TradingView", "https://www.tradingview.com/")
        ]
        
        for name, url in links:
            st.sidebar.markdown(f"[{name}]({url})")
    
    def render_main_content(self):
        """Renderiza conteúdo principal"""
        
        # Verificar se há análise recente
        if st.session_state.analysis_history:
            self.display_latest_analysis()
        else:
            self.display_empty_state()
    
    def display_empty_state(self):
        """Exibe estado vazio quando não há análise"""
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.info("""
            👈 **Configure os parâmetros na barra lateral e execute a análise**
            
            **Recursos disponíveis:**
            - 📊 Análise Smart Money Concepts
            - 🎯 Identificação de FVGs e Order Blocks
            - 📈 Market Structure Shifts
            - 💧 Zonas de Liquidez
            - 📰 Calendário Econômico
            - 🔄 Correlações de Mercado
            """)
    
    def display_latest_analysis(self):
        """Exibe a análise mais recente"""
        
        if not st.session_state.analysis_history:
            return
        
        latest_analysis = st.session_state.analysis_history[-1]
        
        # Header com informações da análise
        self.render_analysis_header(latest_analysis)
        
        # Métricas principais
        self.render_key_metrics(latest_analysis)
        
        # Layout principal
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico principal
            self.render_main_chart(latest_analysis)
            
            # Tabela de sinais
            self.render_signals_table(latest_analysis)
        
        with col2:
            # Bias do mercado
            self.render_market_bias(latest_analysis)
            
            # Notícias econômicas
            self.render_economic_news(latest_analysis)
            
            # Correlações
            self.render_correlations(latest_analysis)
        
        # Seções adicionais
        self.render_confluence_analysis(latest_analysis)
        self.render_tradingview_widget(latest_analysis)
    
    def render_analysis_header(self, analysis: Dict):
        """Renderiza cabeçalho da análise"""
        
        params = analysis['parameters']
        timestamp = analysis['timestamp']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Par Analisado",
                params['pair'],
                help="Par de moedas analisado"
            )
        
        with col2:
            st.metric(
                "Timeframe", 
                params['timeframe'].upper(),
                help="Intervalo de tempo utilizado"
            )
        
        with col3:
            st.metric(
                "Dados",
                f"{len(analysis.get('forex_data', []))} velas",
                help="Quantidade de dados analisados"
            )
        
        with col4:
            st.metric(
                "Atualizado",
                timestamp.strftime("%H:%M"),
                help="Horário da última análise"
            )
    
    def render_key_metrics(self, analysis: Dict):
        """Renderiza métricas principais"""
        
        signals = analysis.get('smart_money_signals', {}).get('all_signals', [])
        forex_data = analysis.get('forex_data')
        
        if forex_data is None or len(forex_data) == 0:
            return
        
        # Calcular métricas
        current_price = forex_data['close'].iloc[-1]
        previous_price = forex_data['close'].iloc[-2] if len(forex_data) > 1 else current_price
        
        price_change = current_price - previous_price
        price_change_pct = (price_change / previous_price) * 100 if previous_price != 0 else 0
        
        # ATR
        high_low = forex_data['high'] - forex_data['low']
        high_close = abs(forex_data['high'] - forex_data['close'].shift(1))
        low_close = abs(forex_data['low'] - forex_data['close'].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(14).mean().iloc[-1]
        
        # Volatilidade
        returns = forex_data['close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * 100
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric(
                "Preço Atual",
                f"{current_price:.5f}",
                f"{price_change:+.5f} ({price_change_pct:+.2f}%)",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                "ATR (14)",
                f"{atr:.5f}",
                help="Average True Range - medida de volatilidade"
            )
        
        with col3:
            st.metric(
                "Volatilidade",
                f"{volatility:.2f}%",
                help="Volatilidade dos retornos (20 períodos)"
            )
        
        with col4:
            bullish_signals = len([s for s in signals if s.direction == 'bullish'])
            bearish_signals = len([s for s in signals if s.direction == 'bearish'])
            
            st.metric(
                "Sinais",
                f"{len(signals)}",
                f"🟢{bullish_signals} 🔴{bearish_signals}"
            )
        
        with col5:
            strong_signals = len([s for s in signals if s.strength > 70])
            st.metric(
                "Sinais Fortes",
                strong_signals,
                help="Sinais com força > 70%"
            )
    
    def render_main_chart(self, analysis: Dict):
        """Renderiza gráfico principal com sinais"""
        
        forex_data = analysis.get('forex_data')
        signals = analysis.get('smart_money_signals', {}).get('all_signals', [])
        
        if forex_data is None or len(forex_data) == 0:
            st.warning("⚠️ Dados forex não disponíveis")
            return
        
        # Criar gráfico
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.8, 0.2],
            subplot_titles=('Análise Smart Money', 'Volume')
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=forex_data['datetime'],
                open=forex_data['open'],
                high=forex_data['high'],
                low=forex_data['low'],
                close=forex_data['close'],
                name="OHLC",
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        # Adicionar sinais
        signal_colors = UIConfiguration.SIGNAL_COLORS
        
        for signal in signals:
            color = signal_colors.get(signal.signal_type, '#ffffff')
            
            # Determinar símbolo baseado no tipo
            if 'MSS' in signal.signal_type:
                symbol = 'diamond'
                size = 12
            elif 'FVG' in signal.signal_type:
                symbol = 'circle'
                size = 10
            elif 'OB' in signal.signal_type:
                symbol = 'square'
                size = 10
            else:
                symbol = 'triangle-up' if signal.direction == 'bullish' else 'triangle-down'
                size = 10
            
            fig.add_trace(
                go.Scatter(
                    x=[signal.timestamp],
                    y=[signal.price],
                    mode='markers',
                    marker=dict(
                        size=size,
                        color=color,
                        symbol=symbol,
                        line=dict(width=2, color='white')
                    ),
                    name=signal.signal_type,
                    text=signal.description,
                    hovertemplate=f"<b>{signal.signal_type}</b><br>" +
                                f"Preço: {signal.price:.5f}<br>" +
                                f"Força: {signal.strength:.1f}%<br>" +
                                f"Tempo: {signal.timestamp}<br>" +
                                f"{signal.description}<extra></extra>",
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Volume
        volume_colors = ['green' if close >= open_price else 'red' 
                        for close, open_price in zip(forex_data['close'], forex_data['open'])]
        
        fig.add_trace(
            go.Bar(
                x=forex_data['datetime'],
                y=forex_data['volume'],
                name="Volume",
                marker_color=volume_colors,
                opacity=0.6
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title=f"Smart Money Analysis - {analysis['parameters']['pair']}",
            xaxis_rangeslider_visible=False,
            height=700,
            template='plotly_dark',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_signals_table(self, analysis: Dict):
        """Renderiza tabela de sinais"""
        
        signals = analysis.get('smart_money_signals', {}).get('all_signals', [])
        
        if not signals:
            st.warning("⚠️ Nenhum sinal identificado")
            return
        
        st.subheader("🎯 Sinais Identificados")
        
        # Preparar dados para tabela
        table_data = []
        for signal in signals[:20]:  # Mostrar apenas os 20 mais recentes
            direction_emoji = "🟢" if signal.direction == 'bullish' else "🔴"
            strength_stars = "⭐" * min(5, int(signal.strength / 20))
            
            table_data.append({
                'Tipo': signal.signal_type.replace('_', ' '),
                'Dir': direction_emoji,
                'Preço': f"{signal.price:.5f}",
                'Força': f"{signal.strength:.0f}%",
                'Stars': strength_stars,
                'Tempo': signal.timestamp.strftime('%H:%M'),
                'Descrição': signal.description[:50] + "..." if len(signal.description) > 50 else signal.description
            })
        
        if table_data:
            df_signals = pd.DataFrame(table_data)
            st.dataframe(df_signals, use_container_width=True, hide_index=True)
    
    def render_market_bias(self, analysis: Dict):
        """Renderiza bias do mercado"""
        
        signals = analysis.get('smart_money_signals', {}).get('all_signals', [])
        
        if not signals:
            st.warning("⚠️ Dados insuficientes para bias")
            return
        
        # Calcular bias usando o analisador
        bias_data = self.smart_money_analyzer.get_market_bias(signals)
        
        st.subheader("🎯 Bias do Mercado")
        
        # Card do bias
        bias = bias_data['bias']
        confidence = bias_data['confidence']
        
        if bias == 'BULLISH':
            st.success(f"📈 **{bias}** ({confidence:.1f}%)")
        elif bias == 'BEARISH':
            st.error(f"📉 **{bias}** ({confidence:.1f}%)")
        else:
            st.warning(f"⚖️ **{bias}** ({confidence:.1f}%)")
        
        st.caption(bias_data['reasoning'])
        
        # Estatísticas detalhadas
        with st.expander("📊 Detalhes"):
            bullish_count = len([s for s in signals if s.direction == 'bullish'])
            bearish_count = len([s for s in signals if s.direction == 'bearish'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Bullish", bullish_count)
            with col2:
                st.metric("Bearish", bearish_count)
            
            # Força média por tipo
            signal_types = {}
            for signal in signals:
                if signal.signal_type not in signal_types:
                    signal_types[signal.signal_type] = []
                signal_types[signal.signal_type].append(signal.strength)
            
            for signal_type, strengths in signal_types.items():
                avg_strength = np.mean(strengths)
                st.text(f"{signal_type}: {avg_strength:.1f}%")
    
    def render_economic_news(self, analysis: Dict):
        """Renderiza notícias econômicas"""
        
        news_data = analysis.get('news_data', [])
        
        st.subheader("📰 Calendário Econômico")
        
        if not news_data:
            st.info("📰 Carregando notícias...")
            return
        
        # Mostrar até 8 notícias mais recentes
        for news in news_data[:8]:
            importance = news.get('importance', 'Low')
            
            # Cores baseadas na importância
            if importance == 'High':
                st.markdown(f"""
                <div class="news-high" style="padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <strong>🔴 {news.get('title', 'N/A')}</strong><br>
                    <small>{news.get('timestamp', 'N/A')} | {news.get('currency', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
            elif importance == 'Medium':
                st.markdown(f"""
                <div class="news-medium" style="padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <strong>🟡 {news.get('title', 'N/A')}</strong><br>
                    <small>{news.get('timestamp', 'N/A')} | {news.get('currency', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="news-low" style="padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <strong>🟢 {news.get('title', 'N/A')}</strong><br>
                    <small>{news.get('timestamp', 'N/A')} | {news.get('currency', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    def render_correlations(self, analysis: Dict):
        """Renderiza correlações de mercado"""
        
        st.subheader("🔗 Correlações")
        
        # Dados de crypto para correlação
        crypto_data = analysis.get('crypto_data', {})
        
        if crypto_data:
            st.write("**Criptomoedas:**")
            
            for crypto, data in crypto_data.items():
                price = data.get('price', 0)
                change = data.get('change_24h', 0)
                
                delta_color = "normal" if change >= 0 else "inverse"
                
                st.metric(
                    crypto,
                    f"${price:,.0f}" if price > 100 else f"${price:.2f}",
                    f"{change:+.2f}%",
                    delta_color=delta_color
                )
        else:
            st.info("📊 Carregando correlações...")
    
    def render_confluence_analysis(self, analysis: Dict):
        """Renderiza análise de confluência"""
        
        signals = analysis.get('smart_money_signals', {}).get('all_signals', [])
        
        if not signals:
            return
        
        st.subheader("🎯 Análise de Confluência")
        
        # Obter confluências
        confluences = self.smart_money_analyzer.get_confluence_signals(signals)
        
        if not confluences:
            st.info("ℹ️ Nenhuma confluência significativa identificada")
            return
        
        for i, confluence in enumerate(confluences[:5]):  # Mostrar top 5
            with st.expander(f"Confluência #{i+1} - Força: {confluence['combined_strength']:.1f}%"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Preço Médio", f"{confluence['avg_price']:.5f}")
                    st.metric("Direção", confluence['dominant_direction'].title())
                
                with col2:
                    st.metric("Sinais", confluence['signal_count'])
                    st.metric("Força Combinada", f"{confluence['combined_strength']:.1f}%")
                
                st.write("**Tipos de Sinais:**")
                for signal_type in confluence['signal_types']:
                    st.write(f"• {signal_type.replace('_', ' ')}")
    
    def render_tradingview_widget(self, analysis: Dict):
        """Renderiza widget do TradingView"""
        
        pair = analysis['parameters']['pair']
        symbol = f"FX:{pair.replace('/', '')}"
        
        st.subheader("📈 TradingView")
        
        tradingview_html = f"""
        <div style="height: 500px;">
            <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol={symbol}&interval=15&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&theme=dark&style=1&timezone=Etc%2FUTC&locale=en" 
                    style="width: 100%; height: 100%; margin: 0; padding: 0;" 
                    frameborder="0" allowtransparency="true" scrolling="no">
            </iframe>
        </div>
        """
        
        st.components.v1.html(tradingview_html, height=520)
    
    def execute_analysis(self, params: Dict):
        """Executa análise completa"""
        
        try:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 1. Coleta de dados
            status_text.text("📊 Coletando dados forex...")
            progress_bar.progress(20)
            
            if params['demo_mode']:
                forex_data = self._generate_demo_forex_data(params)
            else:
                forex_data = asyncio.run(self._get_real_forex_data(params))
            
            # 2. Coleta de notícias
            status_text.text("📰 Coletando notícias...")
            progress_bar.progress(40)
            
            if params['demo_mode']:
                news_data = self._generate_demo_news()
            else:
                news_data = asyncio.run(self._get_real_news_data())
            
            # 3. Coleta de dados de cripto
            status_text.text("🪙 Coletando dados crypto...")
            progress_bar.progress(60)
            
            crypto_data = asyncio.run(self._get_crypto_data())
            
            # 4. Análise Smart Money
            status_text.text("🎯 Executando análise Smart Money...")
            progress_bar.progress(80)
            
            smart_money_results = self.smart_money_analyzer.analyze(
                forex_data, 
                params['pair'], 
                params['timeframe']
            )
            
            # 5. Filtrar sinais por força
            all_signals = smart_money_results['all_signals']
            filtered_signals = self.smart_money_analyzer.filter_signals_by_strength(
                all_signals, 
                params['min_signal_strength']
            )
            
            smart_money_results['all_signals'] = filtered_signals
            
            # 6. Salvar resultados
            status_text.text("✅ Finalizando...")
            progress_bar.progress(100)
            
            analysis_result = {
                'timestamp': datetime.now(),
                'parameters': params,
                'forex_data': forex_data,
                'news_data': news_data,
                'crypto_data': crypto_data,
                'smart_money_signals': smart_money_results
            }
            
            # Adicionar ao histórico
            st.session_state.analysis_history.append(analysis_result)
            
            # Limpar progress
            progress_bar.empty()
            status_text.empty()
            
            # Mostrar sucesso
            st.success("✅ Análise concluída com sucesso!")
            
            # Recarregar para mostrar resultados
            st.rerun()
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            st.error(f"❌ Erro na análise: {str(e)}")
    
    async def _get_real_forex_data(self, params: Dict) -> pd.DataFrame:
        """Obtém dados forex reais via API"""
        
        try:
            pair_formatted = params['pair'].replace('/', '')
            
            # Usar Historical API para dados OHLC
            response = await self.api_manager.historical_api.get_historical_data(
                pair_formatted, 
                params['timeframe'], 
                params['data_points']
            )
            
            if response.success:
                return response.data
            else:
                # Fallback para dados demo
                return self._generate_demo_forex_data(params)
                
        except Exception as e:
            logger.error(f"Erro ao obter dados forex: {e}")
            return self._generate_demo_forex_data(params)
    
    async def _get_real_news_data(self) -> List[Dict]:
        """Obtém notícias econômicas reais"""
        
        try:
            response = await self.api_manager.news_api.get_economic_news()
            
            if response.success:
                return response.data
            else:
                return self._generate_demo_news()
                
        except Exception as e:
            logger.error(f"Erro ao obter notícias: {e}")
            return self._generate_demo_news()
    
    async def _get_crypto_data(self) -> Dict:
        """Obtém dados de criptomoedas"""
        
        try:
            response = await self.api_manager.crypto_api.get_crypto_data()
            
            if response.success:
                return response.data
            else:
                return self._generate_demo_crypto()
                
        except Exception as e:
            logger.error(f"Erro ao obter dados crypto: {e}")
            return self._generate_demo_crypto()
    
    def _generate_demo_forex_data(self, params: Dict) -> pd.DataFrame:
        """Gera dados forex demo"""
        
        # Preços base
        base_prices = {
            'EUR/USD': 1.0850, 'GBP/USD': 1.2650, 'USD/JPY': 149.50,
            'AUD/USD': 0.6550, 'USD/CAD': 1.3650, 'USD/CHF': 0.8750,
            'NZD/USD': 0.6150, 'EUR/GBP': 0.8580, 'EUR/JPY': 162.30,
            'GBP/JPY': 189.20
        }
        
        base_price = base_prices.get(params['pair'], 1.0000)
        
        # Timeframes
        timeframe_map = {
            '1m': timedelta(minutes=1), '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15), '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1), '4h': timedelta(hours=4),
            '1d': timedelta(days=1)
        }
        
        time_delta = timeframe_map.get(params['timeframe'], timedelta(minutes=15))
        end_time = datetime.now()
        
        # Gerar dados
        data = []
        current_price = base_price
        
        for i in range(params['data_points']):
            timestamp = end_time - (time_delta * (params['data_points'] - i - 1))
            
            # Simular movimento de preço mais realista
            volatility = 0.001 if 'JPY' not in params['pair'] else 0.01
            trend = np.sin(i / 50) * 0.0005
            noise = np.random.normal(0, volatility)
            
            # Adicionar eventos ocasionais (spikes)
            if np.random.random() < 0.05:  # 5% chance de evento
                noise += np.random.choice([-1, 1]) * volatility * 3
            
            price_change = trend + noise
            current_price = current_price * (1 + price_change)
            
            # Gerar OHLC realista
            range_size = current_price * np.random.uniform(0.0005, 0.002)
            
            open_price = current_price + np.random.uniform(-range_size/3, range_size/3)
            close_price = current_price + np.random.uniform(-range_size/3, range_size/3)
            high_price = max(open_price, close_price) + np.random.uniform(0, range_size/2)
            low_price = min(open_price, close_price) - np.random.uniform(0, range_size/2)
            
            # Volume mais realista
            base_volume = 5000
            volume = base_volume + np.random.randint(-2000, 8000)
            volume = max(1000, volume)  # Mínimo de 1000
            
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
        
        return df
    
    def _generate_demo_news(self) -> List[Dict]:
        """Gera notícias demo"""
        
        now = datetime.now()
        
        demo_events = [
            {
                'timestamp': now + timedelta(hours=2),
                'title': 'Fed Chair Powell Speaks on Monetary Policy Outlook',
                'description': 'Federal Reserve Chairman discusses current economic conditions and future policy direction.',
                'source': 'Reuters',
                'importance': 'High',
                'currency': 'USD'
            },
            {
                'timestamp': now + timedelta(hours=4),
                'title': 'ECB Releases Monthly Economic Bulletin',
                'description': 'European Central Bank publishes comprehensive economic assessment for the Eurozone.',
                'source': 'Bloomberg',
                'importance': 'Medium',
                'currency': 'EUR'
            },
            {
                'timestamp': now + timedelta(days=1, hours=2),
                'title': 'UK GDP Data Shows Stronger Than Expected Growth',
                'description': 'British economy demonstrates resilience with positive quarterly GDP figures.',
                'source': 'Financial Times',
                'importance': 'High',
                'currency': 'GBP'
            },
            {
                'timestamp': now + timedelta(days=1, hours=6),
                'title': 'US Initial Jobless Claims at Multi-Year Lows',
                'description': 'Weekly unemployment claims data indicates robust labor market conditions.',
                'source': 'MarketWatch',
                'importance': 'Medium',
                'currency': 'USD'
            },
            {
                'timestamp': now + timedelta(days=2, hours=3),
                'title': 'Bank of Japan Maintains Ultra-Loose Monetary Policy',
                'description': 'Japanese central bank keeps interest rates unchanged amid economic uncertainty.',
                'source': 'Nikkei',
                'importance': 'High',
                'currency': 'JPY'
            },
            {
                'timestamp': now + timedelta(days=2, hours=8),
                'title': 'Australian Employment Change Beats Expectations',
                'description': 'Labor market data shows continued strength in Australian job creation.',
                'source': 'ABC News',
                'importance': 'Medium',
                'currency': 'AUD'
            }
        ]
        
        return demo_events
    
    def _generate_demo_crypto(self) -> Dict:
        """Gera dados crypto demo"""
        
        base_prices = {
            'BITCOIN': 42000,
            'ETHEREUM': 2500,
            'RIPPLE': 0.60
        }
        
        crypto_data = {}
        
        for crypto, base_price in base_prices.items():
            # Simular volatilidade crypto
            price_change = np.random.normal(0, 0.05)  # 5% volatilidade
            current_price = base_price * (1 + price_change)
            
            change_24h = np.random.normal(0, 8)  # Mudança diária
            
            crypto_data[crypto] = {
                'price': current_price,
                'change_24h': change_24h,
                'market_cap': current_price * np.random.randint(18000000, 20000000)
            }
        
        return crypto_data