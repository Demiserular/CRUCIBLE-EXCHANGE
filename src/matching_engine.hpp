#pragma once

#include <map>
#include <queue>
#include <string>
#include <memory>
#include <vector>
#include <mutex>

namespace crucible
{

    struct Order
    {
        std::string order_id;
        std::string cl_ord_id;
        std::string symbol;
        char side; // '1' = Buy, '2' = Sell
        int order_qty;
        char order_type; // '1' = Market, '2' = Limit
        double price;
        int filled_qty;
        char status; // '0' = New, '1' = Partial, '2' = Filled
        double timestamp;

        Order(const std::string &oid, const std::string &cloid, const std::string &sym,
              char s, int qty, char type, double p, double ts)
            : order_id(oid), cl_ord_id(cloid), symbol(sym), side(s),
              order_qty(qty), order_type(type), price(p), filled_qty(0),
              status('0'), timestamp(ts) {}

        int remaining_qty() const { return order_qty - filled_qty; }
        bool is_complete() const { return filled_qty >= order_qty; }
    };

    struct Match
    {
        std::string buy_order_id;
        std::string sell_order_id;
        int qty;
        double price;
        double timestamp;
    };

    // Price level holds orders at same price (FIFO queue)
    class PriceLevel
    {
    public:
        double price;
        std::queue<std::shared_ptr<Order>> orders;

        explicit PriceLevel(double p) : price(p) {}

        void add_order(std::shared_ptr<Order> order)
        {
            orders.push(order);
        }

        std::shared_ptr<Order> get_next_order()
        {
            if (orders.empty())
                return nullptr;
            auto order = orders.front();
            if (order->is_complete())
            {
                orders.pop();
                return get_next_order(); // Skip completed, get next
            }
            return order;
        }

        void remove_completed()
        {
            if (!orders.empty() && orders.front()->is_complete())
            {
                orders.pop();
            }
        }

        bool is_empty() const { return orders.empty(); }
        int size() const { return orders.size(); }
    };

    // Order book for one symbol
    class OrderBook
    {
    private:
        std::string symbol_;
        // Buy side: highest price first (descending)
        std::map<double, std::shared_ptr<PriceLevel>, std::greater<double>> buy_levels_;
        // Sell side: lowest price first (ascending)
        std::map<double, std::shared_ptr<PriceLevel>> sell_levels_;
        mutable std::mutex mutex_;

    public:
        explicit OrderBook(const std::string &symbol) : symbol_(symbol) {}

        void add_order(std::shared_ptr<Order> order);
        std::vector<Match> match_orders();

        // Getters for order book state
        std::map<double, int> get_buy_depth() const;
        std::map<double, int> get_sell_depth() const;
        double get_best_bid() const;
        double get_best_ask() const;
        double get_spread() const;
    };

    // Main matching engine
    class MatchingEngine
    {
    private:
        std::map<std::string, std::shared_ptr<OrderBook>> order_books_;
        mutable std::mutex mutex_;

    public:
        MatchingEngine() = default;

        void add_order(const std::string &symbol, std::shared_ptr<Order> order);
        std::vector<Match> match_orders(const std::string &symbol);

        std::shared_ptr<OrderBook> get_or_create_book(const std::string &symbol);
        std::shared_ptr<OrderBook> get_book(const std::string &symbol) const;
    };

} // namespace crucible
