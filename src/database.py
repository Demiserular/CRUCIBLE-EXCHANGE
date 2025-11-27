"""
Database layer for Crucible FIX Exchange
Handles PostgreSQL persistence for orders and executions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_config: Dict):
        """
        Initialize database manager.
        
        Args:
            db_config: Database configuration dict with keys:
                - host: Database host
                - port: Database port
                - dbname: Database name
                - user: Database user
                - password: Database password
        """
        self.db_config = db_config
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info(f"Connected to PostgreSQL database: {self.db_config['dbname']}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            with self.connection.cursor() as cursor:
                # Orders table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id VARCHAR(50) PRIMARY KEY,
                        cl_ord_id VARCHAR(50) NOT NULL,
                        symbol VARCHAR(10) NOT NULL,
                        side CHAR(1) NOT NULL,
                        order_type CHAR(1) NOT NULL,
                        order_qty INTEGER NOT NULL,
                        price DECIMAL(10, 2),
                        filled_qty INTEGER DEFAULT 0,
                        status CHAR(1) DEFAULT '0',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Executions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS executions (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        side VARCHAR(10) NOT NULL,
                        last_qty INTEGER NOT NULL,
                        last_px DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(50),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON executions(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_executions_symbol ON executions(symbol)
                """)
                
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
            order: Order dictionary with keys: order_id, cl_ord_id, symbol, side, 
                   order_type, order_qty, price, filled_qty, status
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO orders (order_id, cl_ord_id, symbol, side, order_type, 
                                       order_qty, price, filled_qty, status, created_at, updated_at)
                    VALUES (%(order_id)s, %(cl_ord_id)s, %(symbol)s, %(side)s, %(order_type)s,
                            %(order_qty)s, %(price)s, %(filled_qty)s, %(status)s, NOW(), NOW())
                    ON CONFLICT (order_id) DO UPDATE SET
                        filled_qty = %(filled_qty)s,
                        status = %(status)s,
                        updated_at = NOW()
                """, order)
                self.connection.commit()
                logger.debug(f"Saved order: {order['order_id']}")
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            self.connection.rollback()
    
    def save_execution(self, execution: Dict):
        """
        Save execution to database.
        
        Args:
            execution: Execution dictionary with keys: symbol, side, last_qty, 
                      last_px, status, timestamp
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO executions (symbol, side, last_qty, last_px, status, timestamp)
                    VALUES (%(symbol)s, %(side)s, %(last_qty)s, %(last_px)s, %(status)s, 
                            COALESCE(%(timestamp)s::timestamp, NOW()))
                """, execution)
                self.connection.commit()
                logger.debug(f"Saved execution: {execution['symbol']} {execution['side']} {execution['last_qty']}@{execution['last_px']}")
        except Exception as e:
            logger.error(f"Failed to save execution: {e}")
            self.connection.rollback()
    
    def get_recent_executions(self, limit: int = 100) -> List[Dict]:
        """
        Get recent executions from database.
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of execution dictionaries
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT symbol, side, last_qty, last_px, status,
                           TO_CHAR(timestamp, 'HH24:MI:SS') as timestamp
                    FROM executions
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (limit,))
                executions = cursor.fetchall()
                return [dict(exec) for exec in executions]
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return []
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open orders from database.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of order dictionaries
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if symbol:
                    cursor.execute("""
                        SELECT order_id, cl_ord_id, symbol, side, order_type, 
                               order_qty, price, filled_qty, status
                        FROM orders
                        WHERE status IN ('0', '1') AND symbol = %s
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
                orders = cursor.fetchall()
                return [dict(order) for order in orders]
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get exchange statistics.
        
        Returns:
            Dictionary with total_orders, filled_orders, total_volume
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM orders) as total_orders,
                        (SELECT COUNT(*) FROM orders WHERE status = '2') as filled_orders,
                        (SELECT COALESCE(SUM(last_qty), 0) FROM executions) as total_volume
                """)
                stats = cursor.fetchone()
                return dict(stats) if stats else {'total_orders': 0, 'filled_orders': 0, 'total_volume': 0}
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'total_orders': 0, 'filled_orders': 0, 'total_volume': 0}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
