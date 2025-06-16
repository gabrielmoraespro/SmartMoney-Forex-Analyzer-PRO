import streamlit as st
import sys
import os
from pathlib import Path
import logging

# Adicionar diretório raiz ao path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Verificar se os módulos existem antes de importar
def safe_import():
    """Importa módulos de forma segura"""
    try:
        from ui.dashboard import ForexDashboard
        from config.settings import AppConfig
        return ForexDashboard, AppConfig, None
    except ImportError as e:
        error_msg = f"Erro ao importar módulos: {e}"
        logger.error(error_msg)
        return None, None, error_msg

# Configuração da página
st.set_page_config(
    page_title="Smart Money Forex Analyzer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': 'Smart Money Forex Analyzer Pro - Análise Institucional Avançada'
    }
)

def show_error_page(error_message):
    """Mostra página de erro quando módulos não podem ser importados"""
    
    st.error("❌ Erro na Aplicação")
    
    st.markdown(f"""
    **Erro detectado:** {error_message}
    
    ### 🔧 Como corrigir:
    
    1. **Verifique a estrutura de arquivos:**
    ```
    📁 pasta_do_projeto/
    ├── main.py
    ├── requirements.txt
    ├── 📁 api/
    │   ├── __init__.py
    │   └── manager.py
    ├── 📁 config/
    │   ├── __init__.py
    │   └── settings.py
    ├── 📁 analysis/
    │   ├── __init__.py
    │   └── smart_money.py
    ├── 📁 ui/
    │   ├── __init__.py
    │   └── dashboard.py
    └── 📁 utils/
        ├── __init__.py
        └── helpers.py
    ```
    
    2. **Execute o setup:**
    ```bash
    python setup.py
    ```
    
    3. **Instale dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    
    4. **Crie arquivos __init__.py:**
    ```bash
    # Em cada pasta, crie um arquivo __init__.py vazio
    touch api/__init__.py
    touch config/__init__.py
    touch analysis/__init__.py
    touch ui/__init__.py
    touch utils/__init__.py
    ```
    """)
    
    if st.button("🔄 Tentar Novamente"):
        st.rerun()

def main():
    """Função principal da aplicação"""
    
    # Importar módulos de forma segura
    ForexDashboard, AppConfig, error = safe_import()
    
    if error:
        show_error_page(error)
        return
    
    try:
        # CSS personalizado
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .metric-card {
            background: #f0f2f6;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #2a5298;
        }
        
        .signal-bullish {
            background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.2rem 0;
        }
        
        .signal-bearish {
            background: linear-gradient(90deg, #ff4444 0%, #cc3333 100%);
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.2rem 0;
        }
        
        .api-status-active {
            color: #00ff88;
        }
        
        .api-status-inactive {
            color: #ff4444;
        }
        
        .news-high { border-left: 4px solid #ff4444; }
        .news-medium { border-left: 4px solid #ffaa00; }
        .news-low { border-left: 4px solid #00ff88; }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Smart Money Forex Analyzer Pro</h1>
            <p>Análise Institucional Avançada com APIs Gratuitas</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializar dashboard
        dashboard = ForexDashboard()
        
        # Executar aplicação
        dashboard.run()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>⚠️ <strong>Aviso:</strong> Esta ferramenta é apenas para fins educacionais. Trading envolve riscos significativos.</p>
            <p>📚 Baseado em Smart Money Concepts + Metodologia Wyckoff | 🔧 APIs 100% Gratuitas</p>
            <p>💡 <em>Desenvolvido para traders que buscam análise institucional avançada</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Erro na aplicação: {str(e)}")
        st.info("🔄 Recarregue a página ou verifique os logs para mais detalhes.")
        
        # Mostrar detalhes do erro para debug
        with st.expander("🐛 Detalhes do Erro (Debug)"):
            st.code(str(e))
            st.write("**Traceback:**")
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()