"""
Database layer for Crucible FIX Exchange
Handles SQLite persistence for orders and executions (lightweight alternative to PostgreSQL)
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str = "crucible.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    cl_ord_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    order_qty INTEGER NOT NULL,
                    price REAL,
                    filled_qty INTEGER DEFAULT 0,
                    status TEXT DEFAULT '0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Executions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    last_qty INTEGER NOT NULL,
                    last_px REAL NOT NULL,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON executions(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_symbol ON executions(symbol)")
            
            self.connection.commit()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.connection.rollback()
            raise
    
    def save_order(self, order: Dict):
        """
        Save order to database.
        
        Args:
            order: Order dictionary
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO orders 
                (order_id, cl_ord_id, symbol, side, order_type, order_qty, price, filled_qty, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                order.get('order_id'),
                order.get('cl_ord_id'),
                order.get('symbol'),
                order.get('side'),
                order.get('order_type'),
                order.get('order_qty'),
                order.get('price'),
                order.get('filled_qty', 0),
                order.get('status', '0')
            ))
            self.connection.commit()
            logger.debug(f"Saved order: {order.get('order_id')}")
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            self.connection.rollback()
    
    def save_execution(self, execution: Dict):
        """
        Save execution to database.
        
        Args:
            execution: Execution dictionary
        """
        try:
            cursor = self.connection.cursor()
            
            # Handle timestamp
            timestamp = execution.get('timestamp')
            if timestamp and not isinstance(timestamp, str):
                timestamp = datetime.now().strftime('%H:%M:%S')
            
            cursor.execute("""
                INSERT INTO executions (symbol, side, last_qty, last_px, status, timestamp)
                VALUES (?, ?, ?, ?, ?, COALESCE(?, datetime('now')))
            """, (
                execution.get('symbol'),
                execution.get('side'),
                execution.get('last_qty'),
                execution.get('last_px'),
                execution.get('status'),
                timestamp
            ))
            self.connection.commit()
            logger.debug(f"Saved execution: {execution.get('symbol')} {execution.get('side')}")
        except Exception as e:
            logger.error(f"Failed to save execution: {e}")
            self.connection.rollback()
    
    def get_recent_executions(self, limit: int = 100) -> List[Dict]:
        """Get recent executions from database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT symbol, side, last_qty, last_px, status,
                       strftime('%H:%M:%S', timestamp) as timestamp
                FROM executions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return []
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders from database."""
        try:
            cursor = self.connection.cursor()
            if symbol:
                cursor.execute("""
                    SELECT order_id, cl_ord_id, symbol, side, order_type, 
                           order_qty, price, filled_qty, status
                    FROM orders
                    WHERE status IN ('0', '1') AND symbol = ?
                    ORDER BY created_at DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT order_id, cl_ord_id, symbol, side, order_type, 
                           order_qty, price, filled_qty, status
                    FROM orders
                    WHERE status IN ('0', '1')
                    ORDER BY created_at DESC
                """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get exchange statistics."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM orders) as total_orders,
                    (SELECT COUNT(*) FROM orders WHERE status = '2') as filled_orders,
                    (SELECT COALESCE(SUM(last_qty), 0) FROM executions) as total_volume
            """)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {'total_orders': 0, 'filled_orders': 0, 'total_volume': 0}
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'total_orders': 0, 'filled_orders': 0, 'total_volume': 0}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
