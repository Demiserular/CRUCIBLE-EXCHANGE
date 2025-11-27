# Testing Guide

## Overview
This project uses Behavior-Driven Development (BDD) with Python's `behave` framework to test the Crucible Exchange system.

## Quick Start

### Running Tests Locally

```bash
# Run all tests
behave

# Run specific feature
behave features/order_matching.feature

# Run with specific tags
behave --tags=@smoke

# Run with Allure reporting
behave -f allure_behave.formatter:AllureFormatter -o allure-results
```

### Generating Test Reports

**Windows:**
```bash
scripts\generate_report.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/generate_report.sh
./scripts/generate_report.sh
```

## Test Scenarios

### Current Test Coverage

1. **Place a buy order** - Verifies basic order placement
2. **Match a buy and sell order** - Tests order matching engine
3. **Reject invalid symbol** - Validates symbol validation
4. **Cancel an order** - Tests order cancellation flow
5. **Execute market order** - Tests market order execution

### Test Environment

Tests run against either:
- **Test Server** (default): Isolated instance on port 9879 with `test_crucible.db`
- **Live Server**: Production instance on port 9878 with `crucible.db` (use `run_live_tests.py`)

## CI/CD Pipeline

### GitHub Actions

The project includes automated testing via GitHub Actions:
- Runs on every push and pull request
- Executes all BDD tests
- Generates Allure reports
- Runs code quality checks (pylint, flake8)
- Publishes reports to GitHub Pages

### Viewing CI/CD Results

1. Go to the **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. View test results and download artifacts

## Allure Reporting

### Features
- ✅ Test execution history
- ✅ Step-by-step test breakdown
- ✅ Failure screenshots and logs
- ✅ Trend analysis
- ✅ Test categorization

### Installing Allure

**Windows (Scoop):**
```bash
scoop install allure
```

**macOS (Homebrew):**
```bash
brew install allure
```

**Linux:**
Download from [Allure releases](https://github.com/allure-framework/allure2/releases)

## Test Structure

```
features/
├── environment.py          # Test setup/teardown
├── order_matching.feature  # Gherkin scenarios
└── steps/
    └── order_steps.py      # Step definitions
```

## Writing New Tests

### 1. Add Gherkin Scenario

Edit `features/order_matching.feature`:

```gherkin
Scenario: Your test name
  Given I am connected to the exchange
  When I send a buy order for "AAPL" with quantity 100 at price 150.00
  Then I should receive an execution report with status "New"
```

### 2. Implement Step Definitions

If needed, add steps in `features/steps/order_steps.py`:

```python
@when('I do something')
def step_impl(context):
    # Your implementation
    pass
```

### 3. Run and Verify

```bash
behave features/order_matching.feature
```

## Troubleshooting

### Tests Hang
- Ensure Exchange Server is running: `.\start_all.bat`
- Check port availability: `netstat -ano | findstr :9878`

### Connection Refused
- Start the servers: `.\start_all.bat`
- Wait 5 seconds for initialization

### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment: `venv\Scripts\activate`

## Best Practices

1. **Keep scenarios focused** - One scenario per test case
2. **Use descriptive names** - Clear scenario titles
3. **Clean test data** - Tests should be independent
4. **Use tags** - Organize tests with `@smoke`, `@regression`, etc.
5. **Document steps** - Add docstrings to step definitions

## Code Quality

### Running Linters

```bash
# Pylint
pylint src

# Flake8
flake8 src

# MyPy (type checking)
mypy src
```

## Contributing

When adding new tests:
1. Write the Gherkin scenario first
2. Implement step definitions
3. Run tests locally
4. Ensure CI/CD passes
5. Update this documentation if needed
