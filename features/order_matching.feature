Feature: Order Matching

  Scenario: Place a buy order
    Given I am connected to the exchange
    When I send a buy order for "AAPL" with quantity 100 at price 150.00
    Then I should receive an execution report with status "New"

  Scenario: Match a buy and sell order
    Given I am connected to the exchange
    When I send a buy order for "GOOGL" with quantity 100 at price 200.00
    And I send a sell order for "GOOGL" with quantity 100 at price 200.00
    Then I should receive an execution report for the buy order with status "Filled"
    And I should receive an execution report for the sell order with status "Filled"

  Scenario: Reject invalid symbol
    Given I am connected to the exchange
    When I send a buy order for "INVALID" with quantity 100 at price 150.00
    Then I should receive an execution report with status "Rejected"

  Scenario: Cancel an order
    Given I am connected to the exchange
    When I send a buy order for "MSFT" with quantity 100 at price 180.00
    And I cancel the order
    Then I should receive an execution report with status "Canceled"

  Scenario: Execute market order
    Given I am connected to the exchange
    When I send a sell order for "TSLA" with quantity 50 at price 250.00
    And I send a market buy order for "TSLA" with quantity 50
    Then I should receive an execution report for the market order with status "Filled"

