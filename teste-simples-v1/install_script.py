"""
Script de instalação automática para Smart Money Forex Analyzer Pro
Execute este arquivo para corrigir todos os problemas de estrutura e dependências
"""

import os
import sys
from pathlib import Path
import subprocess

def print_header():
    """Imprime cabeçalho do instalador"""
    print("=" * 60)
    print("🚀 SMART MONEY FOREX ANALYZER PRO - INSTALADOR")
    print("=" * 60)
    print()

def check_python():
    """Verifica versão do Python"""
    print("🔍 Verificando Python...")
    
    if sys.version_info < (3, 8):
        print("❌ ERRO: Python 3.8+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        print("   Baixe uma versão mais recente em: https://python.org")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")
    return True

def create_structure():
    """Cria estrutura de diretórios e arquivos"""
    print("\n📁 Criando estrutura de diretórios...")
    
    # Diretórios principais
    directories = ['api', 'config', 'analysis', 'ui', 'utils', 'tests', 'data', 'logs']
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
        
        # Criar __init__.py para módulos Python
        if directory not in ['data', 'logs', 'tests']:
            init_file = dir_path / '__init__.py'
            init_content = f'"""\nMódulo {directory} para Smart Money Forex Analyzer Pro\n"""\n'
            init_file.write_text(init_content, encoding='utf-8')
            print(f"   ✅ {directory}/__init__.py")

def install_dependencies():
    """Instala dependências"""
    print("\n📦 Instalando dependências...")
    
    # Verificar se requirements.txt existe
    if not Path('requirements.txt').exists():
        print("❌ Arquivo requirements.txt não encontrado!")
        print("   Criando requirements.txt básico...")
        create_basic_requirements()
    
    try:
        # Atualizar pip primeiro
        print("   📋 Atualizando pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Instalar dependências
        print("   📋 Instalando pacotes...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
        else:
            print("⚠️ Algumas dependências falharam:")
            print(result.stderr)
            print("   Tentando instalação individual...")
            install_individual_packages()
            
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        print("   Tentando instalação individual...")
        install_individual_packages()

def create_basic_requirements():
    """Cria arquivo requirements.txt básico"""
    requirements = """# Smart Money Forex Analyzer Pro - Dependências Básicas
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
requests>=2.31.0
aiohttp>=3.8.0
python-dateutil>=2.8.0
"""
    Path('requirements.txt').write_text(requirements, encoding='utf-8')

def install_individual_packages():
    """Instala pacotes individualmente"""
    packages = [
        'streamlit>=1.28.0',
        'pandas>=2.0.0', 
        'numpy>=1.24.0',
        'plotly>=5.15.0',
        'requests>=2.31.0',
        'aiohttp>=3.8.0',
        'python-dateutil>=2.8.0'
    ]
    
    for package in packages:
        try:
            print(f"   📋 Instalando {package.split('>=')[0]}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
            print(f"   ✅ {package.split('>=')[0]} OK")
        except:
            print(f"   ❌ Falha: {package.split('>=')[0]}")

def create_missing_files():
    """Cria arquivos Python faltantes com conteúdo básico"""
    print("\n📄 Verificando arquivos principais...")
    
    files_to_check = {
        'config/settings.py': create_basic_settings,
        'api/manager.py': create_basic_api_manager,
        'analysis/smart_money.py': create_basic_smart_money,
        'ui/dashboard.py': create_basic_dashboard,
        'utils/helpers.py': create_basic_helpers
    }
    
    for file_path, creator_func in files_to_check.items():
        path = Path(file_path)
        if not path.exists():
            print(f"   📝 Criando {file_path}...")
            creator_func(path)
            print(f"   ✅ {file_path} criado")
        else:
            print(f"   ✅ {file_path} já existe")

def create_basic_settings(path):
    """Cria arquivo de configurações básico"""
    content = '''"""
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
'''
    path.write_text(content, encoding='utf-8')

def create_basic_api_manager(path):
    """Cria API manager básico"""
    content = '''"""
Gerenciador básico de APIs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class APIResponse:
    success: bool
    data: Any
    error_message: Optional[str] = None
    source: Optional[str] = None

class APIManager:
    def __init__(self):
        pass
    
    def get_api_status(self) -> Dict[str, bool]:
        return {"demo": True}
    
    async def get_market_overview(self, base_currency: str = "USD") -> Dict[str, APIResponse]:
        # Retorna dados demo
        demo_data = pd.DataFrame({
            'datetime': [datetime.now() - timedelta(hours=i) for i in range(100)],
            'open': np.random.uniform(1.08, 1.09, 100),
            'high': np.random.uniform(1.08, 1.09, 100),
            'low': np.random.uniform(1.08, 1.09, 100),
            'close': np.random.uniform(1.08, 1.09, 100),
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        return {
            'forex': APIResponse(True, demo_data, source="Demo"),
            'news': APIResponse(True, [], source="Demo"),
            'crypto': APIResponse(True, {}, source="Demo")
        }
'''
    path.write_text(content, encoding='utf-8')

def create_basic_smart_money(path):
    """Cria analisador Smart Money básico"""
    content = '''"""
Analisador Smart Money básico
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SmartMoneySignal:
    signal_type: str
    direction: str
    price: float
    timestamp: datetime
    strength: float
    timeframe: str
    description: str

class SmartMoneyAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, df: pd.DataFrame, pair: str, timeframe: str = "15m") -> Dict:
        # Análise básica demo
        signals = [
            SmartMoneySignal(
                "FVG_Bullish", "bullish", df['close'].iloc[-1], 
                datetime.now(), 75.0, timeframe, "Demo FVG Bullish"
            )
        ]
        
        return {
            'fair_value_gaps': signals,
            'order_blocks': [],
            'market_structure': [],
            'liquidity_zones': [],
            'all_signals': signals
        }
    
    def get_market_bias(self, signals: List) -> Dict:
        return {
            'bias': 'BULLISH',
            'confidence': 75.0,
            'reasoning': 'Análise demo'
        }
    
    def filter_signals_by_strength(self, signals: List, min_strength: float) -> List:
        return [s for s in signals if s.strength >= min_strength]
    
    def get_confluence_signals(self, signals: List) -> List:
        return []
'''
    path.write_text(content, encoding='utf-8')

def create_basic_dashboard(path):
    """Cria dashboard básico"""
    content = '''"""
Dashboard básico para Smart Money Forex Analyzer Pro
"""

import streamlit as st
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta

class ForexDashboard:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        if 'first_run' not in st.session_state:
            st.session_state.first_run = True
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = True
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
    
    def run(self):
        if st.session_state.first_run:
            self.show_welcome_message()
        else:
            self.render_main_app()
    
    def show_welcome_message(self):
        st.markdown("""
        ## 🚀 Bem-vindo ao Smart Money Forex Analyzer Pro!
        
        Esta é uma versão básica funcional da aplicação.
        
        **Recursos disponíveis:**
        - 📊 Análise demo de Smart Money
        - 📈 Gráficos básicos
        - 🎯 Sinais simulados
        """)
        
        if st.button("🚀 Começar", type="primary"):
            st.session_state.first_run = False
            st.rerun()
    
    def render_main_app(self):
        st.title("📊 Smart Money Analyzer Pro")
        
        # Sidebar básica
        st.sidebar.title("⚙️ Configurações")
        
        pair = st.sidebar.selectbox("Par", ["EUR/USD", "GBP/USD", "USD/JPY"])
        timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h"])
        
        if st.sidebar.button("🚀 Executar Análise Demo"):
            self.run_demo_analysis(pair, timeframe)
        
        # Mostrar resultados se existirem
        if st.session_state.analysis_history:
            self.show_results()
    
    def run_demo_analysis(self, pair, timeframe):
        with st.spinner("Executando análise..."):
            # Criar dados demo
            dates = [datetime.now() - timedelta(hours=i) for i in range(100, 0, -1)]
            data = {
                'datetime': dates,
                'open': np.random.uniform(1.08, 1.09, 100),
                'high': np.random.uniform(1.085, 1.095, 100),
                'low': np.random.uniform(1.075, 1.085, 100),
                'close': np.random.uniform(1.08, 1.09, 100),
                'volume': np.random.randint(1000, 10000, 100)
            }
            
            df = pd.DataFrame(data)
            
            # Salvar resultados
            analysis = {
                'pair': pair,
                'timeframe': timeframe,
                'data': df,
                'signals': [
                    {'type': 'FVG_Bullish', 'price': 1.0850, 'strength': 75},
                    {'type': 'OB_Bearish', 'price': 1.0890, 'strength': 60}
                ],
                'timestamp': datetime.now()
            }
            
            st.session_state.analysis_history.append(analysis)
            st.success("✅ Análise concluída!")
            st.rerun()
    
    def show_results(self):
        latest = st.session_state.analysis_history[-1]
        
        st.subheader(f"📊 Resultados - {latest['pair']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Par", latest['pair'])
        with col2:
            st.metric("Timeframe", latest['timeframe'])
        with col3:
            st.metric("Sinais", len(latest['signals']))
        
        # Gráfico básico
        import plotly.graph_objects as go
        
        df = latest['data']
        fig = go.Figure(data=go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ))
        
        fig.update_layout(title=f"{latest['pair']} - {latest['timeframe']}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de sinais
        st.subheader("🎯 Sinais Identificados")
        signals_df = pd.DataFrame(latest['signals'])
        st.dataframe(signals_df, use_container_width=True)
'''
    path.write_text(content, encoding='utf-8')

def create_basic_helpers(path):
    """Cria arquivo de helpers básico"""
    content = '''"""
Funções utilitárias básicas
"""

def format_currency_pair(pair: str, format_type: str = "display") -> str:
    """Formata par de moedas"""
    if format_type == "api":
        return pair.replace("/", "")
    return pair.upper()

def calculate_pips(price1: float, price2: float, pair: str) -> float:
    """Calcula diferença em pips"""
    if "JPY" in pair.upper():
        pip_value = 0.01
    else:
        pip_value = 0.0001
    return abs(price1 - price2) / pip_value

def format_number(number: float, decimal_places: int = 2) -> str:
    """Formata número para exibição"""
    return f"{number:,.{decimal_places}f}"
'''
    path.write_text(content, encoding='utf-8')

def create_env_file():
    """Cria arquivo .env de exemplo"""
    print("\n🔧 Criando arquivo de configuração...")
    
    env_content = """# Smart Money Forex Analyzer Pro - Configurações
# Copie este arquivo para .env e configure suas API keys

# APIs Opcionais (deixe vazio para modo demo)
NEWSAPI_KEY=
ALPHA_VANTAGE_KEY=
MARKETAUX_KEY=

# Configurações
DEBUG=False
LOG_LEVEL=INFO
"""
    
    Path('.env.example').write_text(env_content, encoding='utf-8')
    print("✅ .env.example criado")

def test_installation():
    """Testa se a instalação funcionou"""
    print("\n🧪 Testando instalação...")
    
    try:
        # Testar imports básicos
        import streamlit
        print("✅ Streamlit OK")
        
        import pandas
        print("✅ Pandas OK")
        
        import plotly
        print("✅ Plotly OK")
        
        # Testar estrutura de arquivos
        required_files = [
            'main.py',
            'config/settings.py',
            'api/manager.py',
            'analysis/smart_money.py',
            'ui/dashboard.py',
            'utils/helpers.py'
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} OK")
            else:
                print(f"❌ {file_path} FALTANDO")
                return False
        
        print("\n🎉 Instalação bem-sucedida!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print()
    print("1. 🚀 Execute a aplicação:")
    print("   streamlit run main.py")
    print()
    print("2. 🌐 Acesse no navegador:")
    print("   http://localhost:8501")
    print()
    print("3. 🔧 Configure APIs opcionais (opcional):")
    print("   - Copie .env.example para .env")
    print("   - Configure suas API keys")
    print()
    print("4. 📚 A aplicação funciona no modo DEMO sem configuração!")
    print()
    print("⚠️  NOTA: Esta é uma versão básica funcional.")
    print("   Para recursos completos, certifique-se de ter todos os arquivos originais.")
    print()

def main():
    """Função principal do instalador"""
    print_header()
    
    # Verificações
    if not check_python():
        return
    
    # Criação da estrutura
    create_structure()
    
    # Instalação de dependências
    install_dependencies()
    
    # Criação de arquivos faltantes
    create_missing_files()
    
    # Arquivo de configuração
    create_env_file()
    
    # Teste final
    if test_installation():
        show_next_steps()
    else:
        print("\n❌ Instalação teve problemas. Verifique os erros acima.")

if __name__ == "__main__":
    main()