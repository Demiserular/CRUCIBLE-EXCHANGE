"""
FIX Engine Helper Module

This module provides utilities for constructing, parsing, and validating
FIX 4.2 protocol messages used in electronic trading.
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime


class FIXEngine:
    """
    Helper class for FIX 4.2 message construction and validation.
    
    Provides methods to create common FIX messages (Logon, Heartbeat, 
    New Order Single, etc.) with proper formatting and checksum calculation.
    """
    
    # FIX Protocol Constants
    SOH = '\x01'  # Start of Header delimiter
    FIX_VERSION = "FIX.4.2"
    
    # Message Types (Tag 35)
    MSG_TYPE_HEARTBEAT = "0"
    MSG_TYPE_LOGON = "A"
    MSG_TYPE_LOGOUT = "5"
    MSG_TYPE_NEW_ORDER_SINGLE = "D"
    MSG_TYPE_EXECUTION_REPORT = "8"
    MSG_TYPE_ORDER_CANCEL_REQUEST = "F"
    MSG_TYPE_REJECT = "3"
    
    # Order Side (Tag 54)
    SIDE_BUY = "1"
    SIDE_SELL = "2"
    
    # Order Type (Tag 40)
    ORDER_TYPE_MARKET = "1"
    ORDER_TYPE_LIMIT = "2"
    
    # Execution Type (Tag 150)
    EXEC_TYPE_NEW = "0"
    EXEC_TYPE_PARTIAL_FILL = "1"
    EXEC_TYPE_FILL = "2"
    EXEC_TYPE_CANCELED = "4"
    EXEC_TYPE_REJECTED = "8"
    
    # Order Status (Tag 39)
    ORDER_STATUS_NEW = "0"
    ORDER_STATUS_PARTIALLY_FILLED = "1"
    ORDER_STATUS_FILLED = "2"
    ORDER_STATUS_CANCELED = "4"
    ORDER_STATUS_REJECTED = "8"
    
    def __init__(self, sender_comp_id: str = "CLIENT", target_comp_id: str = "EXCHANGE"):
        """
        Initialize FIX Engine with session identifiers.
        
        Args:
            sender_comp_id: The sender's company ID
            target_comp_id: The target company ID
        """
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.msg_seq_num = 1
    
    def _calculate_checksum(self, message: str) -> str:
        """
        Calculate FIX checksum (Tag 10).
        
        Sum all bytes in message (excluding checksum field) and take modulo 256.
        
        Args:
            message: FIX message string without checksum
            
        Returns:
            Three-digit checksum string (e.g., "156")
        """
        checksum = sum(ord(char) for char in message) % 256
        return f"{checksum:03d}"
    
    def _get_timestamp(self) -> str:
        """
        Generate FIX UTC timestamp in format: YYYYMMDD-HH:MM:SS
        
        Returns:
            Formatted timestamp string
        """
        return datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")
    
    def _build_header(self, msg_type: str) -> str:
        """
        Build standard FIX message header (tags 8, 9, 35, 49, 56, 34, 52).
        
        Args:
            msg_type: FIX message type (e.g., "A" for Logon)
            
        Returns:
            Header string without body length (Tag 9) calculated yet
        """
        header = (
            f"35={msg_type}{self.SOH}"
            f"49={self.sender_comp_id}{self.SOH}"
            f"56={self.target_comp_id}{self.SOH}"
            f"34={self.msg_seq_num}{self.SOH}"
            f"52={self._get_timestamp()}{self.SOH}"
        )
        return header
    
    def _build_message(self, msg_type: str, body: str = "") -> str:
        """
        Build complete FIX message with header, body, and trailer.
        
        Args:
            msg_type: FIX message type
            body: Message body (optional)
            
        Returns:
            Complete FIX message with checksum
        """
        # Build header (without BeginString and BodyLength yet)
        header = self._build_header(msg_type)
        
        # Combine header and body
        message_content = header + body
        
        # Calculate body length (everything after Tag 9)
        body_length = len(message_content)
        
        # Build complete message without checksum
        message_without_checksum = (
            f"8={self.FIX_VERSION}{self.SOH}"
            f"9={body_length}{self.SOH}"
            f"{message_content}"
        )
        
        # Calculate and append checksum
        checksum = self._calculate_checksum(message_without_checksum)
        complete_message = f"{message_without_checksum}10={checksum}{self.SOH}"
        
        # Increment sequence number
        self.msg_seq_num += 1
        
        return complete_message
    
    def create_logon(self, heartbeat_interval: int = 30) -> str:
        """
        Create Logon message (35=A).
        
        Args:
            heartbeat_interval: Heartbeat interval in seconds (Tag 108)
            
        Returns:
            Complete FIX Logon message
        """
        body = f"108={heartbeat_interval}{self.SOH}"
        return self._build_message(self.MSG_TYPE_LOGON, body)
    
    def create_heartbeat(self, test_req_id: Optional[str] = None) -> str:
        """
        Create Heartbeat message (35=0).
        
        Args:
            test_req_id: Optional Test Request ID (Tag 112)
            
        Returns:
            Complete FIX Heartbeat message
        """
        body = ""
        if test_req_id:
            body = f"112={test_req_id}{self.SOH}"
        return self._build_message(self.MSG_TYPE_HEARTBEAT, body)
    
    def create_logout(self, text: Optional[str] = None) -> str:
        """
        Create Logout message (35=5).
        
        Args:
            text: Optional logout reason (Tag 58)
            
        Returns:
            Complete FIX Logout message
        """
        body = ""
        if text:
            body = f"58={text}{self.SOH}"
        return self._build_message(self.MSG_TYPE_LOGOUT, body)
    
    def create_new_order_single(
        self,
        cl_ord_id: str,
        symbol: str,
        side: str,
        order_qty: int,
        order_type: str,
        price: Optional[float] = None
    ) -> str:
        """
        Create New Order Single message (35=D).
        
        Args:
            cl_ord_id: Client Order ID (Tag 11)
            symbol: Trading symbol (Tag 55)
            side: Buy (1) or Sell (2) (Tag 54)
            order_qty: Order quantity (Tag 38)
            order_type: Market (1) or Limit (2) (Tag 40)
            price: Limit price (Tag 44), required for Limit orders
            
        Returns:
            Complete FIX New Order Single message
        """
        body = (
            f"11={cl_ord_id}{self.SOH}"
            f"55={symbol}{self.SOH}"
            f"54={side}{self.SOH}"
            f"38={order_qty}{self.SOH}"
            f"40={order_type}{self.SOH}"
        )
        
        # Add price for limit orders
        if price is not None:
            body += f"44={price}{self.SOH}"
        
        # Add transaction time (Tag 60)
        body += f"60={self._get_timestamp()}{self.SOH}"
        
        return self._build_message(self.MSG_TYPE_NEW_ORDER_SINGLE, body)
    
    def create_execution_report(
        self,
        order_id: str,
        exec_id: str,
        exec_type: str,
        ord_status: str,
        symbol: str,
        side: str,
        order_qty: int,
        last_qty: int,
        last_px: float,
        cum_qty: int,
        avg_px: float,
        cl_ord_id: Optional[str] = None,
        text: Optional[str] = None
    ) -> str:
        """
        Create Execution Report message (35=8).
        
        Args:
            order_id: Exchange Order ID (Tag 37)
            exec_id: Execution ID (Tag 17)
            exec_type: Execution type (Tag 150)
            ord_status: Order status (Tag 39)
            symbol: Trading symbol (Tag 55)
            side: Buy (1) or Sell (2) (Tag 54)
            order_qty: Order quantity (Tag 38)
            last_qty: Quantity filled in this execution (Tag 32)
            last_px: Price of this execution (Tag 31)
            cum_qty: Cumulative quantity filled (Tag 14)
            avg_px: Average fill price (Tag 6)
            cl_ord_id: Client Order ID (Tag 11)
            text: Optional text message (Tag 58)
            
        Returns:
            Complete FIX Execution Report message
        """
        body = (
            f"37={order_id}{self.SOH}"
            f"17={exec_id}{self.SOH}"
            f"150={exec_type}{self.SOH}"
            f"39={ord_status}{self.SOH}"
            f"55={symbol}{self.SOH}"
            f"54={side}{self.SOH}"
            f"38={order_qty}{self.SOH}"
            f"32={last_qty}{self.SOH}"
            f"31={last_px}{self.SOH}"
            f"14={cum_qty}{self.SOH}"
            f"6={avg_px}{self.SOH}"
        )
        
        if cl_ord_id:
            body += f"11={cl_ord_id}{self.SOH}"
        
        if text:
            body += f"58={text}{self.SOH}"
        
        # Add transaction time
        body += f"60={self._get_timestamp()}{self.SOH}"
        
        return self._build_message(self.MSG_TYPE_EXECUTION_REPORT, body)
    
    def create_order_cancel_request(
        self,
        orig_cl_ord_id: str,
        cl_ord_id: str,
        symbol: str,
        side: str,
        order_qty: int
    ) -> str:
        """
        Create Order Cancel Request message (35=F).
        
        Args:
            orig_cl_ord_id: Original Client Order ID (Tag 41)
            cl_ord_id: New Client Order ID (Tag 11)
            symbol: Trading symbol (Tag 55)
            side: Buy (1) or Sell (2) (Tag 54)
            order_qty: Order quantity (Tag 38)
            
        Returns:
            Complete FIX Order Cancel Request message
        """
        body = (
            f"41={orig_cl_ord_id}{self.SOH}"
            f"11={cl_ord_id}{self.SOH}"
            f"55={symbol}{self.SOH}"
            f"54={side}{self.SOH}"
            f"38={order_qty}{self.SOH}"
            f"60={self._get_timestamp()}{self.SOH}"
        )
        
        return self._build_message(self.MSG_TYPE_ORDER_CANCEL_REQUEST, body)
    
    def parse_message(self, raw_message: str) -> Dict[str, str]:
        """
        Parse FIX message into dictionary of tag-value pairs.
        
        Args:
            raw_message: Raw FIX message string
            
        Returns:
            Dictionary mapping tag numbers to values
        """
        tags = {}
        
        # Split by SOH delimiter
        fields = raw_message.split(self.SOH)
        
        for field in fields:
            if '=' in field:
                tag, value = field.split('=', 1)
                tags[tag] = value
        
        return tags
    
    def validate_checksum(self, raw_message: str) -> bool:
        """
        Validate FIX message checksum.
        
        Args:
            raw_message: Complete FIX message with checksum
            
        Returns:
            True if checksum is valid, False otherwise
        """
        # Find checksum field (10=XXX)
        checksum_index = raw_message.rfind(f"10=")
        
        if checksum_index == -1:
            return False
        
        # Extract message without checksum
        message_without_checksum = raw_message[:checksum_index]
        
        # Extract provided checksum
        checksum_field = raw_message[checksum_index:].split(self.SOH)[0]
        provided_checksum = checksum_field.split('=')[1]
        
        # Calculate expected checksum
        expected_checksum = self._calculate_checksum(message_without_checksum)
        
        return provided_checksum == expected_checksum
    
    def validate_message_structure(self, raw_message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate basic FIX message structure.
        
        Args:
            raw_message: Raw FIX message string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if message starts with BeginString (Tag 8)
        if not raw_message.startswith("8="):
            return False, "Message must start with BeginString (Tag 8)"
        
        # Check if message contains SOH delimiters
        if self.SOH not in raw_message:
            return False, "Message missing SOH delimiters"
        
        # Check for required header fields
        tags = self.parse_message(raw_message)
        
        required_tags = ["8", "9", "35", "49", "56", "34", "52", "10"]
        missing_tags = [tag for tag in required_tags if tag not in tags]
        
        if missing_tags:
            return False, f"Missing required tags: {', '.join(missing_tags)}"
        
        # Validate checksum
        if not self.validate_checksum(raw_message):
            return False, "Invalid checksum"
        
        return True, None
    
    def reset_sequence(self) -> None:
        """Reset message sequence number to 1."""
        self.msg_seq_num = 1
