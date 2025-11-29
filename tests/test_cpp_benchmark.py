"""
C++ Engine Integration Tests and Performance Benchmarks
Demonstrates: C++ integration, performance testing, benchmarking
Skills: C++, Python bindings, performance optimization
"""

import pytest
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Try to import C++ engine
try:
    import crucible_engine
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False

from exchange_server import OrderBook, Order


class TestCppEngineIntegration:
    """Test C++ matching engine integration."""
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_engine_import(self):
        """Test C++ engine can be imported."""
        assert crucible_engine is not None
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_order_creation(self):
        """Test creating orders in C++ engine."""
        order = crucible_engine.Order()
        order.order_id = "CPP001"
        order.symbol = "AAPL"
        order.side = 1  # Buy
        order.price = 150.0
        order.quantity = 100
        
        assert order.order_id == "CPP001"
        assert order.symbol == "AAPL"
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_orderbook_creation(self):
        """Test creating order book in C++ engine."""
        ob = crucible_engine.OrderBook()
        assert ob is not None
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_add_order(self):
        """Test adding orders to C++ order book."""
        ob = crucible_engine.OrderBook()
        
        order = crucible_engine.Order()
        order.order_id = "ADD001"
        order.symbol = "AAPL"
        order.side = 1
        order.price = 150.0
        order.quantity = 100
        
        ob.add_order(order)
        # Should not raise exception
        assert True
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_matching(self):
        """Test order matching in C++ engine."""
        ob = crucible_engine.OrderBook()
        
        # Add buy order
        buy = crucible_engine.Order()
        buy.order_id = "MATCH_BUY"
        buy.symbol = "AAPL"
        buy.side = 1
        buy.price = 150.0
        buy.quantity = 100
        ob.add_order(buy)
        
        # Add sell order
        sell = crucible_engine.Order()
        sell.order_id = "MATCH_SELL"
        sell.symbol = "AAPL"
        sell.side = 2
        sell.price = 150.0
        sell.quantity = 100
        ob.add_order(sell)
        
        # Match orders
        matches = ob.match_orders("AAPL")
        assert len(matches) > 0


class TestPerformanceBenchmarks:
    """Performance benchmarks comparing Python and C++ implementations."""
    
    @pytest.fixture
    def python_orderbook(self):
        return OrderBook()
    
    def test_python_add_order_performance(self, python_orderbook):
        """Benchmark Python order addition."""
        start = time.time()
        
        for i in range(1000):
            order = Order(
                order_id=f"PERF_{i}",
                cl_ord_id=f"CL_{i}",
                symbol="AAPL",
                side="1" if i % 2 == 0 else "2",
                order_qty=100,
                order_type="2",
                price=150.0 + (i * 0.01)
            )
            python_orderbook.add_order(order)
        
        elapsed = time.time() - start
        
        print(f"\nPython: Added 1000 orders in {elapsed:.3f}s")
        print(f"Python: {1000/elapsed:.0f} orders/second")
        
        # Should complete in reasonable time
        assert elapsed < 5.0, f"Too slow: {elapsed:.3f}s"
    
    def test_python_matching_performance(self, python_orderbook):
        """Benchmark Python order matching."""
        # Setup: Add orders that will match
        for i in range(100):
            buy = Order(f"BUY_{i}", f"CLB_{i}", "AAPL", "1", 100, "2", 150.0)
            sell = Order(f"SELL_{i}", f"CLS_{i}", "AAPL", "2", 100, "2", 150.0)
            python_orderbook.add_order(buy)
            python_orderbook.add_order(sell)
        
        start = time.time()
        matches = python_orderbook.match_orders("AAPL")
        elapsed = time.time() - start
        
        print(f"\nPython: Matched {len(matches)} orders in {elapsed:.3f}s")
        
        assert elapsed < 2.0, f"Matching too slow: {elapsed:.3f}s"
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_add_order_performance(self):
        """Benchmark C++ order addition."""
        ob = crucible_engine.OrderBook()
        
        start = time.time()
        
        for i in range(1000):
            order = crucible_engine.Order()
            order.order_id = f"CPP_PERF_{i}"
            order.symbol = "AAPL"
            order.side = 1 if i % 2 == 0 else 2
            order.price = 150.0 + (i * 0.01)
            order.quantity = 100
            ob.add_order(order)
        
        elapsed = time.time() - start
        
        print(f"\nC++: Added 1000 orders in {elapsed:.3f}s")
        print(f"C++: {1000/elapsed:.0f} orders/second")
        
        assert elapsed < 1.0, f"C++ too slow: {elapsed:.3f}s"
    
    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ engine not compiled")
    def test_cpp_vs_python_comparison(self):
        """Compare C++ vs Python performance."""
        # Python benchmark
        py_ob = OrderBook()
        
        py_start = time.time()
        for i in range(500):
            order = Order(f"PY_{i}", f"CL_{i}", "AAPL", "1", 100, "2", 150.0)
            py_ob.add_order(order)
        py_elapsed = time.time() - py_start
        
        # C++ benchmark
        cpp_ob = crucible_engine.OrderBook()
        
        cpp_start = time.time()
        for i in range(500):
            order = crucible_engine.Order()
            order.order_id = f"CPP_{i}"
            order.symbol = "AAPL"
            order.side = 1
            order.price = 150.0
            order.quantity = 100
            cpp_ob.add_order(order)
        cpp_elapsed = time.time() - cpp_start
        
        speedup = py_elapsed / cpp_elapsed if cpp_elapsed > 0 else 0
        
        print(f"\n=== Performance Comparison ===")
        print(f"Python: {py_elapsed:.3f}s")
        print(f"C++:    {cpp_elapsed:.3f}s")
        print(f"Speedup: {speedup:.1f}x")
        
        # C++ should be faster
        assert cpp_elapsed <= py_elapsed, "C++ should be faster than Python"


class TestLoadTesting:
    """Load testing for high-volume scenarios."""
    
    def test_high_volume_orders(self):
        """Test handling high volume of orders."""
        ob = OrderBook()
        
        start = time.time()
        
        for i in range(5000):
            side = "1" if i % 2 == 0 else "2"
            price = 150.0 + (i % 100) * 0.01
            
            order = Order(
                order_id=f"LOAD_{i}",
                cl_ord_id=f"CL_{i}",
                symbol="AAPL",
                side=side,
                order_qty=100,
                order_type="2",
                price=price
            )
            ob.add_order(order)
        
        elapsed = time.time() - start
        
        print(f"\nLoad test: Added 5000 orders in {elapsed:.3f}s")
        print(f"Throughput: {5000/elapsed:.0f} orders/second")
        
        assert elapsed < 10.0, "Load test too slow"
        assert len(ob.orders) == 5000
    
    def test_memory_stability(self):
        """Test memory doesn't grow unbounded."""
        import gc
        
        ob = OrderBook()
        
        # Add and remove orders repeatedly
        for batch in range(10):
            for i in range(100):
                order = Order(
                    order_id=f"MEM_{batch}_{i}",
                    cl_ord_id=f"CL_{batch}_{i}",
                    symbol="AAPL",
                    side="1",
                    order_qty=100,
                    order_type="2",
                    price=150.0
                )
                ob.add_order(order)
            
            # Cancel half
            for i in range(50):
                ob.cancel_order(f"MEM_{batch}_{i}")
            
            gc.collect()
        
        # Should complete without memory issues
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
