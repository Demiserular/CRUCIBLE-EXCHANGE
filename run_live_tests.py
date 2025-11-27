
import os
import sys
from behave.__main__ import main as behave_main

# Set environment variable to tell environment.py to use live server
os.environ['USE_LIVE_SERVER'] = 'true'

if __name__ == '__main__':
    sys.exit(behave_main(sys.argv[1:]))
