cmake_minimum_required(VERSION 3.10)

project(salvm VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(concurrentqueue)
add_subdirectory(prestate)
add_subdirectory(loader)
add_subdirectory(vm)

add_executable(salvm main.cpp)

target_link_libraries(salvm PUBLIC concurrentqueue)
target_link_libraries(salvm PUBLIC loader)
target_link_libraries(salvm PUBLIC vm)

target_include_directories(salvm PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           "${PROJECT_SOURCE_DIR}/concurrentqueue"
                           "${PROJECT_SOURCE_DIR}/loader"
                           "${PROJECT_SOURCE_DIR}/vm"
                           )