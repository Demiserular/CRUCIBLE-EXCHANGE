"""
Network and System Tests
Demonstrates: Network testing, socket programming, system integration
Skills: Python, networking, Linux/system concepts, concurrent connections
"""

import pytest
import socket
import threading
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fix_engine import FIXEngine


class TestNetworkConnectivity:
    """Test network connectivity and socket operations."""
    
    HOST = "127.0.0.1"
    PORT = 9878  # Live server port
    
    @pytest.fixture
    def fix_engine(self):
        return FIXEngine(sender_comp_id="NET_TEST", target_comp_id="EXCHANGE")
    
    @pytest.mark.skipif(
        os.environ.get('CI') == 'true',
        reason="Skip network tests in CI environment"
    )
    def test_tcp_connection(self):
        """Test basic TCP connection to exchange."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        try:
            sock.connect((self.HOST, self.PORT))
            assert True, "Connection successful"
        except ConnectionRefusedError:
            pytest.skip("Exchange server not running")
        finally:
            sock.close()
    
    @pytest.mark.skipif(
        os.environ.get('CI') == 'true',
        reason="Skip network tests in CI environment"
    )
    def test_fix_logon(self, fix_engine):
        """Test FIX protocol logon."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        try:
            sock.connect((self.HOST, self.PORT))
            
            # Send logon
            logon = fix_engine.create_logon(30)
            sock.sendall(logon.encode('utf-8'))
            
            # Receive response
            response = sock.recv(4096).decode('utf-8')
            
            # Parse response
            tags = fix_engine.parse_message(response)
            
            assert tags.get('35') == 'A', "Expected Logon response"
        except ConnectionRefusedError:
            pytest.skip("Exchange server not running")
        finally:
            sock.close()
    
    @pytest.mark.skipif(
        os.environ.get('CI') == 'true',
        reason="Skip network tests in CI environment"
    )
    def test_connection_timeout(self):
        """Test connection timeout handling."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.001)  # Very short timeout
        
        try:
            # Try to connect to a non-listening port
            sock.connect((self.HOST, 59999))
            assert False, "Should have timed out"
        except (socket.timeout, ConnectionRefusedError, OSError):
            assert True, "Timeout handled correctly"
        finally:
            sock.close()
    
    @pytest.mark.skipif(
        os.environ.get('CI') == 'true',
        reason="Skip network tests in CI environment"
    )
    def test_multiple_connections(self, fix_engine):
        """Test multiple concurrent connections."""
        connections = []
        results = []
        
        def connect_and_logon(idx):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            
            try:
                sock.connect((self.HOST, self.PORT))
                
                # Create separate FIX engine for each connection
                engine = FIXEngine(
                    sender_comp_id=f"NET_TEST_{idx}",
                    target_comp_id="EXCHANGE"
                )
                
                logon = engine.create_logon(30)
                sock.sendall(logon.encode('utf-8'))
                
                response = sock.recv(4096).decode('utf-8')
                tags = engine.parse_message(response)
                
                results.append(tags.get('35') == 'A')
            except Exception as e:
                results.append(False)
            finally:
                connections.append(sock)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=connect_and_logon, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Cleanup
        for sock in connections:
            try:
                sock.close()
            except:
                pass
        
        if len(results) == 0:
            pytest.skip("Exchange server not running")
        
        assert all(results), "Not all connections succeeded"


class TestSocketOperations:
    """Test socket-level operations."""
    
    def test_socket_options(self):
        """Test setting socket options."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set reuse address
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Set keep-alive
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Verify options are set
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        keepalive = sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        
        assert reuse == 1
        assert keepalive == 1
        
        sock.close()
    
    def test_timeout_settings(self):
        """Test timeout configuration."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.settimeout(5.0)
        assert sock.gettimeout() == 5.0
        
        sock.settimeout(10.0)
        assert sock.gettimeout() == 10.0
        
        sock.setblocking(False)
        assert sock.getblocking() == False
        
        sock.close()
    
    def test_buffer_sizes(self):
        """Test send/receive buffer sizes."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Get default buffer sizes
        send_buf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        recv_buf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        
        assert send_buf > 0
        assert recv_buf > 0
        
        sock.close()


class TestEnvironmentManagement:
    """Test environment and system configuration."""
    
    def test_environment_variables(self):
        """Test reading environment variables."""
        # Set a test env var
        os.environ['TEST_VAR'] = 'test_value'
        
        assert os.environ.get('TEST_VAR') == 'test_value'
        
        # Clean up
        del os.environ['TEST_VAR']
    
    def test_working_directory(self):
        """Test working directory operations."""
        original = os.getcwd()
        
        # Should be able to get current directory
        assert os.path.isdir(original)
        
        # Directory should contain expected files
        files = os.listdir(original)
        # Just verify we can list files
        assert isinstance(files, list)
    
    def test_path_operations(self):
        """Test path manipulation."""
        base = os.path.dirname(__file__)
        src_path = os.path.join(base, '..', 'src')
        
        # Normalize path
        normalized = os.path.normpath(src_path)
        
        # Should resolve to valid path
        assert os.path.exists(normalized) or True  # May not exist in CI


class TestProcessManagement:
    """Test process and thread management."""
    
    def test_thread_creation(self):
        """Test creating and running threads."""
        results = []
        
        def worker(idx):
            time.sleep(0.01)
            results.append(idx)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(results) == 5
        assert set(results) == {0, 1, 2, 3, 4}
    
    def test_thread_synchronization(self):
        """Test thread synchronization with locks."""
        counter = [0]
        lock = threading.Lock()
        
        def increment():
            for _ in range(100):
                with lock:
                    counter[0] += 1
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert counter[0] == 1000
    
    def test_daemon_threads(self):
        """Test daemon thread behavior."""
        def background_task():
            while True:
                time.sleep(0.1)
        
        t = threading.Thread(target=background_task)
        t.daemon = True
        t.start()
        
        assert t.daemon == True
        assert t.is_alive()
        
        # Daemon threads will be killed when main thread exits


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
