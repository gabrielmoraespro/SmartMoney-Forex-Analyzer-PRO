"""
Setup script para Smart Money Forex Analyzer Pro
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Cria estrutura de diretórios necessária"""
    
    directories = [
        'api',
        'config', 
        'analysis',
        'ui',
        'utils',
        'tests',
        'data',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
        # Criar __init__.py em cada diretório Python
        if directory not in ['data', 'logs', 'tests']:
            init_file = Path(directory) / '__init__.py'
            if not init_file.exists():
                init_file.write_text(f'"""\nMódulo {directory} para Smart Money Forex Analyzer Pro\n"""\n')
    
    print("✅ Estrutura de diretórios criada com sucesso!")

def check_python_version():
    """Verifica versão do Python"""
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_requirements():
    """Instala dependências"""
    
    try:
        import subprocess
        
        print("📦 Instalando dependências...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
            return True
        else:
            print("❌ Erro ao instalar dependências:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def create_env_template():
    """Cria template de arquivo .env"""
    
    env_template = """# Smart Money Forex Analyzer Pro - Configurações

# APIs Opcionais (deixe vazio para usar modo demo)
NEWSAPI_KEY=
ALPHA_VANTAGE_KEY=
MARKETAUX_KEY=

# Configurações de Debug
DEBUG=False
LOG_LEVEL=INFO

# Configurações de Cache
CACHE_ENABLED=True
CACHE_TTL=300
"""
    
    env_file = Path('.env.example')
    env_file.write_text(env_template)
    
    print("✅ Arquivo .env.example criado!")
    print("💡 Copie para .env e configure suas API keys opcionais")

def main():
    """Função principal de setup"""
    
    print("🚀 Smart Money Forex Analyzer Pro - Setup")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        return
    
    # Criar estrutura
    create_directory_structure()
    
    # Instalar dependências
    if not install_requirements():
        print("⚠️ Continuando sem instalar dependências...")
    
    # Criar template de configuração
    create_env_template()
    
    print("\n🎉 Setup concluído!")
    print("\n📋 Próximos passos:")
    print("1. Execute: streamlit run main.py")
    print("2. Acesse: http://localhost:8501")
    print("3. Configure APIs opcionais na interface")
    print("\n⚠️ A aplicação funciona sem API keys no modo demo!")

if __name__ == "__main__":
    main()