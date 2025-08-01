import os
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import math
import time as time_module
from contextlib import contextmanager

import requests
import pyotp
import pandas as pd
from SmartApi.smartConnect import SmartConnect


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """Configuration class for trading parameters"""
    api_key: str = ''
    username: str = ''
    pwd: str = ''
    totp_token: str = ''
    margin_limit: float = 7500
    quantity_limit: int = 1000
    price_multiple: float = 1.0
    stop_loss_percentage: float = 0.6
    profit_target_percentage: float = 1.1
    higher_profit_target: float = 1.2
    max_profit_target: float = 1.3
    trailing_stop_percentage: float = 0.93
    higher_trailing_stop: float = 0.87
    max_trailing_stop: float = 0.85

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

class TimeManager:
    """Manages trading time windows"""
    
    def __init__(self):
        self.trading_times = self._create_trading_times()
    
    def _create_trading_times(self) -> List[str]:
        """Create list of trading times"""
        times = []
        # Morning session
        for hour in range(9, 12):
            for minute in range(0, 60, 5):
                if hour == 9 and minute <= 50:
                    continue
                times.append(f"{hour:02d}:{minute:02d}:00")
        
        # Afternoon session
        for hour in range(12, 14):
            for minute in range(0, 60, 1):
                if hour == 14 and minute < 20:
                    break
                times.append(f"{hour:02d}:{minute:02d}:00")
        
        return times
    
    def is_trading_time(self, current_time: str) -> bool:
        """Check if current time is a trading time"""
        return current_time in self.trading_times

class TokenManager:
    """Manages token data and symbol lookups"""
    
    def __init__(self):
        self.token_df = None
        self._load_token_data()
    
    def _load_token_data(self):
        """Load token data from API"""
        try:
            url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.token_df = pd.DataFrame.from_dict(data)
            self.token_df['expiry'] = pd.to_datetime(self.token_df['expiry'])
            self.token_df = self.token_df.astype({'strike': float})
            
            logger.info(f"Loaded {len(self.token_df)} token records")
        except Exception as e:
            logger.error(f"Failed to load token data: {e}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get token and lot size for a symbol"""
        try:
            if self.token_df is None:
                return None
            result = self.token_df[self.token_df['symbol'] == symbol]
            if result.empty:
                return None
            
            return {
                'token': result.iloc[0]['token'],
                'lotsize': int(result.iloc[0]['lotsize'])
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, config: TradingConfig, symbol_config: SymbolConfig):
        self.config = config
        self.symbol_config = symbol_config
        self.time_manager = TimeManager()
        self.token_manager = TokenManager()
        self.smart_api = SmartConnect(config.api_key)
        self.current_position = None
        
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize SmartAPI connection"""
        try:
            token = self.config.totp_token
            totp = pyotp.TOTP(token).now()
        except Exception as e:
            logger.error("Invalid Token: The provided token is not valid.")
            raise e

        correlation_id = "abcde"
        self.smart_api = SmartConnect(self.config.api_key)
        data = self.smart_api.generateSession(self.config.username, self.config.pwd, totp)
        
        if not data.get('status', False):
            logger.error('Failed to generate session')
            raise Exception("API session generation failed")
        else:
            authToken = data['data']['jwtToken']
            refreshToken = data['data']['refreshToken']
            feedToken = self.smart_api.getfeedToken()
            logger.info(f"Feed-Token: {feedToken}")
            
            res = self.smart_api.getProfile(refreshToken)
            logger.info(f"Get Profile: {res}")
            
            self.smart_api.generateToken(refreshToken)
            res = res['data']['exchanges']
            logger.info("API initialization completed successfully")
    
    def get_ltp_data(self, exchange: str, symbol: str, token: str) -> Optional[float]:
        """Get LTP data with error handling"""
        try:
            if self.smart_api is None:
                return None
            ltp_data = self.smart_api.ltpData(exchange, symbol, token)
            if isinstance(ltp_data, dict) and 'data' in ltp_data:
                return float(ltp_data['data']['ltp'])
            else:
                logger.error(f"Unexpected LTP data format: {ltp_data}")
                return None
        except Exception as e:
            logger.error(f"Error getting LTP for {symbol}: {e}")
            return None
    
    
    def get_ltp_data_with_retry(self, exchange: str, symbol: str, token: str, retries: int = 3) -> Optional[float]:
        """Get LTP data with retry mechanism"""
        for _ in range(retries):
            ltp = self.get_ltp_data(exchange, symbol, token)
            if ltp is not None:
                return ltp
            time_module.sleep(1)
        return None
    def get_live_price(self) -> Optional[float]:
        """Get live price for the underlying"""
        ltp = self.get_ltp_data(
            self.symbol_config.live_exchange,
            self.symbol_config.live_symbol,
            self.symbol_config.live_token
        )
        
        if ltp is not None:
            # Round to nearest multiple
            return round(ltp / self.config.price_multiple) * self.config.price_multiple
        return None
    
    def create_option_symbols(self, strike_price: float) -> Tuple[str, str]:
        """Create CE and PE option symbols"""
        strike_price = livedata = round(strike_price/100)*100
        ce_symbol = f"{self.symbol_config.base_symbol}{self.symbol_config.expiry_code}{self.symbol_config.strike_code}{int(strike_price)}CE"
        pe_symbol = f"{self.symbol_config.base_symbol}{self.symbol_config.expiry_code}{self.symbol_config.strike_code}{int(strike_price)}PE"

       
        
        return ce_symbol, pe_symbol
    
    def select_better_option(self, ce_symbol: str, pe_symbol: str) -> Tuple[str, Dict]:
        """Select the better option based on LTP comparison"""
        ce_info = self.token_manager.get_symbol_info(ce_symbol)
        pe_info = self.token_manager.get_symbol_info(pe_symbol)
        
        if not ce_info or not pe_info:
            raise Exception("Could not get symbol information")
        
        ce_ltp = self.get_ltp_data(
            self.symbol_config.options_exchange, 
            ce_symbol, 
            ce_info['token']
        )
        pe_ltp = self.get_ltp_data(
            self.symbol_config.options_exchange, 
            pe_symbol, 
            pe_info['token']
        )
        
        if ce_ltp is None or pe_ltp is None:
            raise Exception("Could not get LTP data for options")
        
        # Select the option with lower premium
        if ce_ltp >= pe_ltp:
            return pe_symbol, pe_info
        else:
            return ce_symbol, ce_info
    
    def calculate_quantity(self, ltp: float, lot_size: int) -> int:
        """Calculate optimal quantity based on margin"""
        quantity = 0
        i = 1
        
        while True:
            potential_quantity = lot_size * i
            if (potential_quantity * ltp < self.config.margin_limit and 
                potential_quantity < self.config.quantity_limit):
                quantity = potential_quantity
                i += 1
            else:
                break
        
        return quantity
    
    def place_order(self, order_params: Dict) -> Optional[str]:
        """Place order with error handling"""
        try:
            if self.smart_api is None:
                return None
            order_id = self.smart_api.placeOrder(order_params)
            logger.info(f"Order placed successfully: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            
            return None
    
    def place_buy_order(self, symbol: str, token: str, ltp: float, quantity: int) -> bool:
        """Place buy order"""
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "BUY",
            "exchange": self.symbol_config.options_exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str(ltp),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        
        order_id = self.place_order(order_params)
        if order_id:
            self.current_position = {
                'symbol': symbol,
                'token': token,
                'buy_price': ltp,
                'quantity': quantity,
                'order_id': order_id,
                'trigger_price': 0
            }
            logger.info(f"Buy order placed: {symbol} at {ltp}, Qty: {quantity}")
            return True
        return False
    
    def place_sell_order(self, symbol: str, token: str, ltp: float, quantity: int) -> bool:
        """Place sell order"""
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "SELL",
            "exchange": self.symbol_config.options_exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str(ltp),
            "squareoff": "0",
            "quantity": str(quantity)
        }
        
        order_id = self.place_order(order_params)
        if order_id:
            logger.info(f"Sell order placed: {symbol} at {ltp}, Qty: {quantity}")
            self.current_position = None
            return True
        return False
    
    def should_sell(self, current_ltp: float, buy_price: float) -> Tuple[bool, str]:
        """Determine if position should be sold"""
        # Stop loss check
        if current_ltp < buy_price * self.config.stop_loss_percentage:
            return True, "stop_loss"
        
        # Profit target checks
        profit_target = buy_price * self.config.profit_target_percentage
        higher_target = buy_price * self.config.higher_profit_target
        max_target = buy_price * self.config.max_profit_target
        
        if current_ltp > profit_target and self.current_position is not None:
            # Update trailing stop
            new_trigger = self._calculate_trailing_stop(current_ltp, buy_price)
            if new_trigger > self.current_position['trigger_price']:
                self.current_position['trigger_price'] = new_trigger
                logger.info(f"Updated trigger price to: {new_trigger}")
        
        # Check if price hit trigger
        if (self.current_position is not None and 
            self.current_position['trigger_price'] > 0 and 
            current_ltp < self.current_position['trigger_price']):
            return True, "trailing_stop"
        
        return False, ""
    
    def _calculate_trailing_stop(self, current_ltp: float, buy_price: float) -> float:
        """Calculate trailing stop price"""
        if current_ltp > buy_price * self.config.max_profit_target:
            return math.ceil(current_ltp * self.config.max_trailing_stop * 10) / 10
        elif current_ltp > buy_price * self.config.higher_profit_target:
            return math.ceil(current_ltp * self.config.higher_trailing_stop * 10) / 10
        else:
            return math.ceil(current_ltp * self.config.trailing_stop_percentage * 10) / 10
    
    def execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            # Get live price
            live_price = self.get_live_price()
            if live_price is None:
                logger.warning("Could not get live price")
                return
            
            # Create option symbols
            ce_symbol, pe_symbol = self.create_option_symbols(live_price)
            
            # Select better option
            selected_symbol, symbol_info = self.select_better_option(ce_symbol, pe_symbol)
            
            # Get current LTP
            current_ltp = self.get_ltp_data(
                self.symbol_config.options_exchange,
                selected_symbol,
                symbol_info['token']
            )
            
            if current_ltp is None:
                logger.warning("Could not get option LTP")
                return
            
            # Calculate quantity
            quantity = self.calculate_quantity(current_ltp, symbol_info['lotsize'])
            
            if quantity == 0:
                logger.warning("Insufficient margin for minimum quantity")
                return
            
            # Place buy order
            if self.place_buy_order(selected_symbol, symbol_info['token'], current_ltp, quantity):
                # Monitor position
                self._monitor_position(selected_symbol, symbol_info['token'], quantity)
            
        except Exception as e:
            
            logger.error(f"Error in trading cycle: {e}")
    
    def _monitor_position(self, symbol: str, token: str, quantity: int):
        """Monitor position for exit conditions"""
        logger.info("Starting position monitoring...")
        
        while self.current_position:
            try:
                current_ltp = self.get_ltp_data(
                    self.symbol_config.options_exchange,
                    symbol,
                    token
                )
                
                if current_ltp is None:
                    logger.warning("Could not get LTP for monitoring")
                    time_module.sleep(0.1)
                    
                    continue
                
                should_sell, reason = self.should_sell(current_ltp, self.current_position['buy_price'])
                
                if should_sell:
                    if self.place_sell_order(symbol, token, current_ltp, quantity):
                        logger.info(f"Position closed due to {reason}")
                        break
                
                time_module.sleep(0.1)  # Wait before next check
                
            except Exception as e:
                logger.error(f"Error in position monitoring: {e}")
                time_module.sleep(0.1)
    
    def run(self):
        """Main trading loop"""
        logger.info("Starting trading bot...")
        
        while True:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Check if it's trading time
                if self.time_manager.is_trading_time(current_time):
                    logger.info(f"Trading time: {current_time}")
                    
                    # Only trade if no current position
                    if not self.current_position:
                        self.execute_trading_cycle()
                    else:
                        logger.info("Position already open, skipping new trade")
                
                # Sleep for a short interval
                time_module.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Trading bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time_module.sleep(0.1)

def main():
    """Main function"""
    # Load configuration from environment variables or config file
    config = TradingConfig(
        api_key = 'uQBIgMGv',
        username = 'S692948',
        pwd = '5472',
        totp_token=os.getenv('TOTP_TOKEN', 'CESGV6Z4HHXCIZHQPL3CUFK6ZU')
    )
    
    symbol_config = SymbolConfig(
        live_symbol="SENSEX",
        live_token="99919000",
        live_exchange="BSE",
        options_exchange="BFO",
        base_symbol="SENSEX",
        expiry_code="25JUL",
        strike_code=""
    )
    
    # Create and run trading bot
    bot = TradingBot(config, symbol_config)
    bot.run()

if __name__ == "__main__":
    main() 

if __name__ == "__main__":
    main() 