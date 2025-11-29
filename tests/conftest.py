"""
pytest configuration file
Handles path setup for test imports
"""

import sys
import os

# Add src to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set environment variable to skip network tests in CI
def pytest_configure(config):
    """Configure pytest environment."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "network: marks tests requiring network (deselect with '-m \"not network\"')"
    )
