#include "matching_engine.hpp"
#include <algorithm>
#include <cmath>
#include <chrono>

namespace crucible
{

    // OrderBook implementation
    void OrderBook::add_order(std::shared_ptr<Order> order)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        double price = order->price;

        if (order->side == '1')
        { // Buy order
            if (buy_levels_.find(price) == buy_levels_.end())
            {
                buy_levels_[price] = std::make_shared<PriceLevel>(price);
            }
            buy_levels_[price]->add_order(order);
        }
        else
        { // Sell order
            if (sell_levels_.find(price) == sell_levels_.end())
            {
                sell_levels_[price] = std::make_shared<PriceLevel>(price);
            }
            sell_levels_[price]->add_order(order);
        }
    }

    std::vector<Match> OrderBook::match_orders()
    {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<Match> matches;

        while (!buy_levels_.empty() && !sell_levels_.empty())
        {
            // Get best bid and ask
            auto &best_buy_level = buy_levels_.begin()->second;
            auto &best_sell_level = sell_levels_.begin()->second;

            // Clean up empty levels
            if (best_buy_level->is_empty())
            {
                buy_levels_.erase(buy_levels_.begin());
                continue;
            }
            if (best_sell_level->is_empty())
            {
                sell_levels_.erase(sell_levels_.begin());
                continue;
            }

            auto buy_order = best_buy_level->get_next_order();
            auto sell_order = best_sell_level->get_next_order();

            if (!buy_order || !sell_order)
                break;

            // Check if prices cross
            bool can_match = false;
            double match_price = 0.0;

            if (buy_order->order_type == '1')
            { // Market buy
                can_match = true;
                match_price = sell_order->price;
            }
            else if (sell_order->order_type == '1')
            { // Market sell
                can_match = true;
                match_price = buy_order->price;
            }
            else if (buy_order->price >= sell_order->price)
            {
                can_match = true;
                match_price = sell_order->price; // Price improvement for buyer
            }

            if (!can_match)
                break; // No more matches possible

            // Execute match
            int match_qty = std::min(buy_order->remaining_qty(), sell_order->remaining_qty());

            buy_order->filled_qty += match_qty;
            sell_order->filled_qty += match_qty;

            buy_order->status = buy_order->is_complete() ? '2' : '1';
            sell_order->status = sell_order->is_complete() ? '2' : '1';

            // Record match
            auto now = std::chrono::system_clock::now();
            auto timestamp = std::chrono::duration<double>(now.time_since_epoch()).count();

            matches.push_back({buy_order->order_id,
                               sell_order->order_id,
                               match_qty,
                               match_price,
                               timestamp});

            // Remove completed orders
            if (buy_order->is_complete())
            {
                best_buy_level->remove_completed();
            }
            if (sell_order->is_complete())
            {
                best_sell_level->remove_completed();
            }
        }

        return matches;
    }

    std::map<double, int> OrderBook::get_buy_depth() const
    {
        std::lock_guard<std::mutex> lock(mutex_);
        std::map<double, int> depth;

        for (const auto &[price, level] : buy_levels_)
        {
            depth[price] = level->size();
        }
        return depth;
    }

    std::map<double, int> OrderBook::get_sell_depth() const
    {
        std::lock_guard<std::mutex> lock(mutex_);
        std::map<double, int> depth;

        for (const auto &[price, level] : sell_levels_)
        {
            depth[price] = level->size();
        }
        return depth;
    }

    double OrderBook::get_best_bid() const
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if (buy_levels_.empty())
            return 0.0;
        return buy_levels_.begin()->first;
    }

    double OrderBook::get_best_ask() const
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if (sell_levels_.empty())
            return 0.0;
        return sell_levels_.begin()->first;
    }

    double OrderBook::get_spread() const
    {
        double bid = get_best_bid();
        double ask = get_best_ask();
        if (bid == 0.0 || ask == 0.0)
            return 0.0;
        return ask - bid;
    }

    // MatchingEngine implementation
    void MatchingEngine::add_order(const std::string &symbol, std::shared_ptr<Order> order)
    {
        auto book = get_or_create_book(symbol);
        book->add_order(order);
    }

    std::vector<Match> MatchingEngine::match_orders(const std::string &symbol)
    {
        auto book = get_book(symbol);
        if (!book)
            return {};
        return book->match_orders();
    }

    std::shared_ptr<OrderBook> MatchingEngine::get_or_create_book(const std::string &symbol)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        if (order_books_.find(symbol) == order_books_.end())
        {
            order_books_[symbol] = std::make_shared<OrderBook>(symbol);
        }
        return order_books_[symbol];
    }

    std::shared_ptr<OrderBook> MatchingEngine::get_book(const std::string &symbol) const
    {
        std::lock_guard<std::mutex> lock(mutex_);

        auto it = order_books_.find(symbol);
        if (it == order_books_.end())
            return nullptr;
        return it->second;
    }

} // namespace crucible
