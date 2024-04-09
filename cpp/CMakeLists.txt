cmake_minimum_required(VERSION 3.5)
project(Tetris)

set(CMAKE_CXX_STANDARD 17) # 使用C++17标准

# 查找pybind11库
find_package(pybind11 REQUIRED)

pybind11_add_module(Tetris Tetris.cpp State.cpp Piece.cpp main.cpp)

# 如果你的项目使用了特定的include目录，使用include_directories指令指定
include_directories(${PROJECT_SOURCE_DIR})

# 设置编译器优化标志
if(MSVC)
    # 对于MSVC编译器，使用/O2标志进行最大程度的优化
    target_compile_options(Tetris PRIVATE /O2)
else()
    # 对于GCC或Clang编译器，使用-O3进行优化，同时启用一些特定的性能优化选项
    target_compile_options(Tetris PRIVATE -O3 -funroll-loops -mavx2 -mbmi -mbmi2 -mlzcnt -mpopcnt)
endif()
