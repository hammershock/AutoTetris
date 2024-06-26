#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // 使得std::vector和std::pair能够自动转换
#include "State.hpp"

namespace py = pybind11;

PYBIND11_MODULE(Tetris, m) {
    py::class_<State, std::shared_ptr<State>>(m, "State")
        .def(py::init<const std::vector<std::vector<int>>&>())
        .def("best1", &State::best1, py::arg("value"))
        .def("best2", &State::best2, py::arg("val1"), py::arg("val2"))
        .def("scores1", &State::scores1)
        .def("scores2", &State::scores2, py::arg("val"));
}
