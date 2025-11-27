# Crucible FIX Exchange

[![CI](https://github.com/Demiserular/Crucible/actions/workflows/ci.yml/badge.svg)](https://github.com/Demiserular/Crucible/actions/workflows/ci.yml)

A high-performance FIX Protocol 4.2 exchange simulator featuring a C++ matching engine, real-time WebSocket updates, and a REST API for manual trading.

## Overview

Crucible is a financial exchange simulator designed to handle electronic trading via the industry-standard FIX 4.2 protocol. It implements a price-time priority matching algorithm for limit orders and provides real-time data streams through WebSockets. The system includes an optional high-performance C++ matching engine that can be built to significantly improve throughput and latency.

## Key Features

- **FIX Protocol 4.2 Compliance**: Supports standard messages for order management (New Order, Cancel, Execution Report).
- **Price-Time Priority Matching**: Employs a fair and deterministic matching algorithm.
- **Dual Implementation**: Includes both a clear, easy-to-understand Python matching engine and a high-performance C++ version.
- **Real-time Data Feeds**: Pushes order book changes and trade executions via WebSockets.
- **REST API**: Allows for manual order submission and interaction with the exchange.
- **SQLite Persistence**: Stores all orders and executions for auditing and recovery.
- **Live Trading Dashboard**: A minimal web-based UI to visualize market activity and place trades manually.

## Technology Stack

- **Backend**: Python 3, `asyncio`
- **Matching Engine**: C++17 (optional, via `pybind11`) or Python
- **API**: REST (Flask), WebSocket
- **Database**: SQLite
- **Testing**: Behave (for BDD), Pytest
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Python 3.8+
- `build-essential`, `cmake` (for building the C++ engine on Linux)
- Visual Studio Build Tools (for building the C++ engine on Windows)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Demiserular/Crucible.git
    cd Crucible
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Exchange

The start script launches the FIX exchange, the WebSocket server, and the REST API server.

-   **Windows**:
    ```cmd
    start.bat
    ```
-   **macOS/Linux**:
    ```bash
    chmod +x start.sh
    ./start.sh
    ```

The system is now running. You can view logs for each service in the `logs/` directory.

## Usage

### Trading Dashboard

1.  Open `dashboard_minimal.html` in a web browser.
2.  The dashboard connects to the WebSocket server for real-time updates.
3.  Submit `BUY` or `SELL` orders using the form.
4.  Watch the order book and recent executions update in real-time.

### APIs

-   **REST API**: `http://127.0.0.1:5000` for submitting orders.
-   **WebSocket**: `ws://127.0.0.1:8765` for live data feeds.
-   **FIX Protocol**: `127.0.0.1:9878` for programmatic trading.

## High-Performance C++ Engine

For significantly higher throughput and lower latency, you can build and enable the C++ matching engine. For detailed instructions, please see [**BUILD_CPP.md**](BUILD_CPP.md).

## Development

### Running Tests

The project uses `behave` for feature-level BDD tests and `pytest` for unit tests.

```bash
# Run all tests
pytest
behave
```

### Code Structure

-   `src/`: Core source code.
    -   `matching_engine.cpp/.hpp`: High-performance C++ matching engine.
    -   `exchange_server.py`: Main application orchestrating the FIX, WebSocket, and matching logic.
    -   `api_server.py`: REST API for manual interaction.
    -   `database.py`: Database interaction layer.
-   `features/`: BDD test scenarios.
-   `scripts/`: Utility and automation scripts.

## Contributing

Contributions are welcome. Please follow the standard fork-and-pull-request workflow.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Commit your changes (`git commit -am 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Create a new Pull Request.

## License

This project is licensed under the MIT License.