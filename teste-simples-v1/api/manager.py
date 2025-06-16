"""
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
