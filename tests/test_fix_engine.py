"""
Unit Tests for FIX Protocol Engine
Demonstrates: Protocol testing, message parsing, validation
Skills: Python, FIX protocol, network protocols
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fix_engine import FIXEngine


class TestFIXEngine:
    """Test cases for FIX protocol engine."""
    
    @pytest.fixture
    def fix_engine(self):
        """Create FIX engine for testing."""
        return FIXEngine(sender_comp_id="TEST_CLIENT", target_comp_id="EXCHANGE")
    
    def test_engine_initialization(self, fix_engine):
        """Test FIX engine initialization."""
        assert fix_engine.sender_comp_id == "TEST_CLIENT"
        assert fix_engine.target_comp_id == "EXCHANGE"
        assert fix_engine.seq_num == 1
    
    def test_create_logon_message(self, fix_engine):
        """Test Logon message creation."""
        logon = fix_engine.create_logon(30)
        
        assert "8=FIX.4.2" in logon
        assert "35=A" in logon  # MsgType = Logon
        assert "108=30" in logon  # HeartbeatInt
        assert "49=TEST_CLIENT" in logon  # SenderCompID
        assert "56=EXCHANGE" in logon  # TargetCompID
    
    def test_create_heartbeat(self, fix_engine):
        """Test Heartbeat message creation."""
        heartbeat = fix_engine.create_heartbeat()
        
        assert "8=FIX.4.2" in heartbeat
        assert "35=0" in heartbeat  # MsgType = Heartbeat
    
    def test_create_heartbeat_with_test_req(self, fix_engine):
        """Test Heartbeat with TestReqID."""
        heartbeat = fix_engine.create_heartbeat("TEST123")
        
        assert "35=0" in heartbeat
        assert "112=TEST123" in heartbeat  # TestReqID
    
    def test_create_logout(self, fix_engine):
        """Test Logout message creation."""
        logout = fix_engine.create_logout()
        
        assert "8=FIX.4.2" in logout
        assert "35=5" in logout  # MsgType = Logout
    
    def test_create_new_order_single_limit(self, fix_engine):
        """Test New Order Single (Limit) creation."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="ORDER001",
            symbol="AAPL",
            side="1",  # Buy
            order_qty=100,
            order_type="2",  # Limit
            price=150.50
        )
        
        assert "35=D" in order  # MsgType = New Order Single
        assert "11=ORDER001" in order  # ClOrdID
        assert "55=AAPL" in order  # Symbol
        assert "54=1" in order  # Side = Buy
        assert "38=100" in order  # OrderQty
        assert "40=2" in order  # OrdType = Limit
        assert "44=150.5" in order  # Price
    
    def test_create_new_order_single_market(self, fix_engine):
        """Test New Order Single (Market) creation."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="ORDER002",
            symbol="GOOGL",
            side="2",  # Sell
            order_qty=50,
            order_type="1"  # Market
        )
        
        assert "35=D" in order
        assert "40=1" in order  # OrdType = Market
        # Market orders should not have price
        assert "44=" not in order
    
    def test_create_cancel_request(self, fix_engine):
        """Test Order Cancel Request creation."""
        cancel = fix_engine.create_cancel_request(
            cl_ord_id="CANCEL001",
            orig_cl_ord_id="ORDER001",
            symbol="AAPL",
            side="1"
        )
        
        assert "35=F" in cancel  # MsgType = Order Cancel Request
        assert "11=CANCEL001" in cancel  # ClOrdID
        assert "41=ORDER001" in cancel  # OrigClOrdID
    
    def test_parse_message(self, fix_engine):
        """Test FIX message parsing."""
        raw_message = "8=FIX.4.2\x0135=A\x0149=EXCHANGE\x0156=TEST_CLIENT\x0134=1\x01108=30\x0110=123\x01"
        
        tags = fix_engine.parse_message(raw_message)
        
        assert tags['8'] == 'FIX.4.2'
        assert tags['35'] == 'A'
        assert tags['49'] == 'EXCHANGE'
        assert tags['108'] == '30'
    
    def test_sequence_number_increment(self, fix_engine):
        """Test sequence number increments with each message."""
        initial_seq = fix_engine.seq_num
        
        fix_engine.create_logon(30)
        assert fix_engine.seq_num == initial_seq + 1
        
        fix_engine.create_heartbeat()
        assert fix_engine.seq_num == initial_seq + 2
    
    def test_checksum_calculation(self, fix_engine):
        """Test FIX checksum is present and valid format."""
        message = fix_engine.create_logon(30)
        
        # Checksum should be present (Tag 10)
        assert "10=" in message
        
        # Checksum should be 3 digits
        checksum_start = message.find("10=")
        checksum_value = message[checksum_start+3:checksum_start+6]
        assert len(checksum_value) == 3
        assert checksum_value.isdigit()
    
    def test_body_length(self, fix_engine):
        """Test body length calculation."""
        message = fix_engine.create_logon(30)
        
        # Body length should be present (Tag 9)
        assert "9=" in message


class TestFIXMessageValidation:
    """Test FIX message validation."""
    
    @pytest.fixture
    def fix_engine(self):
        return FIXEngine(sender_comp_id="TEST", target_comp_id="EXCH")
    
    def test_required_tags_present(self, fix_engine):
        """Test all required tags are present in messages."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="REQ001",
            symbol="AAPL",
            side="1",
            order_qty=100,
            order_type="2",
            price=150.0
        )
        
        # Required tags for New Order Single
        required_tags = ['8', '9', '35', '49', '56', '34', '52', '11', '55', '54', '38', '40']
        
        for tag in required_tags:
            assert f"{tag}=" in order, f"Missing required tag {tag}"
    
    def test_side_values(self, fix_engine):
        """Test valid side values."""
        buy_order = fix_engine.create_new_order_single(
            cl_ord_id="SIDE001", symbol="AAPL", side="1",
            order_qty=100, order_type="2", price=150.0
        )
        assert "54=1" in buy_order
        
        sell_order = fix_engine.create_new_order_single(
            cl_ord_id="SIDE002", symbol="AAPL", side="2",
            order_qty=100, order_type="2", price=150.0
        )
        assert "54=2" in sell_order
    
    def test_order_type_values(self, fix_engine):
        """Test valid order type values."""
        market_order = fix_engine.create_new_order_single(
            cl_ord_id="TYPE001", symbol="AAPL", side="1",
            order_qty=100, order_type="1"  # Market
        )
        assert "40=1" in market_order
        
        limit_order = fix_engine.create_new_order_single(
            cl_ord_id="TYPE002", symbol="AAPL", side="1",
            order_qty=100, order_type="2", price=150.0  # Limit
        )
        assert "40=2" in limit_order


class TestFIXProtocolEdgeCases:
    """Edge case tests for FIX protocol."""
    
    @pytest.fixture
    def fix_engine(self):
        return FIXEngine(sender_comp_id="TEST", target_comp_id="EXCH")
    
    def test_special_characters_in_symbol(self, fix_engine):
        """Test handling symbols with special characters."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="SPEC001",
            symbol="BRK.A",  # Symbol with period
            side="1",
            order_qty=1,
            order_type="2",
            price=500000.0
        )
        
        assert "55=BRK.A" in order
    
    def test_large_quantity(self, fix_engine):
        """Test handling large order quantities."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="LARGE001",
            symbol="AAPL",
            side="1",
            order_qty=1000000,  # 1 million shares
            order_type="2",
            price=150.0
        )
        
        assert "38=1000000" in order
    
    def test_decimal_price_precision(self, fix_engine):
        """Test decimal price handling."""
        order = fix_engine.create_new_order_single(
            cl_ord_id="DEC001",
            symbol="AAPL",
            side="1",
            order_qty=100,
            order_type="2",
            price=150.1234
        )
        
        # Should handle decimal prices
        assert "44=" in order
    
    def test_empty_message_parse(self, fix_engine):
        """Test parsing empty message."""
        tags = fix_engine.parse_message("")
        assert tags == {} or len(tags) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
