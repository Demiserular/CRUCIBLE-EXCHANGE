Feature: REST API Testing
  As an SDET, I need to verify the REST API endpoints work correctly
  for order submission, order book retrieval, and execution queries.

  Background:
    Given the API server is running on port 5000

  Scenario: Submit a valid buy order via API
    When I submit a POST request to "/api/submit_order" with:
      | symbol    | AAPL  |
      | side      | Buy   |
      | order_qty | 100   |
      | order_type| Limit |
      | price     | 150.00|
    Then the response status code should be 200
    And the response should contain "order_id"
    And the response should contain "status"

  Scenario: Submit a valid sell order via API
    When I submit a POST request to "/api/submit_order" with:
      | symbol    | GOOGL |
      | side      | Sell  |
      | order_qty | 50    |
      | order_type| Limit |
      | price     | 175.00|
    Then the response status code should be 200
    And the response should contain "order_id"

  Scenario: Get order book snapshot
    When I submit a GET request to "/api/orderbook"
    Then the response status code should be 200
    And the response should contain "buy_orders"
    And the response should contain "sell_orders"

  Scenario: Get recent executions
    When I submit a GET request to "/api/executions"
    Then the response status code should be 200
    And the response should be a list

  Scenario: Get exchange statistics
    When I submit a GET request to "/api/statistics"
    Then the response status code should be 200
    And the response should contain "total_orders"
    And the response should contain "total_executions"

  Scenario: Submit order with missing required field
    When I submit a POST request to "/api/submit_order" with:
      | symbol    | AAPL  |
      | side      | Buy   |
    Then the response status code should be 400
    And the response should contain "error"

  Scenario: Health check endpoint
    When I submit a GET request to "/api/health"
    Then the response status code should be 200
    And the response should contain "status"
