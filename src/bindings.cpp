#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "matching_engine.hpp"

namespace py = pybind11;
using namespace crucible;

PYBIND11_MODULE(crucible_engine, m)
{
    m.doc() = "High-performance C++ matching engine for Crucible FIX Exchange";

    // Order struct
    py::class_<Order, std::shared_ptr<Order>>(m, "Order")
        .def(py::init<const std::string &, const std::string &, const std::string &,
                      char, int, char, double, double>(),
             py::arg("order_id"), py::arg("cl_ord_id"), py::arg("symbol"),
             py::arg("side"), py::arg("order_qty"), py::arg("order_type"),
             py::arg("price"), py::arg("timestamp"))
        .def_readwrite("order_id", &Order::order_id)
        .def_readwrite("cl_ord_id", &Order::cl_ord_id)
        .def_readwrite("symbol", &Order::symbol)
        .def_readwrite("side", &Order::side)
        .def_readwrite("order_qty", &Order::order_qty)
        .def_readwrite("order_type", &Order::order_type)
        .def_readwrite("price", &Order::price)
        .def_readwrite("filled_qty", &Order::filled_qty)
        .def_readwrite("status", &Order::status)
        .def_readwrite("timestamp", &Order::timestamp)
        .def("remaining_qty", &Order::remaining_qty)
        .def("is_complete", &Order::is_complete);

    // Match struct
    py::class_<Match>(m, "Match")
        .def_readonly("buy_order_id", &Match::buy_order_id)
        .def_readonly("sell_order_id", &Match::sell_order_id)
        .def_readonly("qty", &Match::qty)
        .def_readonly("price", &Match::price)
        .def_readonly("timestamp", &Match::timestamp);

    // OrderBook class
    py::class_<OrderBook, std::shared_ptr<OrderBook>>(m, "OrderBook")
        .def(py::init<const std::string &>(), py::arg("symbol"))
        .def("add_order", &OrderBook::add_order)
        .def("match_orders", &OrderBook::match_orders)
        .def("get_buy_depth", &OrderBook::get_buy_depth)
        .def("get_sell_depth", &OrderBook::get_sell_depth)
        .def("get_best_bid", &OrderBook::get_best_bid)
        .def("get_best_ask", &OrderBook::get_best_ask)
        .def("get_spread", &OrderBook::get_spread);

    // MatchingEngine class
    py::class_<MatchingEngine>(m, "MatchingEngine")
        .def(py::init<>())
        .def("add_order", &MatchingEngine::add_order)
        .def("match_orders", &MatchingEngine::match_orders)
        .def("get_or_create_book", &MatchingEngine::get_or_create_book)
        .def("get_book", &MatchingEngine::get_book);
}
