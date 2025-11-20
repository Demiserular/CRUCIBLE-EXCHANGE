"""
Sample Data Generator for FIX Exchange

Generates realistic trading scenarios and sample data for testing and demonstration.
"""

import random
import time
import sys
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fix_engine import FIXEngine


class SampleDataGenerator:
    """Generate sample trading data for testing and demonstration."""
    
    SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "BAC", "WMT"]
    
    COMPANY_NAMES = {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "MSFT": "Microsoft Corporation",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "META": "Meta Platforms Inc.",
        "NVDA": "NVIDIA Corporation",
        "JPM": "JPMorgan Chase & Co.",
        "BAC": "Bank of America Corp.",
        "WMT": "Walmart Inc."
    }
    
    BASE_PRICES = {
        "AAPL": 185.00,
        "GOOGL": 140.00,
        "MSFT": 380.00,
        "AMZN": 175.00,
        "TSLA": 245.00,
        "META": 485.00,
        "NVDA": 495.00,
        "JPM": 195.00,
        "BAC": 34.00,
        "WMT": 165.00
    }
    
    def __init__(self):
        self.current_prices = self.BASE_PRICES.copy()
        self.order_id_counter = 1
    
    def generate_price_movement(self, symbol: str) -> float:
        """Generate realistic price movement for a symbol."""
        current_price = self.current_prices[symbol]
        # Random walk with small percentage changes
        change_percent = random.uniform(-0.02, 0.02)  # -2% to +2%
        new_price = current_price * (1 + change_percent)
        self.current_prices[symbol] = round(new_price, 2)
        return new_price
    
    def generate_order(
        self,
        symbol: str = None,
        side: str = None,
        order_type: str = None,
        qty: int = None
    ) -> Dict:
        """
        Generate a random order.
        
        Returns:
            Dictionary with order details
        """
        if symbol is None:
            symbol = random.choice(self.SYMBOLS)
        
        if side is None:
            side = random.choice([FIXEngine.SIDE_BUY, FIXEngine.SIDE_SELL])
        
        if order_type is None:
            order_type = random.choice([FIXEngine.ORDER_TYPE_MARKET, FIXEngine.ORDER_TYPE_LIMIT])
        
        if qty is None:
            qty = random.choice([10, 25, 50, 75, 100, 150, 200, 500])
        
        cl_ord_id = f"SAMPLE{self.order_id_counter:06d}"
        self.order_id_counter += 1
        
        order = {
            "cl_ord_id": cl_ord_id,
            "symbol": symbol,
            "side": side,
            "side_name": "BUY" if side == "1" else "SELL",
            "order_qty": qty,
            "order_type": order_type,
            "type_name": "MARKET" if order_type == "1" else "LIMIT"
        }
        
        if order_type == FIXEngine.ORDER_TYPE_LIMIT:
            base_price = self.current_prices[symbol]
            # Add some spread around current price
            if side == FIXEngine.SIDE_BUY:
                # Buy orders slightly below market
                order["price"] = round(base_price * random.uniform(0.98, 1.00), 2)
            else:
                # Sell orders slightly above market
                order["price"] = round(base_price * random.uniform(1.00, 1.02), 2)
        else:
            order["price"] = None
        
        return order
    
    def generate_trading_session(self, num_orders: int = 20) -> List[Dict]:
        """
        Generate a complete trading session with multiple orders.
        
        Args:
            num_orders: Number of orders to generate
            
        Returns:
            List of order dictionaries
        """
        orders = []
        
        for _ in range(num_orders):
            # Update prices slightly
            for symbol in self.SYMBOLS:
                self.generate_price_movement(symbol)
            
            order = self.generate_order()
            orders.append(order)
        
        return orders
    
    def generate_matching_pair(self, symbol: str = None) -> tuple[Dict, Dict]:
        """
        Generate a pair of orders that should match.
        
        Returns:
            Tuple of (buy_order, sell_order)
        """
        if symbol is None:
            symbol = random.choice(self.SYMBOLS)
        
        qty = random.choice([50, 100, 150, 200])
        price = round(self.current_prices[symbol], 2)
        
        buy_order = self.generate_order(
            symbol=symbol,
            side=FIXEngine.SIDE_BUY,
            order_type=FIXEngine.ORDER_TYPE_LIMIT,
            qty=qty
        )
        buy_order["price"] = price
        
        sell_order = self.generate_order(
            symbol=symbol,
            side=FIXEngine.SIDE_SELL,
            order_type=FIXEngine.ORDER_TYPE_LIMIT,
            qty=qty
        )
        sell_order["price"] = price
        
        return buy_order, sell_order
    
    def generate_market_data(self) -> List[Dict]:
        """
        Generate current market data for all symbols.
        
        Returns:
            List of market data dictionaries
        """
        market_data = []
        
        for symbol in self.SYMBOLS:
            price = self.current_prices[symbol]
            prev_close = self.BASE_PRICES[symbol]
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            market_data.append({
                "symbol": symbol,
                "name": self.COMPANY_NAMES[symbol],
                "price": price,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": random.randint(100000, 10000000),
                "bid": round(price - 0.05, 2),
                "ask": round(price + 0.05, 2),
                "high": round(price * 1.02, 2),
                "low": round(price * 0.98, 2)
            })
        
        return market_data
    
    def generate_portfolio(self, num_positions: int = 5) -> List[Dict]:
        """
        Generate a sample portfolio.
        
        Returns:
            List of position dictionaries
        """
        portfolio = []
        symbols = random.sample(self.SYMBOLS, min(num_positions, len(self.SYMBOLS)))
        
        for symbol in symbols:
            qty = random.choice([100, 200, 300, 500, 1000])
            avg_price = round(self.BASE_PRICES[symbol] * random.uniform(0.95, 1.05), 2)
            current_price = self.current_prices[symbol]
            
            market_value = qty * current_price
            cost_basis = qty * avg_price
            pnl = market_value - cost_basis
            pnl_percent = (pnl / cost_basis) * 100
            
            portfolio.append({
                "symbol": symbol,
                "name": self.COMPANY_NAMES[symbol],
                "quantity": qty,
                "avg_price": avg_price,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "cost_basis": round(cost_basis, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
        
        return portfolio


def main():
    """Demonstrate sample data generation."""
    print("="*60)
    print("FIX Exchange Sample Data Generator")
    print("="*60)
    print()
    
    generator = SampleDataGenerator()
    
    # Generate market data
    print("📊 Current Market Data:")
    print("-"*60)
    market_data = generator.generate_market_data()
    for stock in market_data[:5]:  # Show first 5
        print(f"{stock['symbol']:6} {stock['name']:25} ${stock['price']:7.2f} "
              f"({stock['change_percent']:+.2f}%)")
    print()
    
    # Generate sample orders
    print("📝 Sample Orders:")
    print("-"*60)
    orders = generator.generate_trading_session(5)
    for order in orders:
        price_str = f"@ ${order['price']:.2f}" if order['price'] else "@ MARKET"
        print(f"{order['cl_ord_id']} | {order['side_name']:4} {order['order_qty']:3} "
              f"{order['symbol']:6} {price_str}")
    print()
    
    # Generate matching pair
    print("🔄 Matching Order Pair:")
    print("-"*60)
    buy, sell = generator.generate_matching_pair()
    print(f"BUY:  {buy['order_qty']} {buy['symbol']} @ ${buy['price']:.2f}")
    print(f"SELL: {sell['order_qty']} {sell['symbol']} @ ${sell['price']:.2f}")
    print()
    
    # Generate portfolio
    print("💼 Sample Portfolio:")
    print("-"*60)
    portfolio = generator.generate_portfolio(3)
    total_value = sum(p['market_value'] for p in portfolio)
    total_pnl = sum(p['pnl'] for p in portfolio)
    
    for position in portfolio:
        print(f"{position['symbol']:6} {position['quantity']:4} shares @ ${position['avg_price']:7.2f} | "
              f"Value: ${position['market_value']:9,.2f} | P&L: ${position['pnl']:+8.2f}")
    print("-"*60)
    print(f"Total Value: ${total_value:,.2f} | Total P&L: ${total_pnl:+,.2f}")
    print()


if __name__ == "__main__":
    main()
