# Crucible Exchange

A FIX 4.2 protocol-based financial exchange simulator with comprehensive BDD testing framework. Built to demonstrate software testing expertise, test automation, and CI/CD practices.

## Overview

Crucible is a real-time exchange system that processes orders using the FIX (Financial Information eXchange) protocol. The project includes a complete BDD testing framework, automated CI/CD pipeline, and professional test reporting capabilities.

**Key Components:**
- FIX 4.2 protocol server for order processing
- Real-time WebSocket dashboard for live market data
- REST API for order management
- SQLite database for persistence
- Optional C++ matching engine for high performance
- Comprehensive BDD test suite with Behave

## Quick Start

### Prerequisites
- Python 3.12 or higher
- Git

### Installation

```bash
git clone https://github.com/Demiserular/CRUCIBLE-EXCHANGE.git
cd CRUCIBLE-EXCHANGE

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Windows:**
```bash
.\start_all.bat
```

**Linux/Mac:**
```bash
chmod +x start_all.sh
./start_all.sh
```

Open `dashboard_minimal.html` in your browser to access the trading dashboard.

**Server Endpoints:**
- Exchange Server (FIX): 127.0.0.1:9878
- WebSocket: ws://127.0.0.1:8765
- REST API: http://127.0.0.1:5000

## Testing

### Running BDD Tests

```bash
# Run all tests
behave

# Run specific feature
behave features/order_matching.feature

# Generate Allure report
behave -f allure_behave.formatter:AllureFormatter -o allure-results
```

### Test Scenarios

The test suite includes five comprehensive scenarios:

1. **Place a buy order** - Validates basic order placement via FIX protocol
2. **Match buy and sell orders** - Tests the order matching engine
3. **Reject invalid symbol** - Verifies input validation
4. **Cancel an order** - Tests order cancellation workflow
5. **Execute market order** - Validates market order execution

### Test Coverage

- FIX protocol message construction and parsing
- Order placement and validation logic
- Order matching engine functionality
- Order cancellation flow
- Market vs. limit order handling
- Database persistence

## Test Reporting

Generate professional test reports using Allure:

**Windows:**
```bash
scripts\generate_report.bat
```

**Linux/Mac:**
```bash
./scripts/generate_report.sh
```

Reports include test execution history, step-by-step breakdowns, failure analysis, and trend tracking.

## CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:
- Runs BDD tests on every push and pull request
- Executes code quality checks (pylint, flake8)
- Generates Allure test reports
- Deploys reports to GitHub Pages

View the workflow configuration in `.github/workflows/test.yml`

## Project Structure

```
Crucible/
├── .github/workflows/     # CI/CD pipeline configuration
├── features/              # BDD test scenarios and step definitions
│   ├── environment.py     # Test environment setup
│   ├── order_matching.feature
│   └── steps/
├── src/                   # Application source code
│   ├── exchange_server.py # FIX protocol server
│   ├── api_server.py      # REST API server
│   ├── fix_engine.py      # FIX message handling
│   ├── database_sqlite.py # Database layer
│   └── matching_engine.cpp # Optional C++ matching engine
├── scripts/               # Utility scripts
├── tests/                 # Test documentation
├── dashboard_minimal.html # Web-based trading dashboard
└── requirements.txt       # Python dependencies
```

## Technology Stack

**Application:**
- Python 3.12
- FIX 4.2 Protocol
- WebSocket for real-time updates
- Flask for REST API
- SQLite for data persistence
- C++ for optional high-performance matching

**Testing & Quality:**
- Behave (BDD framework)
- Allure (test reporting)
- Pytest (unit testing)
- Pylint, Flake8, MyPy (static analysis)

**DevOps:**
- GitHub Actions (CI/CD)
- Git (version control)

## Documentation

- [Testing Guide](tests/README.md) - Comprehensive guide for running and writing tests
- [API Documentation](docs/README.md) - REST API reference
- [FIX Protocol Guide](docs/FIX_PROTOCOL.md) - FIX message specifications

## Troubleshooting

**Tests hang or timeout:**
```bash
# Ensure servers are running
.\start_all.bat

# Check if ports are available
netstat -ano | findstr :9878
```

**Connection refused errors:**
```bash
# Start servers and wait for initialization
.\start_all.bat
timeout 5  # Wait 5 seconds
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Run tests to ensure everything works (`behave`)
4. Commit your changes (`git commit -m 'Add YourFeature'`)
5. Push to your branch (`git push origin feature/YourFeature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Demiserular**
- GitHub: [@Demiserular](https://github.com/Demiserular)

## Skills Demonstrated

This project demonstrates proficiency in:
- Behavior-Driven Development (BDD) with Python
- Test automation framework development
- CI/CD pipeline configuration
- Protocol-level testing (FIX 4.2)
- End-to-end system testing
- Database integration testing
- Multi-threaded application testing
- Technical documentation
- DevOps practices

## Acknowledgments

Built as a portfolio project to demonstrate SDET (Software Development Engineer in Test) capabilities including test automation, BDD methodologies, and CI/CD practices.
