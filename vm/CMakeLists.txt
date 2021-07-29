cmake_minimum_required(VERSION 3.10)

project(salvm VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(concurrentqueue)

add_executable(salvm vm.cpp)

target_link_libraries(salvm PUBLIC concurrentqueue)

target_include_directories(salvm PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           "${PROJECT_SOURCE_DIR}/concurrentqueue"
                           )