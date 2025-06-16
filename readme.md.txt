# 🚀 Smart Money Forex Analyzer Pro

Uma aplicação avançada de análise institucional forex baseada em **Smart Money Concepts** e **Metodologia Wyckoff**, utilizando exclusivamente **APIs gratuitas**.

## ✨ Recursos Principais

### 📊 Análise Smart Money
- **Fair Value Gaps (FVGs)**: Identificação automática de desequilíbrios de preço
- **Order Blocks (OBs)**: Detecção de zonas institucionais de demanda/oferta
- **Market Structure Shifts (MSS)**: Análise de mudanças na estrutura de mercado
- **Change of Character (ChoCh)**: Identificação de mudanças de caráter do mercado
- **Liquidity Zones**: Mapeamento de zonas de liquidez (Equal Highs/Lows)

### 📈 Recursos Avançados
- **Análise de Confluência**: Identificação de sinais convergentes
- **Bias de Mercado**: Determinação automática da direção institucional
- **Calendário Econômico**: Notícias e eventos em tempo real
- **Correlações**: Análise de correlação com criptomoedas
- **Gestão de Risco**: Calculadora de posição integrada
- **TradingView Integration**: Widget integrado para análise adicional

### 🆓 APIs Gratuitas Integradas
- **Frankfurter**: Taxas forex em tempo real (sem API key)
- **ExchangeRate-API**: Backup para dados forex
- **FreeForexAPI**: Dados forex alternativos
- **NewsAPI**: Notícias econômicas (100 req/dia gratuitas)
- **MarketAux**: Calendário econômico (100 req/dia)
- **CoinGecko**: Dados de criptomoedas (ilimitado)
- **Alpha Vantage**: Dados históricos (5 req/min gratuitas)

## 🎯 Para Quem é Esta Aplicação

- **Traders Forex** que utilizam análise institucional
- **Estudantes** de Smart Money Concepts
- **Analistas** que buscam automação na identificação de padrões
- **Desenvolvedores** interessados em análise técnica avançada

## 🚀 Instalação e Execução

### Pré-requisitos
```bash
Python 3.8+
pip (gerenciador de pacotes Python)
```

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/smart-money-forex-analyzer-pro.git
cd smart-money-forex-analyzer-pro
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Execute a Aplicação
```bash
streamlit run main.py
```

### 4. Acesse no Navegador
```
http://localhost:8501
```

## 📁 Estrutura do Projeto

```
smart-money-forex-analyzer-pro/
├── main.py                    # Aplicação principal
├── requirements.txt           # Dependências
├── README.md                 # Documentação
├── config/
│   └── settings.py           # Configurações centralizadas
├── api/
│   └── manager.py            # Gerenciador de APIs
├── analysis/
│   └── smart_money.py        # Análise Smart Money
├── ui/
│   └── dashboard.py          # Interface do usuário
├── utils/
│   └── helpers.py            # Funções utilitárias
└── tests/
    └── test_*.py             # Testes unitários
```

## 🔧 Configuração

### Modo Demo (Padrão)
A aplicação funciona imediatamente no **Modo Demo** com dados simulados realistas, sem necessidade de configuração.

### APIs Opcionais (Para Dados Premium)
Para dados reais, configure as seguintes API keys gratuitas:

#### NewsAPI (100 requests/dia)
1. Acesse: https://newsapi.org/
2. Registre-se gratuitamente
3. Copie sua API key
4. Configure na barra lateral da aplicação

#### Alpha Vantage (5 requests/min)
1. Acesse: https://www.alphavantage.co/
2. Obtenha API key gratuita
3. Configure na aplicação

#### MarketAux (100 requests/dia)
1. Acesse: https://www.marketaux.com/
2. Registre-se para API gratuita
3. Configure na aplicação

### Variáveis de Ambiente (Opcional)
```bash
# .env
NEWSAPI_KEY=sua_chave_newsapi
ALPHA_VANTAGE_KEY=sua_chave_alphavantage
MARKETAUX_KEY=sua_chave_marketaux
DEBUG=False
LOG_LEVEL=INFO
```

## 📚 Como Usar

### 1. Primeira Execução
- Execute a aplicação
- Leia a mensagem de boas-vindas
- Clique em "🚀 Começar Análise"

### 2. Configuração Básica
- **Par de Moedas**: Selecione o par forex (ex: EUR/USD)
- **Timeframe**: Escolha o intervalo (ex: 15m)
- **Dados Históricos**: Defina quantidade de velas (100-1000)

### 3. Configurações Avançadas
- **Força Mínima**: Filtre sinais por força (0-100%)
- **Confluência**: Ative análise de confluência
- **Liquidez**: Ative análise de zonas de liquidez
- **Modo Demo**: Use dados simulados

### 4. Executar Análise
- Clique em "🚀 Executar Análise"
- Aguarde o processamento
- Analise os resultados

### 5. Interpretação dos Resultados

#### Sinais Smart Money
- 🟢 **FVG Bullish**: Gap de alta para ser preenchido
- 🔴 **FVG Bearish**: Gap de baixa para ser preenchido
- 🔵 **OB Bullish**: Zona de demanda institucional
- 🟠 **OB Bearish**: Zona de oferta institucional
- 💎 **MSS**: Mudança confirmada na estrutura
- ⚡ **ChoCh**: Mudança de caráter do mercado

#### Força dos Sinais
- ⭐ (0-20%): Muito Fraco
- ⭐⭐ (20-40%): Fraco
- ⭐⭐⭐ (40-60%): Moderado
- ⭐⭐⭐⭐ (60-80%): Forte
- ⭐⭐⭐⭐⭐ (80-100%): Muito Forte

#### Bias do Mercado
- 📈 **BULLISH**: Predominância de sinais de alta
- 📉 **BEARISH**: Predominância de sinais de baixa
- ⚖️ **NEUTRAL**: Sinais equilibrados

## 🔬 Metodologia

### Smart Money Concepts
A aplicação implementa os conceitos fundamentais da análise institucional:

1. **Fair Value Gaps**: Áreas onde o preço se moveu rapidamente, deixando um "gap" que tende a ser preenchido
2. **Order Blocks**: Últimas velas antes de um movimento impulsivo, indicando onde instituições colocaram ordens
3. **Market Structure**: Análise de Higher Highs/Lower Lows para determinar tendência
4. **Liquidity Zones**: Áreas onde stops de varejo estão acumulados (Equal Highs/Lows)

### Metodologia Wyckoff
Integração dos princípios de Richard Wyckoff:

1. **Lei da Oferta e Demanda**
2. **Lei da Causa e Efeito**
3. **Lei do Esforço vs Resultado**

### Algoritmos de Detecção

#### Fair Value Gaps
```python
# Condições para FVG Bullish:
# 1. Low da vela[i-2] > High da vela[i]
# 2. Vela do meio é impulso bullish
# 3. Gap >= tamanho mínimo em pips
```

#### Order Blocks
```python
# Condições para OB Bullish:
# 1. Vela bearish (institucional)
# 2. Movimento bullish significativo após
# 3. Volume acima da média (se disponível)
```

#### Market Structure Shifts
```python
# Condições para MSS Bullish:
# 1. Novo Higher High confirmado
# 2. Quebra de estrutura anterior
# 3. Movimento >= tamanho mínimo
```

## 📊 Exemplos de Uso

### Cenário 1: Identificação de FVG
```
1. Execute análise no EUR/USD 15m
2. Identifique FVG Bullish em 1.0850
3. Aguarde retorno do preço à zona
4. Entre long com stop abaixo do FVG
5. Target baseado em próxima resistência
```

### Cenário 2: Trade com Order Block
```
1. Identifique OB Bearish em resistência
2. Aguarde teste da zona OB
3. Confirme rejeição com padrão de velas
4. Entre short com stop acima do OB
5. Target em próximo suporte
```

### Cenário 3: MSS + Confluência
```
1. MSS Bullish quebra estrutura bearish
2. FVG Bullish na mesma região
3. Confluência de 2+ sinais fortes
4. Alta probabilidade de movimento bullish
5. Gestão de risco 1:2 ou 1:3
```

## ⚠️ Gestão de Risco

### Princípios Fundamentais
- **Nunca arrisque mais de 1-2% do capital por trade**
- **Use sempre stop loss baseado em invalidação**
- **Mantenha ratio mínimo de 1:2 (Risk:Reward)**
- **Diversifique entre diferentes pares**

### Calculadora Integrada
A aplicação inclui calculadora automática de:
- Tamanho da posição baseado em % de risco
- Níveis de stop loss baseados em ATR
- Targets baseados em estrutura de mercado
- Risk:Reward ratio automático

## 🔍 Troubleshooting

### Problemas Comuns

#### Erro ao Iniciar
```bash
# Verifique a versão do Python
python --version  # Deve ser 3.8+

# Reinstale dependências
pip install -r requirements.txt --upgrade
```

#### APIs Não Funcionam
```bash
# Verifique conexão internet
ping google.com

# Teste no modo demo primeiro
# Verifique se API keys estão corretas
# Consulte logs para erros específicos
```

#### Gráfico Não Carrega
```bash
# Limpe cache do navegador
# Verifique se porta 8501 está livre
# Reinicie a aplicação
```

#### Performance Lenta
```bash
# Reduza quantidade de dados históricos
# Use timeframes maiores (1h, 4h)
# Feche outras aplicações pesadas
```

### Logs de Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Recursos Avançados

### Personalização de Parâmetros
Edite `config/settings.py` para customizar:
- Tamanhos mínimos de FVG/OB
- Períodos de lookback para MSS
- Tolerâncias para liquidez
- Cores e estilos do gráfico

### Extensões Disponíveis
- **Multi-timeframe**: Análise em múltiplos timeframes
- **Alerts**: Sistema de alertas por email/webhook
- **Backtesting**: Teste histórico de estratégias
- **Portfolio**: Análise de múltiplos pares

### API Externa
A aplicação pode ser estendida para fornecer API REST:
```python
# Exemplo de endpoint
GET /api/analyze/{pair}/{timeframe}
Response: {
  "signals": [...],
  "bias": "BULLISH",
  "confidence": 75.5
}
```

## 🤝 Contribuição

### Como Contribuir
1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** suas modificações
4. **Teste** thoroughly
5. **Submeta** pull request

### Áreas de Contribuição
- 🐛 **Bug fixes**
- ✨ **Novas features**
- 📚 **Documentação**
- 🧪 **Testes**
- 🎨 **Interface**

### Guidelines
- Siga PEP 8 para código Python
- Documente todas as funções
- Inclua testes para novas features
- Use type hints quando possível

## 📝 Roadmap

### Versão 2.1 (Próxima)
- [ ] **Multi-timeframe analysis**
- [ ] **Alert system**
- [ ] **Strategy backtesting**
- [ ] **Export de dados**

### Versão 2.2
- [ ] **Machine learning integration**
- [ ] **Portfolio analysis**
- [ ] **Mobile responsiveness**
- [ ] **Dark/Light theme**

### Versão 3.0
- [ ] **Real-time streaming**
- [ ] **Advanced order types**
- [ ] **Social features**
- [ ] **Mobile app**

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Disclaimer

**IMPORTANTE**: Esta ferramenta é destinada apenas para fins **educacionais e informativos**. 

- ❌ **NÃO** é aconselhamento financeiro
- ❌ **NÃO** garante lucros
- ❌ **NÃO** substitui análise profissional
- ✅ **SIM** é ferramenta de apoio à decisão
- ✅ **SIM** pode ser usada para aprendizado

### Riscos do Trading
- **Alto risco de perda**: Você pode perder todo seu capital
- **Volatilidade**: Mercados forex são altamente voláteis
- **Alavancagem**: Pode amplificar tanto lucros quanto perdas
- **Fatores externos**: Notícias e eventos podem impactar drasticamente

### Recomendações
- 📚 **Estude** Smart Money Concepts profundamente
- 🧪 **Pratique** em conta demo primeiro
- 💰 **Invista** apenas o que pode perder
- 🎓 **Busque** educação financeira contínua
- 👨‍💼 **Consulte** profissionais qualificados

## 📞 Suporte

### Canais de Suporte
- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/smart-money-forex-analyzer-pro/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/smart-money-forex-analyzer-pro/discussions)
- 📧 **Email**: suporte@smartmoney-analyzer.com
- 📱 **Telegram**: @SmartMoneyAnalyzer

### FAQ

**Q: A aplicação funciona sem API keys?**
A: Sim! Funciona perfeitamente no modo demo com dados simulados realistas.

**Q: Posso usar para trading real?**
A: A ferramenta fornece análise, mas a decisão de trading é sempre sua. Use com gestão de risco adequada.

**Q: Como interpretar a força dos sinais?**
A: 0-40% (Fraco), 40-60% (Moderado), 60-80% (Forte), 80-100% (Muito Forte).

**Q: Qual o melhor timeframe para iniciantes?**
A: Recomendamos 15m ou 1h para começar, pois oferecem bom equilíbrio entre sinais e ruído.

**Q: A aplicação funciona para outros mercados?**
A: Atualmente focada em forex, mas os conceitos podem ser aplicados a outros mercados.

## 🙏 Agradecimentos

### Inspirações e Referências
- **ICT (Inner Circle Trader)**: Conceitos Smart Money
- **Richard Wyckoff**: Metodologia de análise institucional
- **Comunidade Forex**: Feedback e sugestões
- **Desenvolvedores Open Source**: Bibliotecas utilizadas

### Tecnologias Utilizadas
- **Streamlit**: Framework web
- **Plotly**: Visualizações interativas
- **Pandas/NumPy**: Manipulação de dados
- **APIs Gratuitas**: Dados de mercado

---

**🚀 Desenvolvido com ❤️ para a comunidade de traders que buscam análise institucional de qualidade**

---

*Última atualização: Janeiro 2025*
*Versão: 2.0.0*