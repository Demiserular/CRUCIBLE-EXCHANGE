"""
Unit Tests for Matching Engine
Demonstrates: TDD/Unit testing, Python proficiency, algorithmic testing
Skills: pytest, test coverage, edge cases, performance testing
"""

import pytest
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exchange_server import OrderBook, Order


class TestOrder:
    """Test cases for Order class."""
    
    def test_order_creation(self):
        """Test basic order creation."""
        order = Order(
            order_id="ORD001",
            cl_ord_id="CL001",
            symbol="AAPL",
            side="1",
            order_qty=100,
            order_type="2",
            price=150.0
        )
        
        assert order.order_id == "ORD001"
        assert order.symbol == "AAPL"
        assert order.side == "1"
        assert order.order_qty == 100
        assert order.price == 150.0
        assert order.status == "0"  # New
        assert order.filled_qty == 0
    
    def test_order_remaining_qty(self):
        """Test remaining quantity calculation."""
        order = Order(
            order_id="ORD002",
            cl_ord_id="CL002",
            symbol="GOOGL",
            side="2",
            order_qty=100,
            order_type="2",
            price=175.0
        )
        
        order.filled_qty = 30
        assert order.remaining_qty == 70
    
    def test_order_is_complete(self):
        """Test order completion status."""
        order = Order(
            order_id="ORD003",
            cl_ord_id="CL003",
            symbol="MSFT",
            side="1",
            order_qty=100,
            order_type="2",
            price=380.0
        )
        
        assert not order.is_complete
        
        order.filled_qty = 100
        order.status = "2"  # Filled
        assert order.is_complete
    
    def test_order_to_dict(self):
        """Test order serialization."""
        order = Order(
            order_id="ORD004",
            cl_ord_id="CL004",
            symbol="TSLA",
            side="1",
            order_qty=50,
            order_type="2",
            price=250.0
        )
        
        data = order.to_dict()
        assert data['order_id'] == "ORD004"
        assert data['symbol'] == "TSLA"
        assert data['order_qty'] == 50


class TestOrderBook:
    """Test cases for OrderBook class."""
    
    @pytest.fixture
    def order_book(self):
        """Create a fresh order book for each test."""
        return OrderBook()
    
    def test_add_buy_order(self, order_book):
        """Test adding a buy order."""
        order = Order(
            order_id="BUY001",
            cl_ord_id="CL001",
            symbol="AAPL",
            side="1",  # Buy
            order_qty=100,
            order_type="2",
            price=150.0
        )
        
        order_book.add_order(order)
        
        assert "BUY001" in order_book.orders
        assert "AAPL" in order_book.buy_orders
    
    def test_add_sell_order(self, order_book):
        """Test adding a sell order."""
        order = Order(
            order_id="SELL001",
            cl_ord_id="CL002",
            symbol="GOOGL",
            side="2",  # Sell
            order_qty=50,
            order_type="2",
            price=175.0
        )
        
        order_book.add_order(order)
        
        assert "SELL001" in order_book.orders
        assert "GOOGL" in order_book.sell_orders
    
    def test_cancel_order(self, order_book):
        """Test canceling an order."""
        order = Order(
            order_id="CANCEL001",
            cl_ord_id="CL003",
            symbol="MSFT",
            side="1",
            order_qty=100,
            order_type="2",
            price=380.0
        )
        
        order_book.add_order(order)
        order_book.cancel_order("CANCEL001")
        
        assert order_book.orders["CANCEL001"].status == "4"  # Canceled
    
    def test_match_exact_price(self, order_book):
        """Test matching orders at exact price."""
        buy_order = Order(
            order_id="MATCH_BUY",
            cl_ord_id="CL004",
            symbol="AAPL",
            side="1",
            order_qty=100,
            order_type="2",
            price=150.0
        )
        
        sell_order = Order(
            order_id="MATCH_SELL",
            cl_ord_id="CL005",
            symbol="AAPL",
            side="2",
            order_qty=100,
            order_type="2",
            price=150.0
        )
        
        order_book.add_order(buy_order)
        order_book.add_order(sell_order)
        
        matches = order_book.match_orders("AAPL")
        
        assert len(matches) > 0
    
    def test_no_match_price_gap(self, order_book):
        """Test no match when price gap exists."""
        buy_order = Order(
            order_id="GAP_BUY",
            cl_ord_id="CL006",
            symbol="GOOGL",
            side="1",
            order_qty=100,
            order_type="2",
            price=170.0  # Bid price
        )
        
        sell_order = Order(
            order_id="GAP_SELL",
            cl_ord_id="CL007",
            symbol="GOOGL",
            side="2",
            order_qty=100,
            order_type="2",
            price=180.0  # Ask price higher than bid
        )
        
        order_book.add_order(buy_order)
        order_book.add_order(sell_order)
        
        matches = order_book.match_orders("GOOGL")
        
        # No matches expected due to price gap
        assert len(matches) == 0
    
    def test_partial_fill(self, order_book):
        """Test partial fill scenario."""
        buy_order = Order(
            order_id="PARTIAL_BUY",
            cl_ord_id="CL008",
            symbol="TSLA",
            side="1",
            order_qty=100,
            order_type="2",
            price=250.0
        )
        
        sell_order = Order(
            order_id="PARTIAL_SELL",
            cl_ord_id="CL009",
            symbol="TSLA",
            side="2",
            order_qty=50,
            order_type="2",
            price=250.0
        )
        
        order_book.add_order(buy_order)
        order_book.add_order(sell_order)
        
        matches = order_book.match_orders("TSLA")
        
        # Buy order should be partially filled
        assert order_book.orders["PARTIAL_BUY"].filled_qty == 50
        assert order_book.orders["PARTIAL_BUY"].status == "1"  # Partially Filled
    
    def test_get_order_book_snapshot(self, order_book):
        """Test order book snapshot generation."""
        order1 = Order("O1", "C1", "AAPL", "1", 100, "2", 150.0)
        order2 = Order("O2", "C2", "AAPL", "2", 100, "2", 151.0)
        
        order_book.add_order(order1)
        order_book.add_order(order2)
        
        snapshot = order_book.get_order_book_snapshot()
        
        assert 'buy_orders' in snapshot
        assert 'sell_orders' in snapshot
        assert 'AAPL' in snapshot['buy_orders']
        assert 'AAPL' in snapshot['sell_orders']


class TestMatchingPerformance:
    """Performance tests for matching engine."""
    
    def test_large_order_book_performance(self):
        """Test performance with large order book."""
        order_book = OrderBook()
        
        # Add 1000 orders
        start_time = time.time()
        
        for i in range(500):
            buy_order = Order(
                order_id=f"PERF_BUY_{i}",
                cl_ord_id=f"CL_BUY_{i}",
                symbol="AAPL",
                side="1",
                order_qty=100,
                order_type="2",
                price=150.0 - (i * 0.01)  # Decreasing prices
            )
            order_book.add_order(buy_order)
        
        for i in range(500):
            sell_order = Order(
                order_id=f"PERF_SELL_{i}",
                cl_ord_id=f"CL_SELL_{i}",
                symbol="AAPL",
                side="2",
                order_qty=100,
                order_type="2",
                price=150.5 + (i * 0.01)  # Increasing prices
            )
            order_book.add_order(sell_order)
        
        add_time = time.time() - start_time
        
        # Should add 1000 orders in under 1 second
        assert add_time < 1.0, f"Adding orders took {add_time:.2f}s"
        
        # Test matching performance
        start_time = time.time()
        matches = order_book.match_orders("AAPL")
        match_time = time.time() - start_time
        
        # Matching should complete in under 0.5 second
        assert match_time < 0.5, f"Matching took {match_time:.2f}s"


class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_order_book_match(self):
        """Test matching on empty order book."""
        order_book = OrderBook()
        matches = order_book.match_orders("AAPL")
        assert matches == []
    
    def test_single_side_order_book(self):
        """Test order book with only buy orders."""
        order_book = OrderBook()
        order = Order("O1", "C1", "AAPL", "1", 100, "2", 150.0)
        order_book.add_order(order)
        
        matches = order_book.match_orders("AAPL")
        assert matches == []
    
    def test_zero_quantity_order(self):
        """Test handling of zero quantity."""
        order_book = OrderBook()
        order = Order("O1", "C1", "AAPL", "1", 0, "2", 150.0)
        order_book.add_order(order)
        
        # Should handle gracefully
        assert "O1" in order_book.orders
    
    def test_cancel_nonexistent_order(self):
        """Test canceling order that doesn't exist."""
        order_book = OrderBook()
        # Should not raise exception
        order_book.cancel_order("NONEXISTENT")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
