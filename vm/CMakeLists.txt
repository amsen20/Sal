cmake_minimum_required(VERSION 3.10)

# set the project name and version
project(salvm VERSION 0.1.0)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# add the executable
add_executable(salvm vm.cpp)

# add the binary tree to the search path for include files
# so that we will find TutorialConfig.h
target_include_directories(salvm PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           )