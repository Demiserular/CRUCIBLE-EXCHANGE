# Crucible - FIX Exchange System

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

A FIX 4.2 protocol exchange server with real-time WebSocket capabilities and comprehensive test automation framework. This system implements order matching, execution reporting, and session management for electronic trading.

## Features

- **FIX Protocol Implementation**: Complete FIX 4.2 message handling
- **Real-Time Dashboard**: WebSocket-enabled order book with live updates
- **Order Matching Engine**: Price-time priority matching algorithm
- **Test Automation**: BDD framework with 21 Gherkin scenarios using Behave
- **CI/CD Pipeline**: Automated testing via GitHub Actions
- **Cross-Platform**: Supports Linux, macOS, and Windows

## Architecture

```
┌─────────────────┐         FIX 4.2 Protocol        ┌──────────────────┐
│  Test Client    │ ◄─────────────────────────────► │ Exchange Server  │
│  (BDD/Behave)   │      TCP/IP Connection          │   (Order Book)   │
└─────────────────┘                                  └──────────────────┘
         │                                                     │
         │                                                     │
         ▼                                                     ▼
┌─────────────────┐                                  ┌──────────────────┐
│ Test Scenarios  │                                  │  WebSocket API   │
│ (21 Gherkin)    │                                  │  (Real-time)     │
└─────────────────┘                                  └──────────────────┘
                                                               │
                                                               ▼
                                                     ┌──────────────────┐
                                                     │   Web Dashboard  │
                                                     └──────────────────┘
```

## Technology Stack

- **Language**: Python 3.9+
- **Protocol**: FIX 4.2
- **Testing**: Behave (BDD), pytest
- **Real-time**: WebSocket, asyncio
- **CI/CD**: GitHub Actions
- **OS**: Linux, macOS, Windows

## Project Structure

```
├── features/               # BDD test scenarios
│   ├── environment.py      # Test hooks
│   ├── trading.feature     # Gherkin scenarios
│   └── steps/              # Step definitions
├── src/
│   ├── exchange_server.py  # FIX server with WebSocket
│   └── fix_engine.py       # FIX protocol utilities
├── scripts/
│   ├── run_suite.sh        # Linux test runner
│   └── run_suite.bat       # Windows test runner
├── .github/workflows/      # CI/CD pipelines
├── dashboard_realtime.html # Real-time dashboard
├── generate_orders.py      # Order generator
└── requirements.txt        # Dependencies
```

## Installation

```bash
git clone https://github.com/Demiserular/Crucible.git
cd Crucible
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Start Exchange Server

```bash
python src/exchange_server.py
```

The server will start on:
- FIX Protocol: `tcp://127.0.0.1:9878`
- WebSocket: `ws://127.0.0.1:8765`

### Generate Sample Orders

```bash
python generate_orders.py
```

### View Dashboard

Open `dashboard_realtime.html` in your browser to see the live order book.

### Run Tests

**Automated:**
```bash
./scripts/run_suite.sh  # Linux/macOS
scripts\run_suite.bat   # Windows
```

**Manual:**
```bash
behave features/
```

## FIX Protocol Support

### Supported Messages

- **Logon (35=A)**: Session establishment
- **Heartbeat (35=0)**: Keep-alive
- **Logout (35=5)**: Session termination
- **New Order Single (35=D)**: Order submission
- **Execution Report (35=8)**: Fill notifications
- **Order Cancel Request (35=F)**: Order cancellation

### Validation Rules

- Symbol validation (AAPL, GOOGL, MSFT, AMZN, TSLA)
- Price validation (positive, non-zero)
- Quantity validation (positive, non-zero)
- Checksum verification
- Message structure validation

## Testing

The test suite includes 21 scenarios covering:

- Session management
- Order lifecycle (submit, fill, cancel)
- Risk validation
- Protocol compliance
- Edge cases and error handling

Run tests with coverage:
```bash
pytest --cov=src tests/
```

## Development

### Prerequisites

- Python 3.9 or higher
- pip

### Setup Development Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Code Quality

```bash
# Linting
pylint src/
flake8 src/

# Type checking
mypy src/
```

## CI/CD

GitHub Actions workflows automatically:
- Run tests on push/PR
- Check code quality
- Generate test reports

## License

MIT License - see LICENSE file for details

## Author

**Shubham Chauhan**

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## Acknowledgments

Built with Python, asyncio, and the FIX Protocol specification.
