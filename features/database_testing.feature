Feature: Database Testing
  As an SDET, I need to verify database operations work correctly
  including data persistence, integrity constraints, and query performance.

  Background:
    Given a test database connection is established

  Scenario: Save and retrieve an order
    When I save an order with:
      | order_id   | TEST001  |
      | symbol     | AAPL     |
      | side       | Buy      |
      | order_qty  | 100      |
      | price      | 150.00   |
      | status     | New      |
    Then I should be able to retrieve the order by id "TEST001"
    And the retrieved order should have symbol "AAPL"

  Scenario: Save and retrieve an execution
    When I save an execution with:
      | exec_id    | EXEC001  |
      | order_id   | TEST001  |
      | symbol     | AAPL     |
      | side       | Buy      |
      | last_qty   | 100      |
      | last_px    | 150.00   |
    Then I should be able to retrieve executions for order "TEST001"

  Scenario: Query orders by status
    Given multiple test orders exist in the database
    When I query orders with status "New"
    Then I should receive a non-empty list of orders

  Scenario: Query orders by symbol
    Given multiple test orders exist in the database
    When I query orders for symbol "AAPL"
    Then I should receive orders only for symbol "AAPL"

  Scenario: Verify order count statistics
    Given multiple test orders exist in the database
    When I query the total order count
    Then the count should be greater than 0

  Scenario: Database handles concurrent writes
    When I save 10 orders concurrently
    Then all 10 orders should be persisted successfully
