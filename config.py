import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TradingConfig:
    """Configuration class for trading parameters"""
    # API Credentials
    api_key: str
    username: str
    password: str
    totp_token: str
    
    # Trading Parameters
    margin_limit: float = 7500
    quantity_limit: int = 1000
    price_multiple: float = 1.0
    
    # Risk Management
    stop_loss_percentage: float = 0.92
    profit_target_percentage: float = 1.03
    higher_profit_target: float = 1.05
    max_profit_target: float = 1.12
    
    # Trailing Stop Parameters
    trailing_stop_percentage: float = 0.975
    higher_trailing_stop: float = 0.965
    max_trailing_stop: float = 0.955

@dataclass
class SymbolConfig:
    """Configuration for trading symbols"""
    live_symbol: str
    live_token: str
    live_exchange: str
    options_exchange: str
    base_symbol: str
    expiry_code: str
    strike_code: str

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables or use defaults"""
    return {
        'trading': TradingConfig(
            api_key=os.getenv('API_KEY', 'uQBIgMGv'),
            username=os.getenv('USERNAME', 'S692948'),
            password=os.getenv('PASSWORD', '5472'),
            totp_token=os.getenv('TOTP_TOKEN', 'CESGV6Z4HHXCIZHQPL3CUFK6ZU'),
            margin_limit=float(os.getenv('MARGIN_LIMIT', '7500')),
            quantity_limit=int(os.getenv('QUANTITY_LIMIT', '1000')),
            price_multiple=float(os.getenv('PRICE_MULTIPLE', '1.0')),
            stop_loss_percentage=float(os.getenv('STOP_LOSS_PERCENTAGE', '0.92')),
            profit_target_percentage=float(os.getenv('PROFIT_TARGET_PERCENTAGE', '1.03')),
            higher_profit_target=float(os.getenv('HIGHER_PROFIT_TARGET', '1.05')),
            max_profit_target=float(os.getenv('MAX_PROFIT_TARGET', '1.12')),
            trailing_stop_percentage=float(os.getenv('TRAILING_STOP_PERCENTAGE', '0.975')),
            higher_trailing_stop=float(os.getenv('HIGHER_TRAILING_STOP', '0.965')),
            max_trailing_stop=float(os.getenv('MAX_TRAILING_STOP', '0.955'))
        ),
        'symbol': SymbolConfig(
            live_symbol=os.getenv('LIVE_SYMBOL', 'NIFTY'),
            live_token=os.getenv('LIVE_TOKEN', '99926000'),
            live_exchange=os.getenv('LIVE_EXCHANGE', 'NSE'),
            options_exchange=os.getenv('OPTIONS_EXCHANGE', 'NFO'),
            base_symbol=os.getenv('BASE_SYMBOL', 'NIFTY'),
            expiry_code=os.getenv('EXPIRY_CODE', '17'),
            strike_code=os.getenv('STRIKE_CODE', 'JUL25')
        )
    } 