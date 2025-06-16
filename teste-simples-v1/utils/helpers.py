"""
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
