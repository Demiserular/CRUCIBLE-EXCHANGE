"""
Unit Tests for Database Operations
Demonstrates: SQL testing, data integrity, CRUD operations
Skills: Python, SQLite, SQL queries, database testing
"""

import pytest
import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database_sqlite import DatabaseManager

TEST_DB = "test_unit.db"


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Clean up before
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
        self.db = DatabaseManager(TEST_DB)
        
        yield
        
        # Clean up after
        self.db.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
    
    def test_database_initialization(self):
        """Test database tables are created."""
        # Tables should exist
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'orders' in tables
        assert 'executions' in tables
    
    def test_save_order(self):
        """Test saving an order."""
        order = {
            'order_id': 'ORD001',
            'cl_ord_id': 'CL001',
            'symbol': 'AAPL',
            'side': 'Buy',
            'order_qty': 100,
            'order_type': 'Limit',
            'price': 150.0,
            'status': 'New',
            'timestamp': '10:00:00'
        }
        
        self.db.save_order(order)
        
        orders = self.db.get_orders()
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'ORD001'
    
    def test_update_order(self):
        """Test updating an existing order."""
        order = {
            'order_id': 'ORD002',
            'symbol': 'GOOGL',
            'side': 'Sell',
            'order_qty': 50,
            'price': 175.0,
            'status': 'New',
            'timestamp': '10:00:00'
        }
        
        self.db.save_order(order)
        
        # Update status
        order['status'] = 'Filled'
        order['filled_qty'] = 50
        self.db.save_order(order)
        
        orders = self.db.get_orders()
        updated = next(o for o in orders if o['order_id'] == 'ORD002')
        assert updated['status'] == 'Filled'
    
    def test_save_execution(self):
        """Test saving an execution."""
        execution = {
            'exec_id': 'EXEC001',
            'order_id': 'ORD001',
            'symbol': 'AAPL',
            'side': 'Buy',
            'last_qty': 100,
            'last_px': 150.0,
            'timestamp': '10:00:01'
        }
        
        self.db.save_execution(execution)
        
        executions = self.db.get_executions()
        assert len(executions) == 1
        assert executions[0]['exec_id'] == 'EXEC001'
    
    def test_get_orders_empty(self):
        """Test getting orders from empty database."""
        orders = self.db.get_orders()
        assert orders == []
    
    def test_get_executions_empty(self):
        """Test getting executions from empty database."""
        executions = self.db.get_executions()
        assert executions == []
    
    def test_get_executions_with_limit(self):
        """Test getting executions with limit."""
        # Add multiple executions
        for i in range(10):
            self.db.save_execution({
                'exec_id': f'EXEC{i:03d}',
                'order_id': f'ORD{i:03d}',
                'symbol': 'AAPL',
                'side': 'Buy',
                'last_qty': 100,
                'last_px': 150.0,
                'timestamp': f'10:00:{i:02d}'
            })
        
        # Get with limit
        executions = self.db.get_executions(limit=5)
        assert len(executions) == 5
    
    def test_multiple_symbols(self):
        """Test orders with different symbols."""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        
        for i, symbol in enumerate(symbols):
            self.db.save_order({
                'order_id': f'SYM{i:03d}',
                'symbol': symbol,
                'side': 'Buy',
                'order_qty': 100,
                'price': 100.0 + i,
                'status': 'New',
                'timestamp': '10:00:00'
            })
        
        orders = self.db.get_orders()
        assert len(orders) == 5
        
        symbols_in_db = set(o['symbol'] for o in orders)
        assert symbols_in_db == set(symbols)


class TestDatabaseConcurrency:
    """Concurrency tests for database operations."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown."""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
        self.db = DatabaseManager(TEST_DB)
        
        yield
        
        self.db.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
    
    def test_concurrent_writes(self):
        """Test concurrent order writes."""
        results = []
        threads = []
        
        def write_order(idx):
            try:
                self.db.save_order({
                    'order_id': f'CONC{idx:04d}',
                    'symbol': 'AAPL',
                    'side': 'Buy',
                    'order_qty': 100,
                    'price': 150.0,
                    'status': 'New',
                    'timestamp': time.strftime('%H:%M:%S')
                })
                results.append(True)
            except Exception:
                results.append(False)
        
        # Create threads
        for i in range(20):
            t = threading.Thread(target=write_order, args=(i,))
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify results
        assert all(results), "Some concurrent writes failed"
        
        orders = self.db.get_orders()
        assert len(orders) == 20
    
    def test_read_while_writing(self):
        """Test reading while writing."""
        stop_flag = threading.Event()
        read_results = []
        write_results = []
        
        def writer():
            for i in range(10):
                try:
                    self.db.save_order({
                        'order_id': f'RW{i:04d}',
                        'symbol': 'AAPL',
                        'side': 'Buy',
                        'order_qty': 100,
                        'price': 150.0,
                        'status': 'New',
                        'timestamp': time.strftime('%H:%M:%S')
                    })
                    write_results.append(True)
                    time.sleep(0.01)
                except Exception:
                    write_results.append(False)
            stop_flag.set()
        
        def reader():
            while not stop_flag.is_set():
                try:
                    orders = self.db.get_orders()
                    read_results.append(len(orders) >= 0)
                    time.sleep(0.005)
                except Exception:
                    read_results.append(False)
        
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        reader_thread.start()
        writer_thread.start()
        
        writer_thread.join()
        reader_thread.join()
        
        assert all(write_results), "Some writes failed"
        assert all(read_results), "Some reads failed"


class TestDatabaseEdgeCases:
    """Edge case tests for database."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
        self.db = DatabaseManager(TEST_DB)
        
        yield
        
        self.db.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
    
    def test_special_characters(self):
        """Test handling special characters in data."""
        self.db.save_order({
            'order_id': "ORD'001",  # Quote in ID
            'symbol': 'BRK.A',  # Period in symbol
            'side': 'Buy',
            'order_qty': 100,
            'price': 150.0,
            'status': 'New',
            'timestamp': '10:00:00'
        })
        
        orders = self.db.get_orders()
        assert len(orders) == 1
    
    def test_large_price_values(self):
        """Test handling large price values."""
        self.db.save_order({
            'order_id': 'LARGE001',
            'symbol': 'BRK.A',
            'side': 'Buy',
            'order_qty': 1,
            'price': 500000.00,  # Very large price
            'status': 'New',
            'timestamp': '10:00:00'
        })
        
        orders = self.db.get_orders()
        assert orders[0]['price'] == 500000.00
    
    def test_null_optional_fields(self):
        """Test handling null optional fields."""
        self.db.save_order({
            'order_id': 'NULL001',
            'symbol': 'AAPL',
            'side': 'Buy',
            'order_qty': 100,
            'status': 'New',
            'timestamp': '10:00:00'
            # No price (market order)
        })
        
        orders = self.db.get_orders()
        assert len(orders) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
