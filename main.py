import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.dashboard import ForexDashboard
from config.settings import AppConfig
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

def main():
    """Função principal da aplicação"""
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

if __name__ == "__main__":
    main()