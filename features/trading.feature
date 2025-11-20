Feature: FIX Exchange Trading Conformance
  As a trading system
  I want to validate FIX protocol compliance
  So that I can ensure proper order routing and execution

  Background:
    Given the exchange server is running
    And I am connected to the exchange

  # ========================================
  # Session Layer Tests
  # ========================================

  Scenario: Successful logon to exchange
    When I send a Logon message with heartbeat interval 30
    Then I should receive a Logon acknowledgment
    And the session should be established

  Scenario: Heartbeat mechanism maintains session
    Given I am logged into the exchange
    When I send a Heartbeat message
    Then I should receive a Heartbeat response

  Scenario: Graceful logout from exchange
    Given I am logged into the exchange
    When I send a Logout message
    Then I should receive a Logout acknowledgment
    And the session should be terminated

  # ========================================
  # Order Management - Market Orders
  # ========================================

  Scenario: Submit market buy order
    Given I am logged into the exchange
    When I submit a market buy order for 100 shares of "AAPL"
    Then I should receive an execution report with status "New"
    And the order should be in the order book

  Scenario: Submit market sell order
    Given I am logged into the exchange
    When I submit a market sell order for 50 shares of "GOOGL"
    Then I should receive an execution report with status "New"
    And the order should be in the order book

  # ========================================
  # Order Management - Limit Orders
  # ========================================

  Scenario: Submit limit buy order
    Given I am logged into the exchange
    When I submit a limit buy order for 100 shares of "MSFT" at price 350.00
    Then I should receive an execution report with status "New"
    And the order should be in the order book

  Scenario: Submit limit sell order
    Given I am logged into the exchange
    When I submit a limit sell order for 75 shares of "AMZN" at price 180.00
    Then I should receive an execution report with status "New"
    And the order should be in the order book

  # ========================================
  # Order Matching and Fills
  # ========================================

  Scenario: Full fill on matching orders
    Given I am logged into the exchange
    When I submit a limit buy order for 100 shares of "TSLA" at price 250.00
    And I submit a limit sell order for 100 shares of "TSLA" at price 250.00
    Then both orders should receive execution reports with status "Filled"
    And the fill quantity should be 100 shares
    And the fill price should be 250.00

  Scenario: Partial fill on matching orders
    Given I am logged into the exchange
    When I submit a limit buy order for 100 shares of "AAPL" at price 180.00
    And I submit a limit sell order for 50 shares of "AAPL" at price 180.00
    Then the sell order should receive an execution report with status "Filled"
    And the buy order should receive an execution report with status "Partially Filled"
    And the buy order should have 50 shares remaining

  Scenario: Market order matches with limit order
    Given I am logged into the exchange
    When I submit a limit sell order for 100 shares of "GOOGL" at price 150.00
    And I submit a market buy order for 100 shares of "GOOGL"
    Then both orders should receive execution reports with status "Filled"
    And the fill price should be 150.00

  # ========================================
  # Order Cancellation
  # ========================================

  Scenario: Cancel an open order
    Given I am logged into the exchange
    And I have submitted a limit buy order for 100 shares of "MSFT" at price 350.00
    When I send a cancel request for that order
    Then I should receive an execution report with status "Canceled"
    And the order should be removed from the order book

  Scenario: Cancel request for non-existent order
    Given I am logged into the exchange
    When I send a cancel request for order "INVALID_ORDER_123"
    Then I should receive a cancel reject message
    And the reject reason should be "Order not found"

  # ========================================
  # Validation & Risk Tests - Price
  # ========================================

  Scenario: Reject order with negative price
    Given I am logged into the exchange
    When I submit a limit buy order for 100 shares of "AAPL" at price -10.00
    Then I should receive an execution report with status "Rejected"
    And the rejection reason should contain "Invalid price"

  Scenario: Reject order with zero price
    Given I am logged into the exchange
    When I submit a limit buy order for 50 shares of "GOOGL" at price 0.00
    Then I should receive an execution report with status "Rejected"
    And the rejection reason should contain "Invalid price"

  # ========================================
  # Validation & Risk Tests - Symbol
  # ========================================

  Scenario: Reject order with invalid symbol
    Given I am logged into the exchange
    When I submit a market buy order for 100 shares of "INVALID"
    Then I should receive an execution report with status "Rejected"
    And the rejection reason should contain "Invalid symbol"

  # ========================================
  # Validation & Risk Tests - Quantity
  # ========================================

  Scenario: Reject order with negative quantity
    Given I am logged into the exchange
    When I submit a market buy order for -50 shares of "AAPL"
    Then I should receive an execution report with status "Rejected"
    And the rejection reason should contain "Invalid quantity"

  Scenario: Reject order with zero quantity
    Given I am logged into the exchange
    When I submit a limit sell order for 0 shares of "MSFT" at price 350.00
    Then I should receive an execution report with status "Rejected"
    And the rejection reason should contain "Invalid quantity"

  # ========================================
  # Protocol Compliance Tests
  # ========================================

  Scenario: Reject message with invalid checksum
    Given I am logged into the exchange
    When I send a FIX message with an incorrect checksum
    Then the message should be rejected
    And no execution report should be received

  Scenario: Handle message with missing required fields
    Given I am logged into the exchange
    When I send a New Order message missing the symbol field
    Then the message should be rejected
    And no execution report should be received

  # ========================================
  # Edge Cases
  # ========================================

  Scenario: Multiple orders for same symbol
    Given I am logged into the exchange
    When I submit 5 limit buy orders for "AAPL" at different prices
    Then all orders should be acknowledged
    And all orders should be in the order book

  Scenario: Rapid order submission
    Given I am logged into the exchange
    When I rapidly submit 10 orders within 1 second
    Then all orders should be processed
    And all orders should receive execution reports
